#!/usr/bin/env python3
"""Idempotently merge this repo's tracked hook registrations (settings.json)
into an installed Claude Code / Gemini settings.json.

Never overwrites the destination file outright: existing hook entries (and
any other top-level keys a user has configured) are preserved. New hook
entries are appended, deduped by (event, matcher, type, command) so running
the install twice leaves exactly one copy of each.
"""
import argparse
import json
import sys
from pathlib import Path


def _load_json(path: Path) -> dict:
    if not path.exists():
        return {}
    text = path.read_text(encoding="utf-8").strip()
    if not text:
        return {}
    return json.loads(text)


def _find_or_create_group(groups: list, matcher: str) -> dict:
    for group in groups:
        if group.get("matcher", "") == matcher:
            return group
    group = {"matcher": matcher, "hooks": []}
    groups.append(group)
    return group


def merge_settings(dest: dict, source: dict) -> dict:
    """Merge source["hooks"] into dest["hooks"] in place, deduped by
    (matcher, type, command). All other dest keys are left untouched."""
    source_hooks = source.get("hooks", {})
    if not source_hooks:
        return dest

    dest_hooks = dest.setdefault("hooks", {})
    for event, groups in source_hooks.items():
        dest_groups = dest_hooks.setdefault(event, [])
        for group in groups:
            matcher = group.get("matcher", "")
            dest_group = _find_or_create_group(dest_groups, matcher)
            existing = {(h.get("type"), h.get("command")) for h in dest_group["hooks"]}
            for hook in group.get("hooks", []):
                key = (hook.get("type"), hook.get("command"))
                if key not in existing:
                    dest_group["hooks"].append(hook)
                    existing.add(key)
    return dest


def install(source_path: Path, dest_path: Path) -> dict:
    source = _load_json(source_path)
    dest = _load_json(dest_path)
    merged = merge_settings(dest, source)
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    dest_path.write_text(json.dumps(merged, indent=2) + "\n", encoding="utf-8")
    return merged


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True, help="Path to the tracked source settings.json")
    parser.add_argument("--dest", required=True, help="Path to the installed settings.json to merge hooks into")
    args = parser.parse_args()

    source_path = Path(args.source).expanduser().resolve()
    dest_path = Path(args.dest).expanduser().resolve()

    if not source_path.exists():
        print(f"install_settings: source settings not found at {source_path}", file=sys.stderr)
        sys.exit(1)

    install(source_path, dest_path)
    print(f"install_settings: merged hooks from {source_path} into {dest_path}")


if __name__ == "__main__":
    main()
