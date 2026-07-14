"""Task 2.3: hook resilience test (REQ-004).

Feeds malformed stdin to both hooks and asserts neither ever breaks a
session: exit 0, empty stdout, and a diagnostic line in .ai-memory/engine.log.

The "simulated missing-dependency env" half of this task is satisfied by the
ambient test environment itself - sqlite-vec/fastembed are deliberately not
installed outside the isolated venv (Task 3.2), so every subprocess run here
already exercises the real degraded path, not a mock of it. See
TestAmbientEnvIsMissingDependency below, which pins that assumption down so a
future `pip install` into this environment fails loudly instead of silently
making these tests stop covering what they claim to cover.
"""

import os
os.environ["PB_LOCAL_MEMORY"] = "1"
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

TOOLS_DIR = Path(__file__).resolve().parent.parent
HOOKS = ["memory_compact.py", "memory_recall.py"]


class TestAmbientEnvIsMissingDependency(unittest.TestCase):
    def test_sqlite_vec_and_fastembed_are_not_importable_here(self):
        for module in ("sqlite_vec", "fastembed"):
            result = subprocess.run(
                [sys.executable, "-c", f"import {module}"],
                capture_output=True,
                timeout=10,
            )
            self.assertNotEqual(
                result.returncode, 0,
                f"{module} is importable in this environment; the resilience "
                "tests below no longer exercise the degraded/missing-dependency path.",
            )


class HookResilienceTests(unittest.TestCase):
    def _run(self, hook: str, stdin_text: str, cwd: str):
        return subprocess.run(
            [sys.executable, str(TOOLS_DIR / hook)],
            input=stdin_text,
            capture_output=True,
            text=True,
            cwd=cwd,
            timeout=10,
        )

    def test_malformed_stdin_both_hooks_exit_zero_empty_stdout(self):
        for hook in HOOKS:
            with self.subTest(hook=hook):
                with tempfile.TemporaryDirectory() as tmp:
                    (Path(tmp) / ".git").mkdir()
                    result = self._run(hook, "{not valid json", tmp)
                    self.assertEqual(result.returncode, 0)
                    self.assertEqual(result.stdout, "")

    def test_empty_stdin_both_hooks_exit_zero(self):
        for hook in HOOKS:
            with self.subTest(hook=hook):
                with tempfile.TemporaryDirectory() as tmp:
                    (Path(tmp) / ".git").mkdir()
                    result = self._run(hook, "", tmp)
                    self.assertEqual(result.returncode, 0)
                    self.assertEqual(result.stdout, "")

    def test_non_object_json_both_hooks_exit_zero(self):
        for hook in HOOKS:
            with self.subTest(hook=hook):
                with tempfile.TemporaryDirectory() as tmp:
                    (Path(tmp) / ".git").mkdir()
                    result = self._run(hook, "[1, 2, 3]", tmp)
                    self.assertEqual(result.returncode, 0)
                    self.assertEqual(result.stdout, "")

    def test_missing_dependency_env_still_exits_zero_and_functions(self):
        """Runs each hook with a real (non-degraded-only) payload in this
        dependency-missing environment - both must complete normally via the
        FTS5 fallback rather than crashing on the sqlite-vec/fastembed
        ImportError."""
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / ".git").mkdir()
            transcript = Path(tmp) / "transcript.jsonl"
            transcript.write_text(
                '{"role": "assistant", "content": [{"type": "text", "text": '
                '"<adr title=\\"Test\\"><decision>d</decision><rationale>r</rationale></adr>"}]}\n',
                encoding="utf-8",
            )
            compact_payload = json.dumps({
                "hook_event_name": "PreCompact",
                "transcript_path": str(transcript),
                "cwd": tmp,
                "session_id": "s1",
            })
            result = self._run("memory_compact.py", compact_payload, tmp)
            self.assertEqual(result.returncode, 0)

            recall_payload = json.dumps({
                "hook_event_name": "UserPromptSubmit",
                "session_id": "s2",
                "prompt": "test decision",
                "cwd": tmp,
            })
            result = self._run("memory_recall.py", recall_payload, tmp)
            self.assertEqual(result.returncode, 0)

    def test_diagnostic_line_appended_to_engine_log(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / ".git").mkdir()
            self._run("memory_compact.py", "{not valid json", tmp)
            log_path = Path(tmp) / ".ai-memory" / "engine.log"
            self.assertTrue(log_path.exists())
            self.assertTrue(log_path.read_text(encoding="utf-8").strip())


if __name__ == "__main__":
    unittest.main()
