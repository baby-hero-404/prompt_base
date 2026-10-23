"""Unit tests for the Gemini/Antigravity Hook Adapter.
Verifies payload normalization, injectSteps output for PreInvocation (invariants, recall),
decision JSON protocol for Stop (verify_gate), and hooks installer merging.
"""

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

TOOLS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(TOOLS))

import memory_engine as me
import pb_trust

SCRIPTS = TOOLS.parent / "scripts"
sys.path.insert(0, str(SCRIPTS))
import install_gemini_hooks as igh


class GeminiAdapterTests(unittest.TestCase):
    def test_normalize_pre_invocation(self):
        raw = {
            "conversationId": "sess-gemini-1",
            "workspacePaths": ["/home/user/my_project"],
            "transcriptPath": "/home/user/my_project/transcript.jsonl",
            "invocationNum": 1,
        }
        norm = me.normalize_payload(raw)
        self.assertEqual(norm["host"], "gemini")
        self.assertEqual(norm["event"], "PreInvocation")
        self.assertEqual(norm["session_id"], "sess-gemini-1")
        self.assertEqual(norm["cwd"], "/home/user/my_project")
        self.assertEqual(norm["transcript_path"], "/home/user/my_project/transcript.jsonl")

    def test_normalize_stop_event(self):
        raw = {
            "conversationId": "sess-gemini-2",
            "workspacePaths": ["/home/user/my_project"],
            "executionNum": 1,
            "terminationReason": "model_stop",
        }
        norm = me.normalize_payload(raw)
        self.assertEqual(norm["host"], "gemini")
        self.assertEqual(norm["event"], "Stop")
        self.assertEqual(norm["cwd"], "/home/user/my_project")

    def test_extract_last_user_prompt_from_transcript(self):
        with tempfile.TemporaryDirectory() as tmp:
            transcript = Path(tmp) / "transcript.jsonl"
            lines = [
                json.dumps({"type": "SYSTEM", "content": "system start"}),
                json.dumps({"type": "USER_INPUT", "content": "How does memory recall work?"}),
                json.dumps({"type": "PLANNER_RESPONSE", "content": "Thinking..."}),
            ]
            transcript.write_text("\n".join(lines) + "\n")
            raw = {
                "conversationId": "sess-3",
                "workspacePaths": [tmp],
                "transcriptPath": str(transcript),
                "invocationNum": 2,
            }
            norm = me.normalize_payload(raw)
            self.assertEqual(norm["prompt"], "How does memory recall work?")

    def test_verify_gate_gemini_decision_continue_on_failure(self):
        gate_script = TOOLS / "verify_gate.py"
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "Makefile").write_text("verify:\n\t@echo 'FAIL lint error'; exit 1\n")
            env = {**os.environ, "PB_TRUST_ALL": "1"}
            payload = json.dumps({
                "conversationId": "conv-1",
                "workspacePaths": [str(root)],
                "executionNum": 1,
                "terminationReason": "model_stop",
            })
            r = subprocess.run([sys.executable, str(gate_script)], input=payload, text=True, capture_output=True, env=env)
            self.assertEqual(r.returncode, 0)
            data = json.loads(r.stdout)
            self.assertEqual(data["decision"], "continue")
            self.assertIn("FAIL lint error", data["reason"])

    def test_verify_gate_gemini_decision_allow_on_success(self):
        gate_script = TOOLS / "verify_gate.py"
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "Makefile").write_text("verify:\n\t@echo 'All checks passed'\n")
            env = {**os.environ, "PB_TRUST_ALL": "1"}
            payload = json.dumps({
                "conversationId": "conv-1",
                "workspacePaths": [str(root)],
                "executionNum": 1,
                "terminationReason": "model_stop",
            })
            r = subprocess.run([sys.executable, str(gate_script)], input=payload, text=True, capture_output=True, env=env)
            self.assertEqual(r.returncode, 0)
            data = json.loads(r.stdout)
            self.assertEqual(data["decision"], "allow")

    def test_hooks_merger(self):
        dest = {
            "custom-tool": {
                "PreToolUse": [{"type": "command", "command": "./test.sh"}]
            }
        }
        source = {
            "prompt-base": {
                "PreInvocation": [{"type": "command", "command": "python3 recall.py"}],
                "Stop": [{"type": "command", "command": "python3 gate.py"}]
            }
        }
        merged = igh.merge_hooks(dest, source)
        self.assertIn("custom-tool", merged)
        self.assertIn("prompt-base", merged)
        self.assertEqual(len(merged["prompt-base"]["PreInvocation"]), 1)


if __name__ == "__main__":
    unittest.main()
