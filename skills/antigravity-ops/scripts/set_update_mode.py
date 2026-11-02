#!/usr/bin/env python3
"""Safely set the top-level Antigravity update.mode in an existing JSONC settings file."""
from __future__ import annotations
import argparse
import datetime as dt
import json
import os
import re
import stat
import tempfile
from pathlib import Path


def skip_ws_comments(s: str, i: int) -> int:
    n = len(s)
    while i < n:
        if s[i].isspace():
            i += 1
        elif s.startswith('//', i):
            j = s.find('\n', i + 2)
            return n if j < 0 else skip_ws_comments(s, j + 1)
        elif s.startswith('/*', i):
            j = s.find('*/', i + 2)
            if j < 0:
                raise ValueError('Unterminated block comment in settings file')
            i = j + 2
        else:
            break
    return i


def read_string(s: str, i: int) -> tuple[str, int]:
    if i >= len(s) or s[i] != '"':
        raise ValueError('Expected a quoted JSON object key')
    j = i + 1
    escaped = False
    while j < len(s):
        c = s[j]
        if escaped:
            escaped = False
        elif c == '\\':
            escaped = True
        elif c == '"':
            token = s[i:j + 1]
            return json.loads(token), j + 1
        j += 1
    raise ValueError('Unterminated string in settings file')


def scan_value_end(s: str, i: int) -> int:
    start = i
    obj = arr = 0
    in_string = escaped = False
    line_comment = block_comment = False
    while i < len(s):
        c = s[i]
        nxt = s[i + 1] if i + 1 < len(s) else ''
        if line_comment:
            if c == '\n': line_comment = False
            i += 1; continue
        if block_comment:
            if c == '*' and nxt == '/': block_comment = False; i += 2; continue
            i += 1; continue
        if in_string:
            if escaped: escaped = False
            elif c == '\\': escaped = True
            elif c == '"': in_string = False
            i += 1; continue
        if c == '"': in_string = True; i += 1; continue
        if c == '/' and nxt == '/': line_comment = True; i += 2; continue
        if c == '/' and nxt == '*': block_comment = True; i += 2; continue
        if c == '{': obj += 1
        elif c == '}':
            if obj == 0 and arr == 0: break
            obj -= 1
        elif c == '[': arr += 1
        elif c == ']': arr -= 1
        elif c == ',' and obj == 0 and arr == 0: break
        i += 1
    while i > start and s[i - 1].isspace(): i -= 1
    return i


def locate_top_level_key(s: str, target: str) -> tuple[int, int, int, int] | None:
    i = skip_ws_comments(s, 0)
    if i >= len(s) or s[i] != '{':
        raise ValueError('settings.json root must be an object')
    i += 1
    while True:
        i = skip_ws_comments(s, i)
        if i >= len(s):
            raise ValueError('Unexpected end of settings file')
        if s[i] == '}':
            return None
        key, after_key = read_string(s, i)
        colon = skip_ws_comments(s, after_key)
        if colon >= len(s) or s[colon] != ':':
            raise ValueError(f'Missing colon after key {key!r}')
        value_start = skip_ws_comments(s, colon + 1)
        value_end = scan_value_end(s, value_start)
        if key == target:
            return (i, after_key, value_start, value_end)
        i = skip_ws_comments(s, value_end)
        if i < len(s) and s[i] == ',':
            i += 1
        elif i < len(s) and s[i] == '}':
            return None
        else:
            raise ValueError('Expected comma or closing brace after setting value')


def top_level_has_any_key(s: str) -> bool:
    i = skip_ws_comments(s, 0)
    if i >= len(s) or s[i] != '{':
        raise ValueError('settings.json root must be an object')
    i = skip_ws_comments(s, i + 1)
    return i < len(s) and s[i] != '}'


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--settings-file', required=True, help='Existing Antigravity User/settings.json')
    ap.add_argument('--mode', choices=('default', 'manual', 'none'), default='default')
    args = ap.parse_args()
    path = Path(args.settings_file).expanduser().resolve()
    if not path.is_file():
        ap.error(f'File does not exist: {path}')
    if path.stat().st_uid != os.getuid():
        ap.error('Refusing to edit a settings file not owned by the current user')
    original = path.read_text(encoding='utf-8')
    found = locate_top_level_key(original, 'update.mode')
    replacement = json.dumps(args.mode)
    if found:
        value_start, value_end = found[2], found[3]
        updated = original[:value_start] + replacement + original[value_end:]
    else:
        root = skip_ws_comments(original, 0)
        if original[root] != '{':
            ap.error('settings.json root must be an object')
        insert_at = root + 1
        has_keys = top_level_has_any_key(original)
        prefix = '\n  ' + json.dumps('update.mode') + ': ' + replacement
        if has_keys:
            prefix += ','
        updated = original[:insert_at] + prefix + original[insert_at:]
    if updated == original:
        print(f'No change needed: {path} already has update.mode={args.mode!r}')
        return 0

    stamp = dt.datetime.now().strftime('%Y%m%d-%H%M%S')
    backup = path.with_name(path.name + '.bak.' + stamp)
    # Preserve file mode and owner (owner is already checked above).
    shutil_mode = stat.S_IMODE(path.stat().st_mode)
    backup.write_text(original, encoding='utf-8')
    os.chmod(backup, shutil_mode)
    fd, temp_name = tempfile.mkstemp(prefix=path.name + '.', suffix='.tmp', dir=str(path.parent))
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            f.write(updated)
            f.flush()
            os.fsync(f.fileno())
        os.chmod(temp_name, shutil_mode)
        os.replace(temp_name, path)
    except Exception:
        try: os.unlink(temp_name)
        except OSError: pass
        raise
    print(f'Updated: {path}')
    print(f'Backup:  {backup}')
    print(f'New setting: "update.mode": {replacement}')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
