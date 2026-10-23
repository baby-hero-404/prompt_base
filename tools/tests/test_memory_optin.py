"""Memory is opt-in per project: hooks write nothing unless the user ran /init-memory
(docs/ai exists) AND trusted the project (pb_trust list outside the repo)."""

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

TOOLS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(TOOLS))
import pb_trust  # noqa: E402

ADR = ('{"role": "assistant", "content": [{"type": "text", "text": '
       '"<adr title=\\"T\\"><decision>d</decision><rationale>r</rationale></adr>"}]}\n')


def env_for(tmp, trust_all=False):
    env = {k: v for k, v in os.environ.items()
           if k not in ("PB_TRUST_ALL", "PB_TRUST_FILE", "PB_LOCAL_MEMORY", "PB_GLOBAL_MEMORY_DIR", "PB_MEMORY_ROOT")}
    env["PB_GLOBAL_MEMORY_DIR"] = str(Path(tmp) / "mem")
    env["PB_TRUST_FILE"] = str(Path(tmp) / "trusted.txt")
    if trust_all:
        env["PB_TRUST_ALL"] = "1"
    return env


def make_project(tmp, ai_dir=False, trusted=False):
    root = Path(tmp) / "work" / "app"
    (root / ".git").mkdir(parents=True)
    if ai_dir:
        (root / "docs" / "ai").mkdir(parents=True)
    if trusted:
        (Path(tmp) / "trusted.txt").write_text(str(root.resolve()) + "\n")
    (Path(tmp) / "transcript.jsonl").write_text(ADR)
    return root


def run_compact(root, tmp, **kw):
    payload = json.dumps({"hook_event_name": "PreCompact", "cwd": str(root), "session_id": "s1",
                          "transcript_path": str(Path(tmp) / "transcript.jsonl")})
    return subprocess.run([sys.executable, str(TOOLS / "memory_compact.py")], input=payload,
                          capture_output=True, text=True, timeout=30, env=env_for(tmp, **kw))


def run_recall(root, tmp, **kw):
    payload = json.dumps({"hook_event_name": "UserPromptSubmit", "cwd": str(root), "session_id": "s1", "prompt": "decision"})
    return subprocess.run([sys.executable, str(TOOLS / "memory_recall.py")], input=payload,
                          capture_output=True, text=True, timeout=30, env=env_for(tmp, **kw))


class MemoryEnabledTests(unittest.TestCase):
    def test_requires_both_trust_and_docs_ai(self):
        with tempfile.TemporaryDirectory() as tmp:
            old = {k: os.environ.get(k) for k in ("PB_TRUST_FILE", "PB_TRUST_ALL")}
            os.environ["PB_TRUST_FILE"] = str(Path(tmp) / "trusted.txt")
            os.environ.pop("PB_TRUST_ALL", None)
            try:
                root = Path(tmp) / "p"
                root.mkdir()
                self.assertFalse(pb_trust.memory_enabled(root))
                (root / "docs" / "ai").mkdir(parents=True)
                self.assertFalse(pb_trust.memory_enabled(root))      # docs/ai but untrusted
                pb_trust.add(root)
                self.assertTrue(pb_trust.memory_enabled(root))       # both
                other = Path(tmp) / "q"
                other.mkdir()
                pb_trust.add(other)
                self.assertFalse(pb_trust.memory_enabled(other))     # trusted but no docs/ai
                os.environ["PB_TRUST_ALL"] = "1"
                self.assertTrue(pb_trust.memory_enabled(Path(tmp) / "nowhere"))
            finally:
                for k, v in old.items():
                    os.environ.pop(k, None) if v is None else os.environ.__setitem__(k, v)


class HookOptInTests(unittest.TestCase):
    def assert_nothing_written(self, root, tmp):
        self.assertFalse((root / "docs").exists(), "hook created docs/ in a project that did not opt in")
        self.assertFalse((Path(tmp) / "mem").exists(), "hook created an index dir for a project that did not opt in")

    def test_compact_untrusted_and_no_docs_ai_writes_nothing(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = make_project(tmp)
            r = run_compact(root, tmp)
            self.assertEqual((r.returncode, r.stdout), (0, ""))
            self.assert_nothing_written(root, tmp)

    def test_compact_trusted_but_no_docs_ai_writes_nothing(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = make_project(tmp, trusted=True)
            run_compact(root, tmp)
            self.assert_nothing_written(root, tmp)

    def test_compact_docs_ai_but_untrusted_writes_nothing(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = make_project(tmp, ai_dir=True)
            run_compact(root, tmp)
            self.assertEqual(list((root / "docs" / "ai").iterdir()), [])
            self.assertFalse((Path(tmp) / "mem").exists())

    def test_compact_opted_in_project_captures(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = make_project(tmp, ai_dir=True, trusted=True)
            r = run_compact(root, tmp)
            self.assertEqual(r.returncode, 0)
            self.assertTrue(list((root / "docs" / "ai" / "adr").glob("*.md")))
            self.assertTrue(list((root / "docs" / "ai" / "archive").glob("*.md")))

    def test_recall_not_opted_in_creates_nothing(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = make_project(tmp)
            r = run_recall(root, tmp)
            self.assertEqual((r.returncode, r.stdout), (0, ""))
            self.assert_nothing_written(root, tmp)


if __name__ == "__main__":
    unittest.main()
