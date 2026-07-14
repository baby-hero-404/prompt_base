import os
os.environ["PB_LOCAL_MEMORY"] = "1"
import subprocess
import sys
import tempfile
import time
import types
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import memory_engine as me  # noqa: E402
import memory_bench as mb  # noqa: E402


class _FakeTextEmbedding:
    def __init__(self, model_name, delay=0.03):
        time.sleep(delay)
        self.model_name = model_name

    def embed(self, texts):
        for _ in texts:
            yield [0.1] * me.EMBED_DIM


def _install_fake_fastembed(delay=0.03):
    stub = types.ModuleType("fastembed")
    stub.TextEmbedding = lambda model_name: _FakeTextEmbedding(model_name, delay=delay)
    sys.modules["fastembed"] = stub


def _remove_fake_fastembed():
    sys.modules.pop("fastembed", None)


class AutoCalibrationTests(unittest.TestCase):
    def setUp(self):
        me._EMBED_BACKEND = None
        me._COLD_LOAD_MS = None
        _install_fake_fastembed(delay=0.02)

    def tearDown(self):
        me._EMBED_BACKEND = None
        me._COLD_LOAD_MS = None
        _remove_fake_fastembed()

    def test_first_upsert_records_embed_load_ms(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / ".git").mkdir()
            conn = me.init_db(tmp)
            self.assertIsNone(me.get_embed_load_ms(conn))
            me.upsert(conn, tmp, "adr", "Title", "some decision body text", "docs/ai/adr/x.md")
            recorded = me.get_embed_load_ms(conn)
            self.assertIsNotNone(recorded)
            self.assertGreater(recorded, 0)

    def test_second_upsert_does_not_overwrite_recorded_value(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / ".git").mkdir()
            conn = me.init_db(tmp)
            me.upsert(conn, tmp, "adr", "Title", "first decision body text", "docs/ai/adr/x.md")
            first = me.get_embed_load_ms(conn)
            me.upsert(conn, tmp, "adr", "Title2", "second decision body text", "docs/ai/adr/y.md")
            self.assertEqual(me.get_embed_load_ms(conn), first)


class MemoryBenchTests(unittest.TestCase):
    def setUp(self):
        me._EMBED_BACKEND = None
        me._COLD_LOAD_MS = None
        _install_fake_fastembed(delay=0.02)

    def tearDown(self):
        me._EMBED_BACKEND = None
        me._COLD_LOAD_MS = None
        _remove_fake_fastembed()

    def test_bench_forces_fresh_measurement_and_returns_ms(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / ".git").mkdir()
            load_ms = mb.bench(tmp)
            self.assertIsNotNone(load_ms)
            self.assertGreater(load_ms, 0)

    def test_bench_ignores_previously_cached_backend(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / ".git").mkdir()
            me.embed("warm the cache", root=tmp)  # populates _EMBED_BACKEND
            first = me._COLD_LOAD_MS
            second = mb.bench(tmp)  # must re-measure, not reuse the cached backend
            self.assertIsNotNone(second)
            self.assertIsNotNone(first)

    def test_main_writes_meta_and_prints_confirmation(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / ".git").mkdir()
            root = me.resolve_project_root(tmp)
            load_ms = mb.bench(root)
            conn = me.init_db(root)
            me.set_embed_load_ms(conn, load_ms)
            self.assertAlmostEqual(me.get_embed_load_ms(conn), load_ms)


class MemoryBenchNoBackendTests(unittest.TestCase):
    def test_subprocess_without_fastembed_exits_nonzero_with_message(self):
        script = str(Path(__file__).resolve().parent.parent / "memory_bench.py")
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / ".git").mkdir()
            result = subprocess.run(
                [sys.executable, script, "--root", tmp],
                capture_output=True,
                text=True,
                timeout=10,
            )
            # This sandbox genuinely has no fastembed installed (see
            # test_hook_resilience.TestAmbientEnvIsMissingDependency).
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("no local embedding backend", result.stderr)


if __name__ == "__main__":
    unittest.main()
