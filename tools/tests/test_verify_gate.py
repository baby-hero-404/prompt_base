"""Stop-hook gate: runs the project's `make verify` and blocks the agent on failure.

Contract: exit 0 = allow stop (also for every case where the gate does not apply),
exit 2 + stderr = block stop and feed the failure back to the agent.
"""

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

GATE = Path(__file__).resolve().parent.parent / "verify_gate.py"


def run_gate(cwd, payload=None, extra_env=None, raw=None, trusted=True):
    stdin = raw if raw is not None else json.dumps({"cwd": str(cwd), **(payload or {})})
    env = {k: v for k, v in os.environ.items() if k not in ("PB_TRUST_ALL", "PB_TRUST_FILE")}
    if trusted:
        env["PB_TRUST_ALL"] = "1"
    env.update(extra_env or {})
    return subprocess.run(
        [sys.executable, str(GATE)], input=stdin, capture_output=True, text=True, timeout=30, env=env
    )


def project(tmp, makefile):
    root = Path(tmp)
    if makefile is not None:
        (root / "Makefile").write_text(makefile)
    return root


class VerifyGateTests(unittest.TestCase):
    def test_no_makefile_allows_stop_silently(self):
        with tempfile.TemporaryDirectory() as tmp:
            r = run_gate(project(tmp, None))
            self.assertEqual((r.returncode, r.stdout, r.stderr), (0, "", ""))

    def test_makefile_without_verify_target_allows_stop(self):
        with tempfile.TemporaryDirectory() as tmp:
            r = run_gate(project(tmp, "test:\n\t@echo ok\n"))
            self.assertEqual(r.returncode, 0)
            self.assertEqual(r.stderr, "")

    def test_passing_verify_allows_stop(self):
        with tempfile.TemporaryDirectory() as tmp:
            r = run_gate(project(tmp, "verify:\n\t@echo fine\n"))
            self.assertEqual(r.returncode, 0)

    def test_failing_verify_blocks_and_reports_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            r = run_gate(project(tmp, "verify:\n\t@echo 'RULE 6.1 lib/a.dart has 400 lines'; exit 1\n"))
            self.assertEqual(r.returncode, 2)
            self.assertIn("RULE 6.1 lib/a.dart has 400 lines", r.stderr)
            self.assertIn("make verify", r.stderr)

    def test_untrusted_project_never_runs_make(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = project(tmp, "verify:\n\t@touch RAN; exit 1\n")
            r = run_gate(root, trusted=False, extra_env={"PB_TRUST_FILE": str(Path(tmp) / "none.txt")})
            self.assertEqual((r.returncode, r.stdout), (0, ""))
            self.assertFalse((root / "RAN").exists())

    def test_project_in_trust_file_is_gated(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = project(tmp, "verify:\n\t@exit 1\n")
            trust = Path(tmp) / "trusted.txt"
            trust.write_text(str(root.resolve()) + "\n")
            r = run_gate(root, trusted=False, extra_env={"PB_TRUST_FILE": str(trust)})
            self.assertEqual(r.returncode, 2)

    def test_stop_hook_active_never_blocks_again(self):
        with tempfile.TemporaryDirectory() as tmp:
            r = run_gate(project(tmp, "verify:\n\t@exit 1\n"), {"stop_hook_active": True})
            self.assertEqual(r.returncode, 0)

    def test_timeout_allows_stop_with_diagnostic(self):
        with tempfile.TemporaryDirectory() as tmp:
            r = run_gate(project(tmp, "verify:\n\t@sleep 5\n"), extra_env={"PB_VERIFY_TIMEOUT": "1"})
            self.assertEqual(r.returncode, 0)
            self.assertIn("timed out", r.stderr)

    def test_malformed_stdin_never_breaks_session(self):
        r = run_gate(".", raw="not json{{")
        self.assertEqual(r.returncode, 0)

    def test_failure_output_is_truncated(self):
        with tempfile.TemporaryDirectory() as tmp:
            r = run_gate(project(tmp, "verify:\n\t@seq 1 5000; exit 1\n"))
            self.assertEqual(r.returncode, 2)
            self.assertLess(len(r.stderr), 6000)
            self.assertIn("5000", r.stderr)  # tail is kept


if __name__ == "__main__":
    unittest.main()
