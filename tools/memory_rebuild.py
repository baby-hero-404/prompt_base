#!/usr/bin/env python3
"""Rebuild the derived index (.ai-memory/memory.db) from the git-tracked
markdown source of truth (docs/ai/adr/, docs/ai/archive/). The DB is
disposable by design (`make memory-rebuild`, REQ-005): this truncates it and
re-embeds every markdown file from scratch, so a fresh clone (which has the
markdown but not the gitignored DB) restores full recall with one command.
Running it twice against unchanged markdown produces an identical row set.
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import memory_engine as me  # noqa: E402


def _title_from_markdown(text: str) -> str:
    for line in text.splitlines():
        line = line.strip()
        if line.startswith("# "):
            return line[2:].strip()
    return "untitled"


def rebuild(root: str) -> int:
    conn = me.init_db(root)  # ensure schema exists even on a fresh clone

    conn.execute("DELETE FROM memory")
    conn.execute("DELETE FROM memory_fts")
    if me._load_vec_extension(conn):
        conn.execute("DELETE FROM memory_vec")
    conn.commit()

    count = 0
    for kind, directory in (("adr", me.adr_dir(root)), ("summary", me.archive_dir(root))):
        for path in sorted(Path(directory).glob("*.md")):
            text = path.read_text(encoding="utf-8")
            title = _title_from_markdown(text)
            source_path = str(path.relative_to(root))
            row_id = me.upsert(conn, root, kind, title, text, source_path)
            if row_id is not None:
                count += 1
    return count


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".", help="Project directory to rebuild (default: cwd)")
    args = parser.parse_args()

    root = me.resolve_project_root(args.root)
    count = rebuild(root)
    print(f"memory_rebuild: re-embedded {count} markdown source(s) into {me.memory_db_path(root)}")


if __name__ == "__main__":
    main()
