#!/usr/bin/env python3
"""Read-only Linux Antigravity environment inspector. Standard library only."""
from __future__ import annotations
import argparse
import ctypes.util
import json
import os
import platform
import re
import shlex
import shutil
import subprocess
from pathlib import Path
from typing import Any


def run(cmd: list[str], timeout: int = 4) -> str:
    try:
        p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                           text=True, timeout=timeout, check=False)
        return p.stdout.strip() if p.returncode == 0 else ""
    except (OSError, subprocess.TimeoutExpired):
        return ""


def command_succeeds(cmd: list[str], timeout: int = 3) -> bool:
    try:
        p = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                           timeout=timeout, check=False)
        return p.returncode == 0
    except (OSError, subprocess.TimeoutExpired):
        return False


def read_os_release() -> dict[str, str]:
    result: dict[str, str] = {}
    path = Path('/etc/os-release')
    if path.exists():
        for line in path.read_text(errors='replace').splitlines():
            if '=' not in line or line.startswith('#'):
                continue
            k, v = line.split('=', 1)
            result[k] = v.strip().strip('"').strip("'")
    return result


def version_tuple(value: str) -> tuple[int, ...]:
    return tuple(int(x) for x in re.findall(r'\d+', value))


def get_glibc() -> str | None:
    try:
        v = os.confstr('CS_GNU_LIBC_VERSION')
        if v:
            return v.replace('glibc ', '')
    except (AttributeError, OSError, ValueError):
        pass
    text = run(['ldd', '--version'])
    m = re.search(r'\b(\d+\.\d+(?:\.\d+)?)\b', text)
    return m.group(1) if m else None


def get_glibcxx() -> str | None:
    candidates: list[str] = []
    ldconfig = run(['ldconfig', '-p'])
    for line in ldconfig.splitlines():
        if 'libstdc++.so.6' in line:
            m = re.search(r'=>\s*(\S+)', line)
            if m:
                candidates.append(m.group(1))
    found = ctypes.util.find_library('stdc++')
    if found and os.path.isabs(found):
        candidates.append(found)
    for lib in candidates:
        text = run(['strings', lib], timeout=8)
        versions = re.findall(r'GLIBCXX_(\d+(?:\.\d+)+)', text)
        if versions:
            return max(versions, key=version_tuple)
    return None


def parse_desktop_entry(path: Path) -> dict[str, str] | None:
    try:
        text = path.read_text(errors='replace')
    except OSError:
        return None
    if 'antigravity' not in (path.name + '\n' + text).lower():
        return None
    result: dict[str, str] = {'desktop_file': str(path)}
    for line in text.splitlines():
        if line.startswith('Name='):
            result['name'] = line[5:].strip()
        elif line.startswith('Exec='):
            result['exec'] = line[5:].strip()
        elif line.startswith('TryExec='):
            result['try_exec'] = line[8:].strip()
    return result


def find_desktop_entries() -> list[dict[str, str]]:
    dirs = [Path.home() / '.local/share/applications', Path('/usr/local/share/applications'), Path('/usr/share/applications')]
    out: list[dict[str, str]] = []
    for d in dirs:
        if d.is_dir():
            for p in d.glob('*.desktop'):
                item = parse_desktop_entry(p)
                if item:
                    out.append(item)
    return out


def process_info() -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    proc = Path('/proc')
    if not proc.is_dir():
        return out
    for d in proc.iterdir():
        if not d.name.isdigit():
            continue
        try:
            raw = (d / 'cmdline').read_bytes()
            args = [x.decode(errors='replace') for x in raw.split(b'\0') if x]
            joined = ' '.join(args)
            exe = os.readlink(d / 'exe') if (d / 'exe').exists() else None
            # Match the actual executable/argv[0], not arbitrary arguments or cwd names.
            names = [Path(x).name.lower() for x in (exe or '', args[0] if args else '') if x]
            if not any('antigravity' in name for name in names):
                continue
            # Do not mistake the separate Antigravity CLI client for the desktop IDE.
            if any(name == 'agy' or name.startswith('agy-') for name in names):
                continue
            out.append({'pid': int(d.name), 'exe': exe, 'cmdline': joined[:600]})
        except (OSError, PermissionError):
            continue
    return out


