"""M2: staleness check for docs/ai/manifest.json (agent-neutral, stdlib only)."""

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

TOOL = Path(__file__).resolve().parent.parent / "memory_stale.py"


def run(root, *args):
    return subprocess.run(
        [sys.executable, str(TOOL), "--root", str(root), *args],
        capture_output=True, text=True, timeout=30,
    )


def make_project(tmp, triggers=("ARCHITECTURE.md",), files=None, manifest=True):
    root = Path(tmp)
    for name, text in (files if files is not None else {"ARCHITECTURE.md": "v1"}).items():
        (root / name).write_text(text)
    if manifest:
        (root / "docs" / "ai").mkdir(parents=True)
        (root / "docs" / "ai" / "manifest.json").write_text(
            json.dumps({"project": "x", "lastScanned": "", "checksums": {}, "autoRefreshTriggers": list(triggers)})
        )
    return root


class MemoryStaleTests(unittest.TestCase):
    def test_never_scanned_manifest_is_stale(self):
        with tempfile.TemporaryDirectory() as tmp:
            r = run(make_project(tmp))
            self.assertEqual(r.returncode, 1)
            self.assertIn("ARCHITECTURE.md", r.stdout)

    def test_update_then_check_is_fresh(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = make_project(tmp)
            self.assertEqual(run(root, "--update").returncode, 0)
            r = run(root)
            self.assertEqual(r.returncode, 0)
            data = json.loads((root / "docs/ai/manifest.json").read_text())
            self.assertTrue(data["lastScanned"])
            self.assertIn("ARCHITECTURE.md", data["checksums"])

    def test_edit_after_update_is_stale(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = make_project(tmp)
            run(root, "--update")
            (root / "ARCHITECTURE.md").write_text("v2")
            r = run(root)
            self.assertEqual(r.returncode, 1)
            self.assertIn("ARCHITECTURE.md", r.stdout)

    def test_newly_listed_trigger_is_stale(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = make_project(tmp, files={"ARCHITECTURE.md": "a", "Makefile": "b"})
            run(root, "--update")
            m = root / "docs/ai/manifest.json"
            data = json.loads(m.read_text())
            data["autoRefreshTriggers"].append("Makefile")
            m.write_text(json.dumps(data))
            r = run(root)
            self.assertEqual(r.returncode, 1)
            self.assertIn("Makefile", r.stdout)

    def test_missing_trigger_file_is_ignored(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = make_project(tmp, triggers=("ARCHITECTURE.md", "nope.json"))
            run(root, "--update")
            self.assertEqual(run(root).returncode, 0)

    def test_missing_manifest_is_reported_not_crash(self):
        with tempfile.TemporaryDirectory() as tmp:
            r = run(make_project(tmp, manifest=False))
            self.assertEqual(r.returncode, 1)
            self.assertIn("manifest", r.stdout.lower())

    def test_corrupt_manifest_is_reported_not_crash(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = make_project(tmp)
            (root / "docs/ai/manifest.json").write_text("{not json")
            r = run(root)
            self.assertEqual(r.returncode, 1)
            self.assertNotIn("Traceback", r.stderr)

    def test_trigger_outside_root_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = make_project(tmp, triggers=("../secret",))
            run(root, "--update")
            data = json.loads((root / "docs/ai/manifest.json").read_text())
            self.assertNotIn("../secret", data["checksums"])


if __name__ == "__main__":
    unittest.main()
