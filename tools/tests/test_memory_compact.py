import json
import os
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import memory_compact as mc  # noqa: E402
import memory_engine as me  # noqa: E402

ADR_A = (
    'Preamble text.\n'
    '<adr title="Use sqlite-vec over Chroma">\n'
    '  <decision>Single-file SQLite vector store.</decision>\n'
    '  <rationale>No server process; fits per-project + hook model.</rationale>\n'
    '</adr>\n'
)

ADR_B = (
    '<adr title="Local ONNX embeddings">\n'
    '  <decision>Use fastembed bge-small-en-v1.5 by default.</decision>\n'
    '  <rationale>Keeps the framework offline and self-contained.</rationale>\n'
    '</adr>\n'
)


def _write_transcript(tmp: str, text: str) -> str:
    path = Path(tmp) / "transcript.jsonl"
    line = {"role": "assistant", "content": [{"type": "text", "text": text}]}
    path.write_text(json.dumps(line) + "\n", encoding="utf-8")
    return str(path)


def _payload(tmp: str, transcript_path: str, session_id="sess-1"):
    return {
        "hook_event_name": "PreCompact",
        "transcript_path": transcript_path,
        "cwd": tmp,
        "session_id": session_id,
        "trigger": "auto",
    }


def _memory_rows(root: str):
    conn = sqlite3.connect(me.memory_db_path(root))
    conn.row_factory = sqlite3.Row
    rows = conn.execute("SELECT kind, title, source_path FROM memory").fetchall()
    return [dict(r) for r in rows]


class CompactExtractionTests(unittest.TestCase):
    def test_two_adr_tags_yield_two_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / ".git").mkdir()
            transcript = _write_transcript(tmp, ADR_A + ADR_B)
            mc.compact(tmp, me.normalize_payload(_payload(tmp, transcript)))
            adr_files = list(Path(me.adr_dir(tmp)).glob("*.md"))
            self.assertEqual(len(adr_files), 2)

    def test_no_adr_tags_yields_rollup_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / ".git").mkdir()
            transcript = _write_transcript(tmp, "Just a plain conversation, no decisions here.")
            mc.compact(tmp, me.normalize_payload(_payload(tmp, transcript)))
            self.assertEqual(list(Path(me.adr_dir(tmp)).glob("*.md")), [])
            self.assertEqual(len(list(Path(me.archive_dir(tmp)).glob("*.md"))), 1)

    def test_rerun_same_transcript_adds_no_duplicate_rows(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / ".git").mkdir()
            transcript = _write_transcript(tmp, ADR_A + ADR_B)
            payload = me.normalize_payload(_payload(tmp, transcript))
            mc.compact(tmp, payload)
            first_count = len(_memory_rows(tmp))
            mc.compact(tmp, payload)
            second_count = len(_memory_rows(tmp))
            self.assertEqual(first_count, second_count)
            self.assertEqual(len(list(Path(me.adr_dir(tmp)).glob("*.md"))), 2)

    def test_same_slug_collision_yields_two_files_no_overwrite(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / ".git").mkdir()
            same_title = (
                '<adr title="Same title">\n'
                '  <decision>First decision.</decision>\n'
                '  <rationale>First rationale.</rationale>\n'
                '</adr>\n'
                '<adr title="Same title">\n'
                '  <decision>Second, different decision.</decision>\n'
                '  <rationale>Second, different rationale.</rationale>\n'
                '</adr>\n'
            )
            transcript = _write_transcript(tmp, same_title)
            mc.compact(tmp, me.normalize_payload(_payload(tmp, transcript)))
            adr_files = list(Path(me.adr_dir(tmp)).glob("*.md"))
            self.assertEqual(len(adr_files), 2)
            contents = {f.read_text(encoding="utf-8") for f in adr_files}
            self.assertEqual(len(contents), 2)  # never overwritten with different content

    def test_secret_in_adr_is_never_persisted(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / ".git").mkdir()
            leaky = (
                '<adr title="Leaky decision">\n'
                '  <decision>api_key: sk-abcdefghijklmnopqrstuvwxyz123456</decision>\n'
                '  <rationale>irrelevant</rationale>\n'
                '</adr>\n'
            )
            transcript = _write_transcript(tmp, leaky)
            mc.compact(tmp, me.normalize_payload(_payload(tmp, transcript)))
            self.assertEqual(list(Path(me.adr_dir(tmp)).glob("*.md")), [])
            self.assertEqual(_memory_rows(tmp), [])

    def test_files_land_at_repo_root_when_launched_from_subdirectory(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / ".git").mkdir()
            nested = Path(tmp) / "server" / "pkg" / "llm"
            nested.mkdir(parents=True)
            transcript = _write_transcript(tmp, ADR_A)
            payload = me.normalize_payload(_payload(str(nested), transcript))
            root = me.resolve_project_root(payload["cwd"])
            self.assertEqual(root, str(Path(tmp).resolve()))
            mc.compact(root, payload)
            self.assertEqual(len(list(Path(me.adr_dir(tmp)).glob("*.md"))), 1)
            self.assertEqual(list(nested.glob("**/*.md")), [])


class CompactMainEntrypointTests(unittest.TestCase):
    def test_malformed_stdin_never_raises(self):
        # main() reads real sys.stdin; exercise compact()'s error handling
        # path directly instead, since that's what main() delegates to.
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / ".git").mkdir()
            payload = me.normalize_payload({"cwd": tmp})  # no transcript_path
            try:
                mc.compact(tmp, payload)
            except Exception as exc:  # pragma: no cover - must never happen
                self.fail(f"compact() raised on missing transcript_path: {exc}")

    def test_subprocess_malformed_stdin_exits_zero_with_empty_stdout(self):
        script = str(Path(__file__).resolve().parent.parent / "memory_compact.py")
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / ".git").mkdir()
            result = subprocess.run(
                [sys.executable, script],
                input="not valid json {{{",
                capture_output=True,
                text=True,
                cwd=tmp,
                timeout=10,
            )
            self.assertEqual(result.returncode, 0)
            self.assertEqual(result.stdout, "")
            self.assertTrue((Path(tmp) / ".ai-memory" / "engine.log").exists())

    def test_subprocess_empty_stdin_exits_zero(self):
        script = str(Path(__file__).resolve().parent.parent / "memory_compact.py")
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / ".git").mkdir()
            result = subprocess.run(
                [sys.executable, script],
                input="",
                capture_output=True,
                text=True,
                cwd=tmp,
                timeout=10,
            )
            self.assertEqual(result.returncode, 0)
            self.assertEqual(result.stdout, "")


if __name__ == "__main__":
    unittest.main()
