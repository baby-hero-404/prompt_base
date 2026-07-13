import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import memory_engine as me  # noqa: E402


class ResolveProjectRootTests(unittest.TestCase):
    def test_nested_dir_walks_up_to_git_root(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / ".git").mkdir()
            nested = Path(tmp) / "server" / "pkg" / "llm"
            nested.mkdir(parents=True)
            self.assertEqual(me.resolve_project_root(str(nested)), str(Path(tmp).resolve()))

    def test_marker_file_used_when_no_git(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "ARCHITECTURE.md").write_text("# root")
            nested = Path(tmp) / "sub"
            nested.mkdir()
            self.assertEqual(me.resolve_project_root(str(nested)), str(Path(tmp).resolve()))

    def test_no_marker_falls_back_to_cwd(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(me.resolve_project_root(tmp), str(Path(tmp).resolve()))
            self.assertTrue((Path(tmp) / ".ai-memory" / "engine.log").exists())

    def test_env_override_wins(self):
        with tempfile.TemporaryDirectory() as tmp, tempfile.TemporaryDirectory() as override:
            (Path(tmp) / ".git").mkdir()
            os.environ["PB_MEMORY_ROOT"] = override
            try:
                self.assertEqual(me.resolve_project_root(tmp), str(Path(override).resolve()))
            finally:
                del os.environ["PB_MEMORY_ROOT"]


class SecretScrubbingTests(unittest.TestCase):
    def test_detects_api_key_pattern(self):
        self.assertTrue(me.contains_secret("api_key: sk-abcdefghijklmnopqrstuvwxyz123456"))

    def test_detects_aws_key(self):
        self.assertTrue(me.contains_secret("AKIA" + "A" * 16))

    def test_plain_text_is_not_flagged(self):
        self.assertFalse(me.contains_secret("We chose sqlite-vec because it needs no server process."))

    def test_upsert_skips_chunk_with_secret(self):
        with tempfile.TemporaryDirectory() as tmp:
            conn = me.init_db(tmp)
            row_id = me.upsert(conn, tmp, "adr", "leak", "password: hunter2hunter2hunter2", None)
            self.assertIsNone(row_id)
            count = conn.execute("SELECT COUNT(*) AS c FROM memory").fetchone()["c"]
            self.assertEqual(count, 0)


class UpsertQueryTests(unittest.TestCase):
    def test_dedupes_on_content_sha(self):
        with tempfile.TemporaryDirectory() as tmp:
            conn = me.init_db(tmp)
            body = "Chose sqlite-vec over Chroma for single-file simplicity."
            first = me.upsert(conn, tmp, "adr", "Use sqlite-vec", body, "docs/ai/adr/x.md")
            second = me.upsert(conn, tmp, "adr", "Use sqlite-vec", body, "docs/ai/adr/x.md")
            self.assertEqual(first, second)
            count = conn.execute("SELECT COUNT(*) AS c FROM memory").fetchone()["c"]
            self.assertEqual(count, 1)

    def test_query_degrades_to_fts5_without_vec_extension(self):
        with tempfile.TemporaryDirectory() as tmp:
            conn = me.init_db(tmp)
            me.upsert(conn, tmp, "adr", "Use sqlite-vec", "sqlite-vec is a single file extension", "docs/ai/adr/x.md")
            result = me.query(conn, tmp, "sqlite-vec single file", k=5)
            self.assertTrue(result["degraded"])
            self.assertEqual(len(result["hits"]), 1)
            self.assertEqual(result["hits"][0]["title"], "Use sqlite-vec")

    def test_query_empty_store_returns_no_hits(self):
        with tempfile.TemporaryDirectory() as tmp:
            conn = me.init_db(tmp)
            result = me.query(conn, tmp, "anything", k=5)
            self.assertEqual(result["hits"], [])

    def test_drop_row_removes_from_all_tables(self):
        with tempfile.TemporaryDirectory() as tmp:
            conn = me.init_db(tmp)
            row_id = me.upsert(conn, tmp, "adr", "Title", "some body text about the decision", "docs/ai/adr/x.md")
            me.drop_row(conn, tmp, row_id)
            self.assertIsNone(conn.execute("SELECT id FROM memory WHERE id = ?", (row_id,)).fetchone())
            self.assertIsNone(conn.execute("SELECT rowid FROM memory_fts WHERE rowid = ?", (row_id,)).fetchone())


class MetaHelperTests(unittest.TestCase):
    def test_embed_load_ms_roundtrip(self):
        with tempfile.TemporaryDirectory() as tmp:
            conn = me.init_db(tmp)
            self.assertIsNone(me.get_embed_load_ms(conn))
            me.set_embed_load_ms(conn, 1234.5)
            self.assertEqual(me.get_embed_load_ms(conn), 1234.5)

    def test_init_db_is_idempotent(self):
        with tempfile.TemporaryDirectory() as tmp:
            me.init_db(tmp)
            conn = me.init_db(tmp)
            tables = {r["name"] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
            self.assertIn("meta", tables)
            self.assertIn("memory", tables)


if __name__ == "__main__":
    unittest.main()
