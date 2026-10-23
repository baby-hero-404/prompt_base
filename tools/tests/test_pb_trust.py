"""Per-project trust list: hooks that act on repo-controlled content only run for trusted projects."""

import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

TOOLS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(TOOLS))
import pb_trust  # noqa: E402

TOOL = TOOLS / "pb_trust.py"


class TrustTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.file = Path(self.tmp.name) / "trusted.txt"
        self.old = {k: os.environ.get(k) for k in ("PB_TRUST_FILE", "PB_TRUST_ALL")}
        os.environ["PB_TRUST_FILE"] = str(self.file)
        os.environ.pop("PB_TRUST_ALL", None)
        self.addCleanup(self._restore)
        self.proj = Path(self.tmp.name) / "proj"
        (self.proj / "sub").mkdir(parents=True)

    def _restore(self):
        for k, v in self.old.items():
            os.environ.pop(k, None) if v is None else os.environ.__setitem__(k, v)

    def test_untrusted_by_default(self):
        self.assertFalse(pb_trust.is_trusted(self.proj))

    def test_add_then_trusted_and_idempotent(self):
        pb_trust.add(self.proj)
        pb_trust.add(self.proj)
        self.assertTrue(pb_trust.is_trusted(self.proj))
        self.assertEqual(self.file.read_text().splitlines(), [str(self.proj.resolve())])

    def test_subdirectory_of_trusted_project_is_trusted(self):
        pb_trust.add(self.proj)
        self.assertTrue(pb_trust.is_trusted(self.proj / "sub"))

    def test_sibling_with_same_prefix_is_not_trusted(self):
        pb_trust.add(self.proj)
        other = Path(self.tmp.name) / "proj-evil"
        other.mkdir()
        self.assertFalse(pb_trust.is_trusted(other))

    def test_trust_all_escape_hatch(self):
        os.environ["PB_TRUST_ALL"] = "1"
        self.assertTrue(pb_trust.is_trusted(self.proj))

    def test_remove_untrusts_and_is_idempotent(self):
        pb_trust.add(self.proj)
        self.assertTrue(pb_trust.remove(self.proj))
        self.assertFalse(pb_trust.is_trusted(self.proj))
        self.assertFalse(pb_trust.remove(self.proj))

    def test_remove_keeps_other_entries(self):
        other = Path(self.tmp.name) / "other"
        other.mkdir()
        pb_trust.add(self.proj)
        pb_trust.add(other)
        pb_trust.remove(self.proj)
        self.assertTrue(pb_trust.is_trusted(other))

    def test_cli_add_and_list(self):
        env = {**os.environ}
        r = subprocess.run([sys.executable, str(TOOL), "--add", str(self.proj)],
                           capture_output=True, text=True, env=env, timeout=30)
        self.assertEqual(r.returncode, 0)
        r = subprocess.run([sys.executable, str(TOOL), "--list"], capture_output=True, text=True, env=env, timeout=30)
        self.assertIn(str(self.proj.resolve()), r.stdout)


if __name__ == "__main__":
    unittest.main()
