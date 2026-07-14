"""Task 5.1 end-to-end smoke test: run memory_compact.py on a sample
transcript from a repo SUBDIRECTORY, then memory_recall.py with a related
first prompt, and confirm the relevant memory pointer is surfaced from the
root-level DB (not scattered under the subdirectory)."""

import os
os.environ["PB_LOCAL_MEMORY"] = "1"
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

TOOLS_DIR = Path(__file__).resolve().parent.parent


class EndToEndSmokeTest(unittest.TestCase):
    def test_compact_then_recall_from_subdirectory(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            (repo_root / ".git").mkdir()
            nested_cwd = repo_root / "server" / "pkg" / "llm"
            nested_cwd.mkdir(parents=True)

            transcript = repo_root / "transcript.jsonl"
            transcript.write_text(
                json.dumps({
                    "role": "assistant",
                    "content": [{
                        "type": "text",
                        "text": (
                            '<adr title="Use sqlite-vec over Chroma">\n'
                            "  <decision>Single-file SQLite vector store, no server process.</decision>\n"
                            "  <rationale>Fits the per-project + hook model with zero infrastructure.</rationale>\n"
                            "</adr>\n"
                        ),
                    }],
                }) + "\n",
                encoding="utf-8",
            )

            compact_payload = json.dumps({
                "hook_event_name": "PreCompact",
                "transcript_path": str(transcript),
                "cwd": str(nested_cwd),
                "session_id": "smoke-session-1",
                "trigger": "auto",
            })
            compact_result = subprocess.run(
                [sys.executable, str(TOOLS_DIR / "memory_compact.py")],
                input=compact_payload,
                capture_output=True,
                text=True,
                cwd=str(nested_cwd),
                timeout=15,
            )
            self.assertEqual(compact_result.returncode, 0, compact_result.stderr)

            # ADR markdown and the DB must land at the repo ROOT, not under
            # the subdirectory the hook was actually launched from.
            self.assertTrue((repo_root / ".ai-memory" / "memory.db").exists())
            adr_files = list((repo_root / "docs" / "ai" / "adr").glob("*.md"))
            self.assertEqual(len(adr_files), 1)
            self.assertFalse((nested_cwd / ".ai-memory").exists())
            self.assertFalse((nested_cwd / "docs").exists())

            recall_payload = json.dumps({
                "hook_event_name": "UserPromptSubmit",
                "session_id": "smoke-session-2",
                "prompt": "why did we choose sqlite-vec over chroma for the vector store",
                "cwd": str(nested_cwd),
            })
            recall_result = subprocess.run(
                [sys.executable, str(TOOLS_DIR / "memory_recall.py")],
                input=recall_payload,
                capture_output=True,
                text=True,
                cwd=str(nested_cwd),
                timeout=15,
            )
            self.assertEqual(recall_result.returncode, 0, recall_result.stderr)
            self.assertIn("Use sqlite-vec over Chroma", recall_result.stdout)
            self.assertIn("docs/ai/adr", recall_result.stdout)


if __name__ == "__main__":
    unittest.main()
