import json
import os
os.environ["PB_LOCAL_MEMORY"] = "1"
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import memory_engine as me  # noqa: E402
import memory_recall as mr  # noqa: E402


def _seed(root: str, title: str, body: str, source_rel: str, write_file=True):
    conn = me.init_db(root)
    if write_file:
        path = Path(root) / source_rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(body, encoding="utf-8")
    me.upsert(conn, root, "adr", title, body, source_rel if write_file else None)
    return conn


class SentinelGatingTests(unittest.TestCase):
    def test_first_prompt_is_served(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / ".git").mkdir()
            _seed(tmp, "Use sqlite-vec", "sqlite-vec avoids running a server process", "docs/ai/adr/x.md")
            payload = {"session_id": "s1", "prompt": "why did we pick sqlite-vec", "cwd": tmp}
            output = mr.recall(tmp, payload)
            self.assertIn("Use sqlite-vec", output)

    def test_second_prompt_same_session_is_noop(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / ".git").mkdir()
            _seed(tmp, "Use sqlite-vec", "sqlite-vec avoids running a server process", "docs/ai/adr/x.md")
            payload = {"session_id": "s1", "prompt": "why did we pick sqlite-vec", "cwd": tmp}
            mr.recall(tmp, payload)
            second = mr.recall(tmp, {"session_id": "s1", "prompt": "a totally different question", "cwd": tmp})
            self.assertEqual(second, "")

    def test_different_session_is_served_again(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / ".git").mkdir()
            _seed(tmp, "Use sqlite-vec", "sqlite-vec avoids running a server process", "docs/ai/adr/x.md")
            mr.recall(tmp, {"session_id": "s1", "prompt": "sqlite-vec", "cwd": tmp})
            output = mr.recall(tmp, {"session_id": "s2", "prompt": "sqlite-vec", "cwd": tmp})
            self.assertIn("Use sqlite-vec", output)

    def test_no_prompt_produces_no_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / ".git").mkdir()
            output = mr.recall(tmp, {"session_id": "s1", "prompt": None, "cwd": tmp})
            self.assertEqual(output, "")


class BudgetGatingTests(unittest.TestCase):
    def test_over_budget_never_imports_fastembed(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / ".git").mkdir()
            conn = _seed(tmp, "Use sqlite-vec", "sqlite-vec is a single file", "docs/ai/adr/x.md")
            me.set_embed_load_ms(conn, 5000)  # over the default 2000ms budget
            with mock.patch.object(me, "_get_fastembed_model") as fake_backend:
                fake_backend.side_effect = AssertionError("fastembed should not be imported over budget")
                output = mr.recall(tmp, {"session_id": "s1", "prompt": "sqlite-vec single file", "cwd": tmp})
            fake_backend.assert_not_called()
            self.assertIn("Use sqlite-vec", output)

    def test_no_recorded_load_ms_never_imports_fastembed(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / ".git").mkdir()
            _seed(tmp, "Use sqlite-vec", "sqlite-vec is a single file", "docs/ai/adr/x.md")
            with mock.patch.object(me, "_get_fastembed_model") as fake_backend:
                fake_backend.side_effect = AssertionError("fastembed should not be imported")
                mr.recall(tmp, {"session_id": "s1", "prompt": "sqlite-vec single file", "cwd": tmp})
            fake_backend.assert_not_called()


