#!/usr/bin/env python3
"""User-local list of projects whose repo content may drive automatic hooks.

Hooks that run repo-controlled content automatically (Stop gate running `make verify`,
invariant injection from docs/ai/DOMAIN.md) must not fire in a freshly cloned, unread
repo. The list lives outside any repo, so a repo cannot trust itself.

  python3 tools/pb_trust.py --add [DIR]   trust DIR (default: current directory)
  python3 tools/pb_trust.py --remove [DIR]   stop trusting DIR
  python3 tools/pb_trust.py --list
Escape hatch: PB_TRUST_ALL=1 trusts everything. Files: ~/.gemini/prompt_base_trusted.txt
and ~/.claude/prompt_base_trusted.txt (override: PB_TRUST_FILE).
"""
import argparse
import os
import sys
from pathlib import Path


def _trust_files() -> list:
    override = os.environ.get("PB_TRUST_FILE")
    if override:
        return [Path(override).expanduser()]
    claude = Path("~/.claude/prompt_base_trusted.txt").expanduser()
    gemini = Path("~/.gemini/prompt_base_trusted.txt").expanduser()
    files = []
    if gemini.parent.exists():
        files.append(gemini)
    if claude.parent.exists():
        files.append(claude)
    return files or [gemini, claude]


def trust_file() -> Path:
    caller_str = str(Path(__file__).resolve())
    if ".claude" in caller_str:
        claude = Path("~/.claude/prompt_base_trusted.txt").expanduser()
        if claude.parent.exists():
            return claude
    return _trust_files()[0]


def _entries():
    entries = set()
    for tf in _trust_files():
        try:
            for ln in tf.read_text(encoding="utf-8").splitlines():
                if ln.strip():
                    entries.add(ln.strip())
        except OSError:
            pass
    return sorted(entries)


def is_trusted(root) -> bool:
    if os.environ.get("PB_TRUST_ALL") == "1":
        return True
    resolved = Path(root).resolve()
    for entry in _entries():
        trusted = Path(entry)
        if resolved == trusted or trusted in resolved.parents:
            return True
    return False


def memory_enabled(root) -> bool:
    """Memory hooks (capture, recall) act only on projects that opted in: initialized
    with /init-memory (docs/ai exists) AND trusted by the user. PB_TRUST_ALL=1 bypasses both."""
    if os.environ.get("PB_TRUST_ALL") == "1":
        return True
    return (Path(root) / "docs" / "ai").is_dir() and is_trusted(root)


def add(root) -> Path:
    resolved = str(Path(root).resolve())
    for tf in _trust_files():
        try:
            existing = []
            if tf.exists():
                existing = [ln.strip() for ln in tf.read_text(encoding="utf-8").splitlines() if ln.strip()]
            if resolved not in existing:
                tf.parent.mkdir(parents=True, exist_ok=True)
                with open(tf, "a", encoding="utf-8") as f:
                    f.write(resolved + "\n")
        except OSError:
            pass
    return Path(resolved)


def remove(root) -> bool:
    """Drop root from the list. Returns whether it was listed."""
    resolved = str(Path(root).resolve())
    any_removed = False
    for tf in _trust_files():
        try:
            if not tf.exists():
                continue
            entries = [ln.strip() for ln in tf.read_text(encoding="utf-8").splitlines() if ln.strip()]
            if resolved in entries:
                tf.write_text("".join(e + "\n" for e in entries if e != resolved), encoding="utf-8")
                any_removed = True
        except OSError:
            pass
    return any_removed


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--add", nargs="?", const=".", metavar="DIR")
    parser.add_argument("--remove", nargs="?", const=".", metavar="DIR")
    parser.add_argument("--list", action="store_true")
    args = parser.parse_args()
    if args.add is not None:
        print(f"trusted: {add(args.add)}")
    elif args.remove is not None:
        print(("removed: " if remove(args.remove) else "not listed: ") + str(Path(args.remove).resolve()))
    elif args.list:
        print("\n".join(_entries()) or "(no trusted projects)")
    else:
        parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
