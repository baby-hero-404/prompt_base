#!/usr/bin/env python3
"""Read-only report on a project's memory: shared markdown (docs/ai), the derived
index for this agent, and leftover index dirs. Never creates or deletes anything."""
import argparse
import re
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import memory_engine as me  # noqa: E402
import pb_trust  # noqa: E402


def _vec_importable() -> bool:
    try:
        import sqlite_vec  # noqa: F401
        return True
    except ImportError:
        return False


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".")
    args = parser.parse_args()

    root = me.resolve_project_root(args.root)
    root_path = Path(root)
    print(f"project root: {root}")

    trusted = pb_trust.is_trusted(root)
    print(f"trust: {'trusted (hooks active)' if trusted else 'untrusted (hooks inactive; opt in via /init-memory or python3 ~/.agents/tools/pb_trust.py --add .)'}")

    ai_dir = root_path / "docs" / "ai"
    if ai_dir.is_dir():
        parts = [name for name in ("PROFILE.md", "DOMAIN.md", "manifest.json", "adr", "archive") if (ai_dir / name).exists()]
        print(f"docs/ai: present ({', '.join(parts) or 'empty'})")
    else:
        print("docs/ai: missing (no memory in this project; opt in with /init-memory)")

    mem_dir = me.get_memory_dir(root)
    db_path = mem_dir / "memory.db"
    print(f"index dir: {mem_dir}")
    if not db_path.exists():
        print("index: no database yet")
    else:
        try:
            conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
            rows = conn.execute("SELECT kind, COUNT(*) FROM memory GROUP BY kind").fetchall()
            load_ms = conn.execute("SELECT value FROM meta WHERE key='embed_load_ms'").fetchone()
            conn.close()
            print("index rows: " + (", ".join(f"{k}: {n}" for k, n in rows) or "0"))
            semantic = _vec_importable() and load_ms is not None
            print(f"recall mode: {'semantic (vec)' if semantic else 'keyword (FTS5)'}"
                  f"{'' if load_ms is None else f', embed_load_ms={load_ms[0]}'}")
        except sqlite3.Error as exc:
            print(f"index: unreadable ({exc})")
        sentinel = mem_dir / "last_recall_session"
        if sentinel.exists():
            print("last recall: " + datetime.fromtimestamp(sentinel.stat().st_mtime).isoformat(timespec="seconds"))

    leaf = root_path.resolve().name
    sibling_name = re.compile(rf"^{re.escape(leaf)}-[0-9a-f]{{16}}$")
    siblings = sorted(p for p in mem_dir.parent.iterdir() if p.is_dir() and p != mem_dir and sibling_name.match(p.name)) if mem_dir.parent.is_dir() else []
    if siblings:
        print("other index dirs with the same project name (candidates to prune, review before deleting):")
        for p in siblings:
            print(f"  {p}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
