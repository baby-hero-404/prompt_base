---
name: antigravity-ops
description: "Use when installing, setting up, checking versions, or safely auto-updating Google Antigravity (standalone IDE & agy CLI) on Linux. Detects distro, architecture, libc, and the actual install method (tarball, dpkg/rpm/pacman, Snap, Flatpak, AppImage) before changing anything, and flags that Google's old APT/RPM repositories for Antigravity 1.x are historical and unsupported for current releases. Triggers on: antigravity, agy, update antigravity, setup antigravity, upgrade antigravity."
allowed-tools: Read, Write, Edit, Glob, Grep, Bash
---

# Antigravity Ops (Environment-Aware Setup & Auto-Update)

## Purpose

Adapt installation, update configuration, and desktop integration to the machine running Antigravity. Never assume Ubuntu, x86_64, a legacy APT/RPM package, a settings path, or systemd. Diagnose first; make only supported changes.

## Important Product Behavior and Limits

- **Standalone distribution**: Current Linux standalone distribution is a `.tar.gz` archive: download, extract, and run `Antigravity`. Minimums: glibc >= 2.28 and GLIBCXX >= 3.4.25.
- **In-App auto-updater on Linux**: Google's standalone Linux builds hardcode `"updateUrl": "https://example.com"` in `product.json`. OTA background updates do not function on Linux standalone tarballs; upgrades require downloading the official archive and syncing files into the install directory.
- **Legacy repositories are frozen on the 1.x line**: `https://us-central1-apt.pkg.dev/projects/antigravity-auto-updater-dev` (Debian/Ubuntu APT) last served `1.23.2` and is not publishing the current `2.x` line — confirmed by comparing `apt-cache policy antigravity` against the releases API below, which already lists `2.6.0`. Never recommend `apt-get upgrade antigravity` as the path to a current release; it will not get you past `1.23.2`.
- **No unattended force-restart**: No documented Linux CLI switch exists for silent restart. Never kill or restart a running IDE process externally.
- **Desktop & PATH integration**: Standalone tarballs do not auto-register desktop entries or PATH. Configuring `~/.local/share/applications/antigravity.desktop`, `antigravity.png` icon, and `~/.local/bin/antigravity` symlink are mandatory setup steps.

### How to verify these claims yourself (don't take them on faith)
- `grep -o '"updateUrl": "[^"]*"' <install-dir>/resources/app/product.json` — confirms the stub `updateUrl`.
- `curl -s https://antigravity-ide-auto-updater-974169037036.us-central1.run.app/releases` — returns `[{"version":"2.6.0","execution_id":"..."}, ...]`; this is the actual current-release feed (undocumented, no official SLA — re-check it still responds before relying on it).
- `apt-cache policy antigravity` (Debian/Ubuntu) — compare its `Candidate:` version against the releases feed above to confirm the APT repo is behind.

Official refs: https://antigravity.google/releases | https://antigravity-ide-auto-updater-974169037036.us-central1.run.app/releases (undocumented API, discovered by observing the app's own update check — treat as best-effort, not a stable contract)

## Workflow: Always Inspect First

1. Run `python3 skills/antigravity-ops/scripts/inspect_environment.py --json`.
2. Read the report. If Antigravity is not detected, ask the user for its launch path before searching disk.
3. Identify install type and follow the decision tree below.
4. Before any write, state target file/setting. Back up files. Do not use `sudo` for per-user settings/launchers.
5. Verify effective settings, desktop launcher, and PATH resolution after configuration.

## Decision Tree

### A. Official Standalone Tarball / Unpacked Binary (Recommended Path)

#### 1. Architecture & Libc Validation
- Check arch (`x86_64` -> Linux x64; `aarch64`/`arm64` -> Linux ARM64).
- Verify minimums: glibc >= 2.28 and GLIBCXX >= 3.4.25. If below minimum, halt and explain.

#### 2. User Settings Configuration (`update.mode`)
- Locate existing `settings.json` from running process or XDG config (`~/.config/Antigravity IDE/User/settings.json`).
- If identified: `python3 skills/antigravity-ops/scripts/set_update_mode.py --settings-file '<path>' --mode default`.

