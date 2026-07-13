import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import install_settings as ins  # noqa: E402


def _tracked_source() -> Path:
    return REPO_ROOT / "settings.json"


class MergeSettingsTests(unittest.TestCase):
    def test_fresh_dest_gets_both_hook_events(self):
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / "settings.json"
            merged = ins.install(_tracked_source(), dest)
            self.assertIn("PreCompact", merged["hooks"])
            self.assertIn("UserPromptSubmit", merged["hooks"])

    def test_preserves_preexisting_unrelated_hooks_and_keys(self):
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / "settings.json"
            dest.write_text(json.dumps({
                "hooks": {
                    "PreToolUse": [
                        {"matcher": "Bash", "hooks": [{"type": "command", "command": "echo hi"}]}
                    ]
                },
                "permissions": {"allow": ["Bash(git *)"]},
            }))
            merged = ins.install(_tracked_source(), dest)
            self.assertEqual(
                merged["hooks"]["PreToolUse"][0]["hooks"][0]["command"], "echo hi"
            )
            self.assertEqual(merged["permissions"], {"allow": ["Bash(git *)"]})
            self.assertIn("PreCompact", merged["hooks"])

    def test_running_twice_yields_no_duplicates(self):
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / "settings.json"
            ins.install(_tracked_source(), dest)
            merged = ins.install(_tracked_source(), dest)
            for event in ("PreCompact", "UserPromptSubmit"):
                groups = merged["hooks"][event]
                self.assertEqual(len(groups), 1)
                self.assertEqual(len(groups[0]["hooks"]), 1)

    def test_merging_into_dest_with_same_event_different_matcher_adds_new_group(self):
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / "settings.json"
            dest.write_text(json.dumps({
                "hooks": {
                    "PreCompact": [
                        {"matcher": "manual", "hooks": [{"type": "command", "command": "echo manual-only"}]}
                    ]
                }
            }))
            merged = ins.install(_tracked_source(), dest)
            matchers = {g["matcher"] for g in merged["hooks"]["PreCompact"]}
            self.assertEqual(matchers, {"manual", "manual|auto"})

    def test_missing_dest_file_creates_it(self):
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / "nested" / "settings.json"
            self.assertFalse(dest.exists())
            ins.install(_tracked_source(), dest)
            self.assertTrue(dest.exists())

    def test_empty_dest_file_is_treated_as_no_settings(self):
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / "settings.json"
            dest.write_text("")
            merged = ins.install(_tracked_source(), dest)
            self.assertIn("PreCompact", merged["hooks"])


class TrackedSettingsShapeTests(unittest.TestCase):
    def test_settings_json_is_valid_json_with_expected_hooks(self):
        data = json.loads(_tracked_source().read_text())
        self.assertIn("PreCompact", data["hooks"])
        self.assertIn("UserPromptSubmit", data["hooks"])
        for event, script in (("PreCompact", "memory_compact.py"), ("UserPromptSubmit", "memory_recall.py")):
            command = data["hooks"][event][0]["hooks"][0]["command"]
            self.assertIn(script, command)
            self.assertIn("$HOME/.claude/tools", command)
            self.assertNotIn("args", data["hooks"][event][0]["hooks"][0])  # shell form, not exec form

    def test_command_falls_back_to_python3_when_venv_missing(self):
        data = json.loads(_tracked_source().read_text())
        command = data["hooks"]["PreCompact"][0]["hooks"][0]["command"]
        with tempfile.TemporaryDirectory() as tmp:
            script_dir = Path(tmp) / ".claude" / "tools"
            script_dir.mkdir(parents=True)
            (script_dir / "memory_compact.py").write_text("import sys; sys.exit(0)")
            result = subprocess.run(
                ["sh", "-c", command],
                env={"HOME": tmp, "PATH": "/usr/bin:/bin:/usr/local/bin"},
                capture_output=True,
                text=True,
                timeout=10,
            )
            self.assertEqual(result.returncode, 0)


class MainCliTests(unittest.TestCase):
    def test_cli_merges_and_prints_confirmation(self):
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / "settings.json"
            result = subprocess.run(
                [sys.executable, str(REPO_ROOT / "scripts" / "install_settings.py"),
                 "--source", str(_tracked_source()), "--dest", str(dest)],
                capture_output=True,
                text=True,
                timeout=10,
            )
            self.assertEqual(result.returncode, 0)
            self.assertTrue(dest.exists())
            merged = json.loads(dest.read_text())
            self.assertIn("PreCompact", merged["hooks"])

    def test_cli_missing_source_exits_nonzero(self):
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / "settings.json"
            result = subprocess.run(
                [sys.executable, str(REPO_ROOT / "scripts" / "install_settings.py"),
                 "--source", str(Path(tmp) / "does-not-exist.json"), "--dest", str(dest)],
                capture_output=True,
                text=True,
                timeout=10,
            )
            self.assertNotEqual(result.returncode, 0)


if __name__ == "__main__":
    unittest.main()