class GhostRowPruningTests(unittest.TestCase):
    def test_deleted_markdown_never_shown_and_row_removed(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / ".git").mkdir()
            conn = _seed(tmp, "Use sqlite-vec", "sqlite-vec keyword ghost test", "docs/ai/adr/x.md")
            row = conn.execute("SELECT id FROM memory WHERE title = ?", ("Use sqlite-vec",)).fetchone()
            row_id = row["id"]

            os.remove(Path(tmp) / "docs" / "ai" / "adr" / "x.md")

            output = mr.recall(tmp, {"session_id": "s1", "prompt": "sqlite-vec keyword ghost test", "cwd": tmp})
            self.assertNotIn("Use sqlite-vec", output)
            self.assertIsNone(conn.execute("SELECT id FROM memory WHERE id = ?", (row_id,)).fetchone())

    def test_next_best_backfills_after_ghost_removed(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / ".git").mkdir()
            conn = me.init_db(tmp)
            ghost_path = Path(tmp) / "docs" / "ai" / "adr" / "ghost.md"
            ghost_path.parent.mkdir(parents=True, exist_ok=True)
            ghost_path.write_text("widget rollout decision", encoding="utf-8")
            me.upsert(conn, tmp, "adr", "Ghost widget decision", "widget rollout decision", "docs/ai/adr/ghost.md")
            os.remove(ghost_path)

            survivor_path = Path(tmp) / "docs" / "ai" / "adr" / "survivor.md"
            survivor_path.write_text("widget rollout backup plan", encoding="utf-8")
            me.upsert(conn, tmp, "adr", "Survivor widget plan", "widget rollout backup plan", "docs/ai/adr/survivor.md")

            output = mr.recall(tmp, {"session_id": "s1", "prompt": "widget rollout", "cwd": tmp})
            self.assertIn("Survivor widget plan", output)
            self.assertNotIn("Ghost widget decision", output)

    def test_source_path_null_rows_exempt_from_check(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / ".git").mkdir()
            conn = me.init_db(tmp)
            me.upsert(conn, tmp, "transcript_chunk", None, "raw chunk about widget rollout", None)
            output = mr.recall(tmp, {"session_id": "s1", "prompt": "widget rollout", "cwd": tmp})
            self.assertIn("widget rollout", output)


class OutputBudgetTests(unittest.TestCase):
    def test_output_capped_and_drops_lowest_scoring(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / ".git").mkdir()
            conn = me.init_db(tmp)
            for i in range(10):
                body = f"widget rollout decision number {i} " + ("padding text " * 20)
                path_rel = f"docs/ai/adr/w{i}.md"
                path = Path(tmp) / path_rel
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(body, encoding="utf-8")
                me.upsert(conn, tmp, "adr", f"Widget decision {i}", body, path_rel)

            os.environ["PB_RECALL_K"] = "10"
            os.environ["PB_RECALL_MAX_CHARS"] = "300"
            try:
                output = mr.recall(tmp, {"session_id": "s1", "prompt": "widget rollout decision", "cwd": tmp})
            finally:
                del os.environ["PB_RECALL_K"]
                del os.environ["PB_RECALL_MAX_CHARS"]

            self.assertLessEqual(len(output), 300)
            self.assertNotEqual(output, "")

    def test_never_includes_full_body_only_truncated_summary(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / ".git").mkdir()
            long_body = "widget rollout rationale " + ("detail " * 100)
            _seed(tmp, "Widget decision", long_body, "docs/ai/adr/w.md")
            output = mr.recall(tmp, {"session_id": "s1", "prompt": "widget rollout", "cwd": tmp})
            self.assertNotIn(long_body.strip(), output)
            self.assertLess(len(output), len(long_body))


class EmptyStoreTests(unittest.TestCase):
    def test_empty_store_prints_nothing(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / ".git").mkdir()
            output = mr.recall(tmp, {"session_id": "s1", "prompt": "anything at all", "cwd": tmp})
            self.assertEqual(output, "")


class MainEntrypointTests(unittest.TestCase):
    def test_subprocess_malformed_stdin_exits_zero_with_empty_stdout(self):
        script = str(Path(__file__).resolve().parent.parent / "memory_recall.py")
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / ".git").mkdir()
            result = subprocess.run(
                [sys.executable, script],
                input="not valid json {{{",
                capture_output=True,
                text=True,
                cwd=tmp,
                timeout=10,
            )
            self.assertEqual(result.returncode, 0)
            self.assertEqual(result.stdout, "")

    def test_subprocess_first_prompt_prints_pointer(self):
        script = str(Path(__file__).resolve().parent.parent / "memory_recall.py")
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / ".git").mkdir()
            _seed(tmp, "Use sqlite-vec", "sqlite-vec is a single-file vector store", "docs/ai/adr/x.md")
            payload = json.dumps({
                "hook_event_name": "UserPromptSubmit",
                "session_id": "s1",
                "prompt": "sqlite-vec single-file vector store",
                "cwd": tmp,
            })
            result = subprocess.run(
                [sys.executable, script],
                input=payload,
                capture_output=True,
                text=True,
                cwd=tmp,
                timeout=10,
            )
            self.assertEqual(result.returncode, 0)
            self.assertIn("Use sqlite-vec", result.stdout)


if __name__ == "__main__":
    unittest.main()
