import os
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import memory_engine as me  # noqa: E402
import memory_rebuild as mr  # noqa: E402

TOOLS_DIR = Path(__file__).resolve().parent.parent


def _rows(root: str):
    conn = sqlite3.connect(me.memory_db_path(root))
    conn.row_factory = sqlite3.Row
    return [dict(r) for r in conn.execute("SELECT kind, title, source_path FROM memory ORDER BY id")]


class MemoryInitTests(unittest.TestCase):
    def test_creates_empty_schema_correct_db(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / ".git").mkdir()
            result = subprocess.run(
                [sys.executable, str(TOOLS_DIR / "memory_init.py"), "--root", tmp],
                capture_output=True, text=True, timeout=10,
            )
            self.assertEqual(result.returncode, 0)
            db_path = Path(me.memory_db_path(tmp))
            self.assertTrue(db_path.exists())
            conn = sqlite3.connect(str(db_path))
            tables = {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
            self.assertIn("meta", tables)
            self.assertIn("memory", tables)
            self.assertEqual(_rows(tmp), [])


class MemoryRebuildTests(unittest.TestCase):
    def _seed_markdown(self, tmp: str):
        adr_dir = Path(tmp) / "docs" / "ai" / "adr"
        adr_dir.mkdir(parents=True)
        (adr_dir / "2026-01-01-000000-use-sqlite-vec.md").write_text(
            "# Use sqlite-vec\n\n## Decision\n\nSingle-file store.\n\n## Rationale\n\nNo server.\n",
            encoding="utf-8",
        )
        archive_dir = Path(tmp) / "docs" / "ai" / "archive"
        archive_dir.mkdir(parents=True)
        (archive_dir / "2026-01-01-000000-rollup.md").write_text(
            "# Session rollup\n\nSome preview text.\n", encoding="utf-8"
        )

    def test_rebuild_from_fresh_clone_with_no_db(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / ".git").mkdir()
            self._seed_markdown(tmp)
            self.assertFalse(Path(me.memory_db_path(tmp)).exists())
            count = mr.rebuild(tmp)
            self.assertEqual(count, 2)
            rows = _rows(tmp)
            self.assertEqual({r["kind"] for r in rows}, {"adr", "summary"})

    def test_rebuild_twice_is_idempotent(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / ".git").mkdir()
            self._seed_markdown(tmp)
            mr.rebuild(tmp)
            first = _rows(tmp)
            mr.rebuild(tmp)
            second = _rows(tmp)
            self.assertEqual(first, second)

    def test_rebuild_drops_rows_for_deleted_markdown(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / ".git").mkdir()
            self._seed_markdown(tmp)
            mr.rebuild(tmp)
            self.assertEqual(len(_rows(tmp)), 2)

            os.remove(Path(tmp) / "docs" / "ai" / "adr" / "2026-01-01-000000-use-sqlite-vec.md")
            mr.rebuild(tmp)
            rows = _rows(tmp)
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["kind"], "summary")

    def test_rebuild_picks_up_edited_markdown(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / ".git").mkdir()
            self._seed_markdown(tmp)
            mr.rebuild(tmp)
            adr_path = Path(tmp) / "docs" / "ai" / "adr" / "2026-01-01-000000-use-sqlite-vec.md"
            adr_path.write_text(adr_path.read_text(encoding="utf-8") + "\nEdited addendum.\n", encoding="utf-8")
            mr.rebuild(tmp)
            rows = _rows(tmp)
            adr_row = next(r for r in rows if r["kind"] == "adr")
            conn = sqlite3.connect(me.memory_db_path(tmp))
            conn.row_factory = sqlite3.Row
            body = conn.execute("SELECT body FROM memory WHERE title = ?", (adr_row["title"],)).fetchone()["body"]
            self.assertIn("Edited addendum.", body)

    def test_rebuild_empty_project_yields_zero_and_no_crash(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / ".git").mkdir()
            count = mr.rebuild(tmp)
            self.assertEqual(count, 0)

    def test_subprocess_rebuild_exits_zero(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / ".git").mkdir()
            self._seed_markdown(tmp)
            result = subprocess.run(
                [sys.executable, str(TOOLS_DIR / "memory_rebuild.py"), "--root", tmp],
                capture_output=True, text=True, timeout=10,
            )
            self.assertEqual(result.returncode, 0)
            self.assertIn("re-embedded 2", result.stdout)


if __name__ == "__main__":
    unittest.main()
