#!/usr/bin/env python3
"""Create an empty, schema-correct .ai-memory/memory.db for a project
(`make memory-init`). Mainly useful right after a fresh clone, before any
hook has run - memory_compact.py/memory_recall.py also call init_db()
themselves on demand, so this is a convenience, not a prerequisite."""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import memory_engine as me  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".", help="Project directory to initialize (default: cwd)")
    args = parser.parse_args()

    root = me.resolve_project_root(args.root)
    me.init_db(root)
    print(f"memory_init: created {me.memory_db_path(root)}")


if __name__ == "__main__":
    main()
