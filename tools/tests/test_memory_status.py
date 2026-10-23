"""M4: read-only memory status report."""

import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

TOOLS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(TOOLS))
import memory_engine as me  # noqa: E402

TOOL = TOOLS / "memory_status.py"


def run(root, tmp):
    env = {**os.environ, "PB_GLOBAL_MEMORY_DIR": str(Path(tmp) / "mem")}
    env.pop("PB_LOCAL_MEMORY", None)
    return subprocess.run([sys.executable, str(TOOL), "--root", str(root)],
                          capture_output=True, text=True, timeout=30, env=env)


def project(tmp):
    root = Path(tmp) / "work" / "app"
    (root / ".git").mkdir(parents=True)
    return root


class StatusTests(unittest.TestCase):
    def setUp(self):
        self._orig_local = os.environ.pop("PB_LOCAL_MEMORY", None)

    def tearDown(self):
        if self._orig_local is not None:
            os.environ["PB_LOCAL_MEMORY"] = self._orig_local

    def test_no_database_is_reported_not_created(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = project(tmp)
            r = run(root, tmp)
            self.assertEqual(r.returncode, 0)
            self.assertIn("no database", r.stdout.lower())
            self.assertFalse((Path(tmp) / "mem").exists())

    def test_reports_rows_by_kind(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = project(tmp)
            os.environ["PB_GLOBAL_MEMORY_DIR"] = str(Path(tmp) / "mem")
            try:
                conn = me.init_db(str(root))
                conn.execute("INSERT INTO memory(kind,title,body,content_sha,created_at) VALUES('adr','t','b','sha1','now')")
                conn.commit()
                conn.close()
            finally:
                del os.environ["PB_GLOBAL_MEMORY_DIR"]
            r = run(root, tmp)
            self.assertIn("adr: 1", r.stdout)

    def test_lists_sibling_dirs_without_deleting(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = project(tmp)
            mem = Path(tmp) / "mem"
            sibling = mem / "app-0000000000000000"
            sibling.mkdir(parents=True)
            r = run(root, tmp)
            self.assertIn(str(sibling), r.stdout)
            self.assertTrue(sibling.exists())

    def test_other_project_with_prefix_name_is_not_a_sibling(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = project(tmp)
            other = Path(tmp) / "mem" / "app-v2-0123456789abcdef"
            other.mkdir(parents=True)
            self.assertNotIn(str(other), run(root, tmp).stdout)

    def test_reports_docs_ai_state(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = project(tmp)
            self.assertIn("docs/ai: missing", run(root, tmp).stdout)
            (root / "docs" / "ai").mkdir(parents=True)
            self.assertIn("docs/ai: present", run(root, tmp).stdout)


if __name__ == "__main__":
    unittest.main()
