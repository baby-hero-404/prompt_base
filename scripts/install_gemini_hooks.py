#!/usr/bin/env python3
"""Idempotently merge this repo's tracked Antigravity/Gemini hooks (hooks.gemini.json)
into ~/.gemini/config/hooks.json.
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
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return {}


def merge_hooks(dest: dict, source: dict) -> dict:
    """Merge source hook groups into dest hook groups, deduping handlers by command."""
    for group_name, events in source.items():
        dest_group = dest.setdefault(group_name, {})
        for event, handlers in events.items():
            dest_handlers = dest_group.setdefault(event, [])
            existing_cmds = {h.get("command") for h in dest_handlers if isinstance(h, dict)}
            for handler in handlers:
                if isinstance(handler, dict) and handler.get("command") not in existing_cmds:
                    dest_handlers.append(handler)
                    existing_cmds.add(handler.get("command"))
    return dest


def install(source_path: Path, dest_path: Path) -> dict:
    source = _load_json(source_path)
    dest = _load_json(dest_path)
    merged = merge_hooks(dest, source)
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    dest_path.write_text(json.dumps(merged, indent=2) + "\n", encoding="utf-8")
    return merged


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", default="hooks.gemini.json", help="Path to tracked source hooks")
    parser.add_argument("--dest", default="~/.gemini/config/hooks.json", help="Path to destination hooks.json")
    args = parser.parse_args()

    source_path = Path(args.source).expanduser().resolve()
    dest_path = Path(args.dest).expanduser().resolve()

    if not source_path.exists():
        print(f"install_gemini_hooks: source not found at {source_path}", file=sys.stderr)
        sys.exit(1)

    install(source_path, dest_path)
    print(f"install_gemini_hooks: merged hooks from {source_path} into {dest_path}")


if __name__ == "__main__":
    main()
