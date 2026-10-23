"""M3: invariant re-injection. Core is agent-neutral (--print); hook mode serves Claude."""

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

TOOL = Path(__file__).resolve().parent.parent / "memory_invariants.py"

DOMAIN = """# Domain

## Core Concepts
- thing

## Invariant Rules
1. 1.2 [test] domain/ never imports Flutter
2. 6.1 [test] UI files <= 300 lines

## Key Learnings
- not an invariant
"""


def env_for(tmp, **extra):
    base = {k: v for k, v in os.environ.items() if k not in ("PB_TRUST_ALL", "PB_TRUST_FILE")}
    return {**base, "PB_GLOBAL_MEMORY_DIR": str(Path(tmp) / "mem"),
            "PB_LEGACY_PROJECTS_DIR": str(Path(tmp) / "legacy"),
            "PB_TRUST_FILE": str(Path(tmp) / "trusted.txt"), **extra}


def project(tmp, domain=DOMAIN):
    root = Path(tmp) / "work" / "app"
    (root / ".git").mkdir(parents=True)
    if domain is not None:
        (root / "docs" / "ai").mkdir(parents=True)
        (root / "docs" / "ai" / "DOMAIN.md").write_text(domain)
    return root


def cli(root, tmp):
    return subprocess.run([sys.executable, str(TOOL), "--print", "--root", str(root)],
                          capture_output=True, text=True, timeout=30, env=env_for(tmp))


def hook(root, tmp, session="s1", raw=None, trusted=True, **extra):
    if trusted:
        extra.setdefault("PB_TRUST_ALL", "1")
    payload = raw if raw is not None else json.dumps({"cwd": str(root), "session_id": session, "prompt": "hi"})
    return subprocess.run([sys.executable, str(TOOL)], input=payload,
                          capture_output=True, text=True, timeout=30, env=env_for(tmp, **extra))


class CliTests(unittest.TestCase):
    def test_prints_only_invariant_section(self):
        with tempfile.TemporaryDirectory() as tmp:
            r = cli(project(tmp), tmp)
            self.assertEqual(r.returncode, 0)
            self.assertIn("domain/ never imports Flutter", r.stdout)
            self.assertNotIn("not an invariant", r.stdout)
            self.assertNotIn("- thing", r.stdout)

    def test_no_domain_file_prints_nothing(self):
        with tempfile.TemporaryDirectory() as tmp:
            r = cli(project(tmp, domain=None), tmp)
            self.assertEqual((r.returncode, r.stdout), (0, ""))

    def test_no_invariant_section_prints_nothing(self):
        with tempfile.TemporaryDirectory() as tmp:
            r = cli(project(tmp, domain="# Domain\n\n## Core Concepts\n- x\n"), tmp)
            self.assertEqual(r.stdout, "")

    def test_legacy_gemini_path_is_fallback(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = project(tmp, domain=None)
            legacy = Path(tmp) / "legacy" / "work-app"
            legacy.mkdir(parents=True)
            (legacy / "DOMAIN.md").write_text(DOMAIN)
            self.assertIn("UI files <= 300 lines", cli(root, tmp).stdout)

    def test_output_is_capped(self):
        with tempfile.TemporaryDirectory() as tmp:
            big = "## Invariant Rules\n" + "".join(f"{i}. rule number {i} " + "x" * 80 + "\n" for i in range(200))
            r = cli(project(tmp, domain=big), tmp)
            self.assertLessEqual(len(r.stdout), 1800)
            self.assertIn("rule number 0", r.stdout)

    def test_content_with_secret_is_skipped(self):
        with tempfile.TemporaryDirectory() as tmp:
            bad = "## Invariant Rules\n1. token = abcdefghijklmnop1234\n"
            r = cli(project(tmp, domain=bad), tmp)
            self.assertEqual(r.stdout, "")


class HookTests(unittest.TestCase):
    def test_first_prompt_emits_then_silent_until_tenth(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = project(tmp)
            outs = [hook(root, tmp).stdout for _ in range(11)]
            self.assertIn("never imports Flutter", outs[0])
            self.assertTrue(all(o == "" for o in outs[1:10]))
            self.assertIn("never imports Flutter", outs[10])

    def test_untrusted_project_injects_nothing_and_writes_no_state(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = project(tmp)
            r = hook(root, tmp, trusted=False)
            self.assertEqual((r.returncode, r.stdout), (0, ""))
            self.assertFalse((Path(tmp) / "mem").exists())

    def test_trusted_via_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = project(tmp)
            (Path(tmp) / "trusted.txt").write_text(str(root.resolve()) + "\n")
            self.assertIn("Flutter", hook(root, tmp, trusted=False).stdout)

    def test_project_without_invariants_writes_no_state(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = project(tmp, domain=None)
            hook(root, tmp)
            self.assertFalse((Path(tmp) / "mem").exists())

    def test_new_session_resets_counter(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = project(tmp)
            hook(root, tmp, session="a")
            self.assertEqual(hook(root, tmp, session="a").stdout, "")
            self.assertIn("Flutter", hook(root, tmp, session="b").stdout)

    def test_interval_is_configurable(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = project(tmp)
            outs = [hook(root, tmp, PB_INVARIANT_EVERY="2").stdout for _ in range(3)]
            self.assertEqual([bool(o) for o in outs], [True, False, True])

    def test_malformed_stdin_is_silent_exit_zero(self):
        with tempfile.TemporaryDirectory() as tmp:
            r = hook(project(tmp), tmp, raw="not json{{")
            self.assertEqual((r.returncode, r.stdout), (0, ""))

    def test_missing_session_id_is_silent(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = project(tmp)
            r = hook(root, tmp, raw=json.dumps({"cwd": str(root), "prompt": "x"}))
            self.assertEqual((r.returncode, r.stdout), (0, ""))


if __name__ == "__main__":
    unittest.main()