def package_owner(path: str | None) -> dict[str, str] | None:
    if not path:
        return None
    real = os.path.realpath(path)
    checks = [
        (['dpkg-query', '-S', real], 'dpkg'),
        (['rpm', '-qf', real], 'rpm'),
        (['pacman', '-Qo', real], 'pacman'),
    ]
    for cmd, manager in checks:
        output = run(cmd)
        if output:
            return {'manager': manager, 'owner': output.splitlines()[0]}
    return None


def detect_container_install() -> dict[str, Any] | None:
    if os.environ.get('FLATPAK_ID'):
        return {'type': 'flatpak', 'app_id': os.environ['FLATPAK_ID']}
    if os.environ.get('SNAP'):
        return {'type': 'snap', 'app_name': os.environ.get('SNAP_NAME', 'unknown'), 'mount': os.environ['SNAP']}
    if os.environ.get('APPIMAGE'):
        return {'type': 'appimage', 'path': os.environ['APPIMAGE']}
    return None


def known_settings_candidates(user_data_dirs: list[str]) -> list[str]:
    candidates: list[Path] = []
    for d in user_data_dirs:
        candidates.append(Path(d) / 'User/settings.json')
    config_home = Path(os.environ.get('XDG_CONFIG_HOME', str(Path.home() / '.config')))
    for product in ('Antigravity', 'antigravity', 'Antigravity IDE', 'Google Antigravity'):
        candidates.append(config_home / product / 'User/settings.json')
    # Deduplicate and only report existing regular files.
    result = []
    seen = set()
    for p in candidates:
        try:
            rp = str(p.expanduser().resolve())
            if rp not in seen and Path(rp).is_file():
                seen.add(rp)
                result.append(rp)
        except OSError:
            pass
    return result


