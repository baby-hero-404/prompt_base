"""memory_adr.py: hook-free ADR recording for agents without PreCompact (Gemini, Codex)."""
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

TOOL = Path(__file__).resolve().parent.parent / "memory_adr.py"
sys.path.insert(0, str(TOOL.parent))


def run_tool(root, *args, stdin=None, trusted=True, memory_dir=None):
    env = {k: v for k, v in os.environ.items() if not k.startswith("PB_")}
    env["PB_GLOBAL_MEMORY_DIR"] = memory_dir
    if trusted:
        env["PB_TRUST_ALL"] = "1"
    else:
        env["PB_TRUST_FILE"] = str(Path(memory_dir) / "none.txt")
    return subprocess.run(
        [sys.executable, str(TOOL), "--root", str(root), *args],
        input=stdin, capture_output=True, text=True, timeout=60, env=env,
    )


class MemoryAdrTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name) / "proj"
        (self.root / ".git").mkdir(parents=True)
        (self.root / "docs" / "ai").mkdir(parents=True)
        self.mem = str(Path(self._tmp.name) / "mem")
        self.addCleanup(self._tmp.cleanup)

    def adr_files(self):
        return list((self.root / "docs" / "ai" / "adr").glob("*.md"))

    def test_flags_write_markdown_adr(self):
        r = run_tool(self.root, "--title", "Use sqlite", "--decision", "Pick sqlite", "--rationale", "No server needed", memory_dir=self.mem)
        self.assertEqual(r.returncode, 0, r.stderr)
        files = self.adr_files()
        self.assertEqual(len(files), 1)
        text = files[0].read_text()
        self.assertIn("# Use sqlite", text)
        self.assertIn("Pick sqlite", text)
        self.assertIn("No server needed", text)
        self.assertIn("docs/ai/adr/", r.stdout)

    def test_json_stdin_handles_quotes_and_newlines(self):
        payload = json.dumps({"title": 'Quote "x"', "decision": "line1\nline2", "rationale": "it's fine"})
        r = run_tool(self.root, "--json", stdin=payload, memory_dir=self.mem)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("line1\nline2", self.adr_files()[0].read_text())

    def test_recorded_adr_is_recalled_by_other_agents(self):
        run_tool(self.root, "--title", "Use grpc", "--decision", "Expose grpc", "--rationale", "Typed contracts", memory_dir=self.mem)
        env = {k: v for k, v in os.environ.items() if not k.startswith("PB_")}
        env.update(PB_GLOBAL_MEMORY_DIR=self.mem, PB_TRUST_ALL="1")
        recall = TOOL.parent / "memory_recall.py"
        payload = json.dumps({"session_id": "s1", "prompt": "how do we expose grpc", "cwd": str(self.root)})
        r = subprocess.run([sys.executable, str(recall)], input=payload, capture_output=True, text=True, timeout=60, env=env)
        self.assertIn("Use grpc", r.stdout)

    def test_same_decision_twice_creates_one_file(self):
        args = ("--title", "Same", "--decision", "d", "--rationale", "r")
        run_tool(self.root, *args, memory_dir=self.mem)
        r = run_tool(self.root, *args, memory_dir=self.mem)
        self.assertEqual(r.returncode, 0)
        self.assertEqual(len(self.adr_files()), 1)

    def test_refused_when_memory_not_enabled(self):
        r = run_tool(self.root, "--title", "t", "--decision", "d", "--rationale", "r", trusted=False, memory_dir=self.mem)
        self.assertEqual(r.returncode, 1)
        self.assertIn("/init-memory", r.stderr)
        self.assertEqual(self.adr_files(), [])

    def test_refused_without_docs_ai_even_if_trusted_by_env(self):
        bare = Path(self._tmp.name) / "bare"
        (bare / ".git").mkdir(parents=True)
        env = {k: v for k, v in os.environ.items() if not k.startswith("PB_")}
        env.update(PB_GLOBAL_MEMORY_DIR=self.mem, PB_TRUST_FILE=str(Path(self.mem) / "t.txt"))
        Path(self.mem).mkdir(parents=True, exist_ok=True)
        Path(env["PB_TRUST_FILE"]).write_text(str(bare.resolve()) + "\n")
        r = subprocess.run(
            [sys.executable, str(TOOL), "--root", str(bare), "--title", "t", "--decision", "d", "--rationale", "r"],
            capture_output=True, text=True, timeout=60, env=env,
        )
        self.assertEqual(r.returncode, 1)
        self.assertFalse((bare / "docs").exists())  # never creates docs/ai itself

    def test_secret_is_never_written(self):
        r = run_tool(self.root, "--title", "Keys", "--decision", "use sk-" + "a" * 30, "--rationale", "r", memory_dir=self.mem)
        self.assertEqual(r.returncode, 1)
        self.assertIn("secret", r.stderr)
        self.assertEqual(self.adr_files(), [])

    def test_missing_field_is_rejected(self):
        r = run_tool(self.root, "--title", "only title", memory_dir=self.mem)
        self.assertEqual(r.returncode, 1)
        self.assertIn("required", r.stderr)

    def test_malformed_json_is_rejected_without_traceback(self):
        r = run_tool(self.root, "--json", stdin="not json", memory_dir=self.mem)
        self.assertEqual(r.returncode, 1)
        self.assertNotIn("Traceback", r.stderr)


if __name__ == "__main__":
    unittest.main()