#### 3. Terminal PATH Integration
- Ensure binary alias symlink inside install dir: `ln -sf antigravity-ide <install-dir>/antigravity`.
- Create user symlink: `mkdir -p ~/.local/bin && ln -sf "<install-dir>/bin/antigravity-ide" ~/.local/bin/antigravity`.
- Verify `~/.local/bin` in `$PATH`; propose adding `export PATH="$HOME/.local/bin:$PATH"` to `~/.bashrc` if missing.

#### 4. Desktop Launcher & Icon Integration
<!-- contract:ignore -->
- **Icon**: Verify `/usr/share/pixmaps/antigravity.png` or `~/.local/share/icons/hicolor/512x512/apps/antigravity.png`. If missing, copy from `<install-dir>/resources/app/resources/linux/code.png`.
<!-- /contract:ignore -->
- **Desktop Entry**: Write/repair `~/.local/share/applications/antigravity.desktop`:
  ```ini
  [Desktop Entry]
  Name=Antigravity
  Comment=Antigravity IDE
  Exec=<install-dir>/bin/antigravity-ide %F
  Icon=antigravity
  Type=Application
  StartupNotify=true
  StartupWMClass=Antigravity
  Categories=Development;IDE;TextEditor;
  MimeType=application/x-antigravity-workspace;text/plain;
  Actions=new-empty-window;
  Keywords=vscode;antigravity;code;editor;
  [Desktop Action new-empty-window]
  Name=New Empty Window
  Exec=<install-dir>/bin/antigravity-ide --new-window %F
  Icon=antigravity
  ```
- Run `update-desktop-database ~/.local/share/applications/ 2>/dev/null || true`.

#### 5. Tarball In-Place Upgrade Flow
1. **Check version**: Query `https://antigravity-ide-auto-updater-974169037036.us-central1.run.app/releases` for latest version & `execution_id`.
2. **Download archive**: `https://edgedl.me.gvt1.com/edgedl/release2/j0qc3/antigravity/stable/<version>-<execution_id>/linux-x64/Antigravity%20IDE.tar.gz` (currently `linux-x64` only; `linux-arm64` 404s on this CDN as of this writing — re-check before assuming it exists).
3. **Stage & Extract**: Unpack into `/tmp/antigravity-stage/`.
4. **Confirm the app is fully closed**: `pgrep -f antigravity` must return nothing. Never `rsync` into a running app's install directory — ask the user to quit Antigravity first instead of force-killing it.
5. **Sync**: `rsync -av --exclude=chrome-sandbox "/tmp/antigravity-stage/Antigravity IDE/" "<install-dir>/"` (preserve existing `chrome-sandbox` SUID).
6. **Restart**: Instruct user to relaunch Antigravity IDE to load the upgraded binaries.

### B. Package-Managed Installation (dpkg/rpm/pacman)
- Query package owner. If legacy APT/RPM repo (`us-central1-apt.pkg.dev`) is found, warn user and recommend tarball migration. Never run `apt-get upgrade antigravity` against historical repos.

### C. Snap or Flatpak
- Treat package manager as update authority (`snap refresh`, `flatpak update`). Do not alter remotes silently.

### D. AppImage or Custom Wrapper
- Report path and ask how it was installed. Do not overwrite or configure down loaders without user guidance.

### E. macOS / Windows (Out of Scope for Linux Scripts)
- Point user to https://antigravity.google/releases and use the in-app Settings UI.

## Environment-Specific Checks & Restart Policy

- Branch on `/etc/os-release`, CPU arch, libc, package ownership, running processes, and XDG desktop entries.
- Unattended restart is unsupported on Linux: separate check/download/sync from application restart. Never force-kill running IDE sessions.

## Automation Scripts

- `skills/antigravity-ops/scripts/inspect_environment.py` — read-only Linux inspector (stdlib only).
- `skills/antigravity-ops/scripts/set_update_mode.py` — edits `update.mode` with timestamped backup.
- Rollback: restore `.bak.<timestamp>` file beside `settings.json`.

## Completion Report

Report:
1. detected distro / architecture / libc,
2. detected install type and path,
3. settings file and resulting `update.mode`,
4. desktop launcher & icon integration status,
5. terminal PATH integration status,
6. current version vs latest available upstream version,
7. native background update status,
8. restart instructions and backup verification.