def read_update_mode(settings_file: str) -> str | None:
    try:
        text = Path(settings_file).read_text(errors='replace')
    except OSError:
        return None
    m = re.search(r'(?m)^\s*"update\.mode"\s*:\s*"([^"]+)"', text)
    return m.group(1) if m else None


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--json', action='store_true', help='emit JSON only')
    args = ap.parse_args()

    if platform.system() != 'Linux':
        print(json.dumps({'supported': False, 'reason': 'This skill run targets Linux.', 'system': platform.system()}, indent=2))
        return 2

    osr = read_os_release()
    arch = platform.machine().lower()
    mapped_arch = 'x64' if arch in ('x86_64', 'amd64') else 'arm64' if arch in ('aarch64', 'arm64') else 'unsupported'
    glibc = get_glibc()
    glibcxx = get_glibcxx()
    procs = process_info()
    desktops = find_desktop_entries()
    binary_candidates: list[str] = []
    for cmd in ('antigravity', 'Antigravity', 'antigravity-ide'):
        found = shutil.which(cmd)
        if found:
            binary_candidates.append(os.path.realpath(found))
    for p in procs:
        if p.get('exe') and not p['exe'].endswith(' (deleted)'):
            binary_candidates.append(p['exe'])
    desktop_install_hints: list[dict[str, str]] = []
    for entry in desktops:
        exec_line = entry.get('try_exec') or entry.get('exec', '')
        if not exec_line:
            continue
        try:
            tokens = shlex.split(exec_line)
            # Desktop entries often wrap Flatpak/Snap apps; preserve app identity.
            if len(tokens) >= 3 and tokens[0] == 'flatpak' and tokens[1] == 'run':
                desktop_install_hints.append({'type': 'flatpak', 'app_id': tokens[2], 'desktop_file': entry['desktop_file']})
                continue
            if len(tokens) >= 3 and tokens[0] == 'snap' and tokens[1] == 'run':
                desktop_install_hints.append({'type': 'snap', 'app_name': tokens[2], 'desktop_file': entry['desktop_file']})
                continue
            first_index = 1 if tokens and tokens[0] == 'env' else 0
            while first_index < len(tokens) and '=' in tokens[first_index]:
                first_index += 1
            if first_index < len(tokens):
                first = tokens[first_index]
                if 'antigravity' in Path(first).name.lower():
                    resolved = first if first.startswith('/') else shutil.which(first)
                    if resolved and Path(resolved).exists():
                        binary_candidates.append(os.path.realpath(resolved))
        except (ValueError, OSError):
            pass
    binary_candidates = list(dict.fromkeys(binary_candidates))

    package_managers = [x for x in ('apt-get', 'dnf', 'yum', 'zypper', 'pacman', 'flatpak', 'snap') if shutil.which(x)]
    flatpak_antigravity = []
    if shutil.which('flatpak'):
        for line in run(['flatpak', 'list', '--app', '--columns=application,name']).splitlines():
            if 'antigravity' in line.lower():
                flatpak_antigravity.append(line.strip())
    snap_antigravity = []
    if shutil.which('snap'):
        for line in run(['snap', 'list']).splitlines():
            if 'antigravity' in line.lower():
                snap_antigravity.append(line.strip())

    owner = package_owner(binary_candidates[0]) if binary_candidates else None
    container = detect_container_install()
    if container:
        install = container
    elif desktop_install_hints:
        install = desktop_install_hints[0]
    elif flatpak_antigravity:
        install = {'type': 'flatpak', 'detected_package': flatpak_antigravity[0]}
    elif snap_antigravity:
        install = {'type': 'snap', 'detected_package': snap_antigravity[0]}
    elif owner:
        install = {'type': 'system-package', **owner}
    elif binary_candidates and any('appimage' in p.lower() for p in binary_candidates):
        install = {'type': 'appimage', 'path': binary_candidates[0]}
    elif binary_candidates:
        install = {'type': 'unmanaged-binary-or-tarball', 'path': binary_candidates[0], 'confidence': 'medium; confirm from desktop launcher and installation directory'}
    else:
        install = {'type': 'not-detected', 'path': None}

    # Determine user-data dirs from process/desktop args without searching the whole home directory.
    user_data_dirs: list[str] = []
    for p in procs:
        try:
            raw = (Path('/proc') / str(p['pid']) / 'cmdline').read_bytes().split(b'\0')
            tokens = [x.decode(errors='replace') for x in raw if x]
            for i, token in enumerate(tokens):
                if token.startswith('--user-data-dir='):
                    user_data_dirs.append(token.split('=', 1)[1])
                elif token == '--user-data-dir' and i + 1 < len(tokens):
                    user_data_dirs.append(tokens[i + 1])
        except OSError:
            pass
    settings = known_settings_candidates(user_data_dirs)
    mode = {p: read_update_mode(p) for p in settings}

    legacy_repo_markers = []
    for root in (Path('/etc/apt/sources.list.d'), Path('/etc/yum.repos.d'), Path('/etc/dnf/repos.d')):
        if root.is_dir():
            for f in root.glob('*'):
                if f.is_file():
                    try:
                        content = f.read_text(errors='replace').lower()
                        if 'antigravity' in content:
                            legacy_repo_markers.append(str(f))
                    except OSError:
                        pass
    if owner and owner.get('manager') in ('dpkg', 'rpm') and legacy_repo_markers:
        install['legacy_antigravity_repo_config_found'] = legacy_repo_markers

    report = {
        'supported': True,
        'os': {'id': osr.get('ID'), 'id_like': osr.get('ID_LIKE'), 'name': osr.get('PRETTY_NAME'), 'version_id': osr.get('VERSION_ID')},
        'kernel': platform.release(),
        'architecture': {'raw': arch, 'google_linux_asset': mapped_arch},
        'libc': {'glibc': glibc, 'glibcxx': glibcxx,
                 'meets_google_minimum': bool(glibc and glibcxx and version_tuple(glibc) >= (2, 28) and version_tuple(glibcxx) >= (3, 4, 25))},
        'desktop_session': {'type': os.environ.get('XDG_SESSION_TYPE'), 'desktop': os.environ.get('XDG_CURRENT_DESKTOP'), 'wayland_display': bool(os.environ.get('WAYLAND_DISPLAY')), 'display': bool(os.environ.get('DISPLAY'))},
        'systemd_user_available': bool(shutil.which('systemctl') and command_succeeds(['systemctl', '--user', 'show-environment'], timeout=3)),
        'package_managers_available': package_managers,
        'flatpak_antigravity_apps': flatpak_antigravity,
        'snap_antigravity_packages': snap_antigravity,
        'install': install,
        'binary_candidates': binary_candidates,
        'running_processes': procs,
        'desktop_entries': desktops,
        'settings_files': [{'path': p, 'update_mode': mode[p]} for p in settings],
        'legacy_repository_config_files': legacy_repo_markers,
        'notes': [
            'Read-only inspection; no files or system settings were changed.',
            'A missing update.mode override normally means the application default applies.',
            'Google documents background download followed by a Restart to Update prompt for standalone IDE.'
        ]
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
