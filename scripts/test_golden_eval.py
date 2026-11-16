#!/usr/bin/env python3
"""Offline unit tests for golden_eval.py. No API calls or network requests are made."""
import io
import json
import os
import sys
import tempfile
import unittest
import urllib.error
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))
import golden_eval as ge

ROOT = Path(__file__).resolve().parent.parent


class VerdictTests(unittest.TestCase):
    def test_invalid_verdict_fails_closed(self):
        for bad in ({}, {"status": "MAYBE"}, "text", None, {"score": 1}):
            self.assertEqual(ge.normalize_verdict(bad)["status"], "ERROR")

    def test_valid_verdict_passes_through(self):
        v = {"score": 1, "status": "BETTER", "reasoning": "ok"}
        self.assertEqual(ge.normalize_verdict(v), v)

    def test_invert_flips_worse_and_better_only(self):
        self.assertEqual(ge.invert_verdict({"status": "WORSE", "score": -2})["status"], "BETTER")
        self.assertEqual(ge.invert_verdict({"status": "WORSE", "score": -2})["score"], 2)
        self.assertEqual(ge.invert_verdict({"status": "BETTER", "score": 1})["status"], "WORSE")
        self.assertEqual(ge.invert_verdict({"status": "SAME", "score": 0})["status"], "SAME")

    def test_judge_failure_is_error_not_same(self):
        with mock.patch.object(ge, "gemini_generate", return_value={"error": "boom"}):
            self.assertEqual(ge.judge_results("a", "b", [], "m", ROOT)["status"], "ERROR")
        garbage = {"candidates": [{"content": {"parts": [{"text": "no json here"}]}}]}
        with mock.patch.object(ge, "gemini_generate", return_value=garbage):
            self.assertEqual(ge.judge_results("a", "b", [], "m", ROOT)["status"], "ERROR")
        wrong = {"candidates": [{"content": {"parts": [{"text": '{"status": "GREAT"}'}]}}]}
        with mock.patch.object(ge, "gemini_generate", return_value=wrong):
            self.assertEqual(ge.judge_results("a", "b", [], "m", ROOT)["status"], "ERROR")

    def test_compare_swaps_order_and_maps_verdict_back(self):
        seen = []

        def fake_judge(first, second, *a, **k):
            seen.append((first, second))
            return {"score": -1, "status": "WORSE", "reasoning": "second is worse",
                    "scores": {"first": 70, "second": 90}}

        class AlwaysSwap:
            def random(self): return 0.0

        class NeverSwap:
            def random(self): return 0.9

        with mock.patch.object(ge, "judge_results", side_effect=fake_judge):
            plain = ge.compare("REF", "CAND", [], "m", ROOT, "p", NeverSwap())
            swapped = ge.compare("REF", "CAND", [], "m", ROOT, "p", AlwaysSwap())
        self.assertEqual(seen, [("REF", "CAND"), ("CAND", "REF")])
        self.assertEqual(plain["status"], "WORSE")
        self.assertEqual(swapped["status"], "BETTER")
        # Quality score mapping:
        self.assertEqual(plain["quality"], {"old": 70.0, "new": 90.0})
        self.assertEqual(swapped["quality"], {"old": 90.0, "new": 70.0})

    def test_aggregate_runs(self):
        self.assertEqual(ge.aggregate_runs(["SAME", "SAME", "WORSE"]), "SAME")
        self.assertEqual(ge.aggregate_runs(["WORSE", "WORSE", "SAME"]), "WORSE")
        self.assertEqual(ge.aggregate_runs(["BETTER", "BETTER", "SAME"]), "BETTER")
        self.assertEqual(ge.aggregate_runs(["SAME", "WORSE"]), "SAME")
        self.assertEqual(ge.aggregate_runs(["SAME", "ERROR"]), "ERROR")
        self.assertEqual(ge.aggregate_runs([]), "ERROR")

    def test_baseline_verdict_can_fail_the_run(self):
        # Old vs New is fine, but the skill is worse than using no skill at all.
        self.assertEqual(ge.overall_status(["SAME", "WORSE"]), "WORSE")

    def test_overall_status_precedence(self):
        self.assertEqual(ge.overall_status(["WORSE", "ERROR"]), "ERROR")
        self.assertEqual(ge.overall_status([None, None]), "UNVERIFIED")
        self.assertEqual(ge.overall_status([]), "UNVERIFIED")
        self.assertEqual(ge.overall_status(["SAME", "BETTER"]), "BETTER")
        self.assertEqual(ge.overall_status(["SAME", "SAME"]), "SAME")

    def test_exit_codes(self):
        self.assertEqual(ge.exit_code("WORSE"), 1)
        self.assertEqual(ge.exit_code("ERROR"), 1)
        self.assertEqual(ge.exit_code("SAME"), 0)
        self.assertEqual(ge.exit_code("BETTER"), 0)
        self.assertEqual(ge.exit_code("UNVERIFIED"), 0)
        self.assertEqual(ge.exit_code("UNVERIFIED", strict=True), 1)


class BaselineTests(unittest.TestCase):
    def test_reads_a_committed_file(self):
        text = ge.load_baseline(ROOT, "scripts/golden_eval.py", "HEAD")
        self.assertIn("golden", text.lower())

    def test_unknown_ref_or_path_raises(self):
        with self.assertRaises(RuntimeError):
            ge.load_baseline(ROOT, "scripts/golden_eval.py", "no-such-ref-xyz")
        with self.assertRaises(RuntimeError):
            ge.load_baseline(ROOT, "no/such/file.md", "HEAD")

    def test_option_like_ref_is_rejected(self):
        for bad in ("--output=x", "-x", ""):
            with self.assertRaises(RuntimeError):
                ge.load_baseline(ROOT, "scripts/golden_eval.py", bad)


class CoverageTests(unittest.TestCase):
    def test_coverage_lists_missing_skills(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            for name in ("alpha", "beta", "gamma"):
                (root / "skills" / name).mkdir(parents=True)
                (root / "skills" / name / "SKILL.md").write_text("x")
            (root / "evals" / "golden" / "alpha").mkdir(parents=True)
            (root / "evals" / "golden" / "alpha" / "task1.yaml").write_text("prompt: p\nrubric: []\n")
            (root / "evals" / "golden" / "beta").mkdir(parents=True)  # directory without tasks
            covered, missing = ge.coverage(root)
            self.assertEqual(covered, ["alpha"])
            self.assertEqual(missing, ["beta", "gamma"])

    def test_load_tasks_empty_when_no_directory(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(ge.load_tasks(Path(d), "nothing"), [])


class UsageTests(unittest.TestCase):
    def test_full_usage(self):
        res = {
            "usageMetadata": {
                "promptTokenCount": 120,
                "cachedContentTokenCount": 30,
                "candidatesTokenCount": 45,
                "thoughtsTokenCount": 15,
            }
        }
        u = ge.usage_of(res)
        self.assertEqual(u["input"], 120)
        self.assertEqual(u["cached"], 30)
        self.assertEqual(u["output"], 45)
        self.assertEqual(u["thinking"], 15)
        self.assertFalse(u["usage_missing"])

    def test_missing_usage(self):
        for bad in ({}, {"usageMetadata": {}}, None):
            u = ge.usage_of(bad)
            self.assertEqual(u["input"], 0)
            self.assertEqual(u["cached"], 0)
            self.assertEqual(u["output"], 0)
            self.assertEqual(u["thinking"], 0)
            self.assertTrue(u["usage_missing"])

    def test_missing_optional_fields(self):
        res = {
            "usageMetadata": {
                "promptTokenCount": 100,
                "candidatesTokenCount": 50,
            }
        }
        u = ge.usage_of(res)
        self.assertEqual(u["input"], 100)
        self.assertEqual(u["cached"], 0)
        self.assertEqual(u["output"], 50)
        self.assertEqual(u["thinking"], 0)
        self.assertFalse(u["usage_missing"])


class AttributionTests(unittest.TestCase):
    def test_one_turn(self):
        rows = ge.attribute([100], [20], baseline_first=80, is_baseline=False)
        self.assertEqual(len(rows), 1)
        r = rows[0]
        self.assertEqual(r["fixed"], 80)
        self.assertEqual(r["skill"], 20)
        self.assertEqual(r["model_replies"], 0)
        self.assertEqual(r["tool_outputs"], 0)
        self.assertTrue(r["skill_known"])
        self.assertFalse(r["derived_clamped"])
        self.assertEqual(r["fixed"] + r["skill"] + r["model_replies"] + r["tool_outputs"], 100)

    def test_three_turns(self):
        prompt_tokens = [100, 150, 230]
        outputs = [20, 40, 30]
        rows = ge.attribute(prompt_tokens, outputs, baseline_first=80, is_baseline=False)
        self.assertEqual(len(rows), 3)

        # Turn 1
        self.assertEqual(rows[0]["fixed"], 80)
        self.assertEqual(rows[0]["skill"], 20)
        self.assertEqual(rows[0]["model_replies"], 0)
        self.assertEqual(rows[0]["tool_outputs"], 0)

        # Turn 2: growth = 50. reply = min(50, 20) = 20. tool = 50 - 20 = 30.
        self.assertEqual(rows[1]["fixed"], 80)
        self.assertEqual(rows[1]["skill"], 20)
        self.assertEqual(rows[1]["model_replies"], 20)
        self.assertEqual(rows[1]["tool_outputs"], 30)

        # Turn 3: growth = 80. reply = 20 + min(80, 40) = 60. tool = 30 + (80 - 40) = 70.
        self.assertEqual(rows[2]["fixed"], 80)
        self.assertEqual(rows[2]["skill"], 20)
        self.assertEqual(rows[2]["model_replies"], 60)
        self.assertEqual(rows[2]["tool_outputs"], 70)

        for k, total in enumerate(prompt_tokens):
            r = rows[k]
            self.assertEqual(r["fixed"] + r["skill"] + r["model_replies"] + r["tool_outputs"], total)

    def test_baseline_turn(self):
        rows = ge.attribute([80, 120], [25, 30], baseline_first=80, is_baseline=True)
        self.assertEqual(rows[0]["fixed"], 80)
        self.assertEqual(rows[0]["skill"], 0)
        self.assertTrue(rows[0]["skill_known"])

    def test_fixed_none(self):
        rows = ge.attribute([100], [20], baseline_first=None, is_baseline=False)
        self.assertEqual(rows[0]["fixed"], 100)
        self.assertEqual(rows[0]["skill"], 0)
        self.assertFalse(rows[0]["skill_known"])

    def test_negative_growth_clamped(self):
        prompt_tokens = [100, 90]
        outputs = [20, 30]
        rows = ge.attribute(prompt_tokens, outputs, baseline_first=50, is_baseline=False)
        self.assertTrue(rows[1]["derived_clamped"])
        for k, total in enumerate(prompt_tokens):
            r = rows[k]
            self.assertEqual(r["fixed"] + r["skill"] + r["model_replies"] + r["tool_outputs"], total)

    def test_empty_tokens(self):
        self.assertEqual(ge.attribute([], []), [])


class PricingTests(unittest.TestCase):
    def setUp(self):
        self.pricing = {
            "version": "2026-11-16",
            "models": {
                "test-model": {
                    "input_per_million": 1.0,
                    "cached_input_per_million": 0.5,
                    "output_per_million": 2.0,
                },
                "no-cache-model": {
                    "input_per_million": 1.5,
                    "cached_input_per_million": None,
                    "output_per_million": 3.0,
                },
                "null-model": {
                    "input_per_million": None,
                    "cached_input_per_million": None,
                    "output_per_million": None,
                },
            },
        }

    def test_priced_model(self):
        tokens = {"input": 1000, "cached": 200, "output": 500, "thinking": 100, "usage_missing": False}
        # (1000 - 200) * 1.0 + 200 * 0.5 + (500 + 100) * 2.0 = 800 + 100 + 1200 = 2100 / 1M = 0.0021
        cost = ge.price(tokens, "test-model", self.pricing)
        self.assertEqual(cost, 0.0021)

    def test_model_with_null_prices(self):
        tokens = {"input": 1000, "cached": 0, "output": 500, "thinking": 0, "usage_missing": False}
        cost = ge.price(tokens, "null-model", self.pricing)
        self.assertIsNone(cost)

    def test_unknown_model(self):
        tokens = {"input": 1000, "cached": 0, "output": 500, "thinking": 0, "usage_missing": False}
        cost = ge.price(tokens, "unknown-model", self.pricing)
        self.assertIsNone(cost)

    def test_cached_rate_fallback(self):
        tokens = {"input": 1000, "cached": 200, "output": 100, "thinking": 0, "usage_missing": False}
        # cached rate falls back to input_per_million (1.5)
        # 800 * 1.5 + 200 * 1.5 + 100 * 3.0 = 1500 + 300 = 1800 / 1M = 0.0018
        cost = ge.price(tokens, "no-cache-model", self.pricing)
        self.assertEqual(cost, 0.0018)

    def test_missing_pricing_file_and_invalid_json(self):
        self.assertEqual(ge.load_pricing(Path("/nonexistent/pricing.json")), {"version": None, "models": {}})
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False) as f:
            f.write("{invalid json")
            bad_path = Path(f.name)
        try:
            self.assertEqual(ge.load_pricing(bad_path), {"version": None, "models": {}})
        finally:
            bad_path.unlink(missing_ok=True)

    def test_usage_missing_returns_none(self):
        tokens = {"input": 1000, "cached": 0, "output": 500, "thinking": 0, "usage_missing": True}
        self.assertIsNone(ge.price(tokens, "test-model", self.pricing))


class QualityAndMetricsTests(unittest.TestCase):
    def test_quality_from_verdict(self):
        # Unswapped
        v = {"scores": {"first": 80, "second": 90}}
        q = ge.quality_from_verdict(v, swapped=False, ref_variant="old", cand_variant="new")
        self.assertEqual(q, {"old": 80.0, "new": 90.0})

        # Swapped
        q_swap = ge.quality_from_verdict(v, swapped=True, ref_variant="old", cand_variant="new")
        self.assertEqual(q_swap, {"old": 90.0, "new": 80.0})

        # Missing scores
        q_missing = ge.quality_from_verdict({}, swapped=False, ref_variant="old", cand_variant="new")
        self.assertEqual(q_missing, {"old": None, "new": None})

        # Out of range scores
        v_out = {"scores": {"first": 150, "second": -10}}
        q_out = ge.quality_from_verdict(v_out, swapped=False, ref_variant="old", cand_variant="new")
        self.assertEqual(q_out, {"old": None, "new": None})

        # Boolean in score
        v_bool = {"scores": {"first": True, "second": 80}}
        q_bool = ge.quality_from_verdict(v_bool, swapped=False, ref_variant="old", cand_variant="new")
        self.assertEqual(q_bool, {"old": None, "new": 80.0})

    def test_summarize(self):
        records = [
            {"variant": "baseline", "task_id": "t1", "run_no": 1, "tokens": {"input": 100, "output": 20, "thinking": 0, "usage_missing": False, "breakdown": {"fixed": 100, "skill": 0, "model_replies": 0, "tool_outputs": 0}}, "cost_usd": 0.001, "status": "SUCCESS"},
            {"variant": "new", "task_id": "t1", "run_no": 1, "tokens": {"input": 120, "output": 30, "thinking": 0, "usage_missing": False, "breakdown": {"fixed": 100, "skill": 20, "model_replies": 0, "tool_outputs": 0}}, "cost_usd": 0.002, "status": "SUCCESS"},
            {"variant": "judge_base_new", "task_id": "t1", "run_no": 1, "tokens": {"input": 200, "output": 50, "thinking": 0, "usage_missing": False}, "cost_usd": 0.005, "status": "SUCCESS"},
        ]
        quality = [
            {"task_id": "t1", "run_no": 1, "variant": "baseline", "q": 70.0},
            {"task_id": "t1", "run_no": 1, "variant": "new", "q": 85.0},
        ]
        pass_scores = {"t1": 70}
        summary = ge.summarize(records, quality, pass_scores)
        self.assertEqual(summary["variants"]["baseline"]["tokens_per_sample"], 120)
        self.assertEqual(summary["variants"]["new"]["tokens_per_sample"], 150)
        self.assertEqual(summary["delta_tokens"], 30)
        self.assertEqual(summary["delta_quality"], 15.0)
        self.assertEqual(summary["efficiency"], (15.0 / 30) * 1000)
        self.assertEqual(summary["variants"]["baseline"]["success_rate"], 1.0)
        self.assertEqual(summary["variants"]["new"]["success_rate"], 1.0)
        self.assertEqual(summary["variants"]["new"]["cost_per_success"], 0.002)
        # Judge calls excluded from T and delta_tokens
        self.assertEqual(summary["judge_calls"], 1)
        self.assertEqual(summary["judge_tokens"], 250)
        self.assertEqual(summary["judge_cost"], 0.005)

    def test_summarize_unpriced_and_zero_successes(self):
        records = [
            {"variant": "new", "task_id": "t1", "run_no": 1, "tokens": {"input": 100, "output": 20, "thinking": 0, "usage_missing": False}, "cost_usd": None, "status": "SUCCESS"},
        ]
        quality = [
            {"task_id": "t1", "run_no": 1, "variant": "new", "q": 50.0},
        ]
        pass_scores = {"t1": 70}
        summary = ge.summarize(records, quality, pass_scores)
        self.assertIsNone(summary["variants"]["new"]["cost"])
        self.assertIsNone(summary["variants"]["new"]["cost_per_success"])
        self.assertEqual(summary["variants"]["new"]["success_rate"], 0.0)

    def test_recommend_decision_table(self):
        # 1. INSUFFICIENT_DATA (< 3 paired samples)
        s1 = {"paired_samples": 2, "delta_quality": 15.0, "delta_tokens": 5000}
        self.assertEqual(ge.recommend(s1)[0], "INSUFFICIENT_DATA")

        # 2. REGRESSION (delta_quality <= 0)
        s2 = {"paired_samples": 3, "delta_quality": 0.0, "delta_tokens": 5000}
        self.assertEqual(ge.recommend(s2)[0], "REGRESSION")
        s2_neg = {"paired_samples": 3, "delta_quality": -5.0, "delta_tokens": 1000}
        self.assertEqual(ge.recommend(s2_neg)[0], "REGRESSION")

        # 3. KEEP (dq >= 10, dt <= 20,000)
        s3 = {"paired_samples": 3, "delta_quality": 10.0, "delta_tokens": 20000}
        self.assertEqual(ge.recommend(s3)[0], "KEEP")
        s3_strong = {"paired_samples": 3, "delta_quality": 15.0, "delta_tokens": 15000}
        self.assertEqual(ge.recommend(s3_strong)[0], "KEEP")

        # 4. OPTIMIZE (dq >= 10, dt > 20,000)
        s4 = {"paired_samples": 3, "delta_quality": 10.0, "delta_tokens": 20001}
        self.assertEqual(ge.recommend(s4)[0], "OPTIMIZE")

        # 5. KEEP (0 < dq < 10, dt <= 10,000)
        s5 = {"paired_samples": 3, "delta_quality": 5.0, "delta_tokens": 10000}
        self.assertEqual(ge.recommend(s5)[0], "KEEP")

        # 6. REVIEW (0 < dq < 10, dt > 10,000)
        s6 = {"paired_samples": 3, "delta_quality": 5.0, "delta_tokens": 10001}
        self.assertEqual(ge.recommend(s6)[0], "REVIEW")


class TelemetryWriterTests(unittest.TestCase):
    def test_record_writes_jsonl_and_flushes(self):
        with tempfile.TemporaryDirectory() as d:
            log_path = Path(d) / "eval-telemetry.jsonl"
            ctx = {"run_id": "test-run", "git_sha": "abc1234", "baseline_ref": "HEAD", "skill": "test-skill"}
            t = ge.Telemetry(log_path, context=ctx)
            rec = t.record(
                variant="new",
                task_id="task1",
                run_no=1,
                turn_no=1,
                model="test-model",
                response={"usageMetadata": {"promptTokenCount": 100, "candidatesTokenCount": 20}},
                skill_sha256="sha-123",
                tools_called=["read_file"],
                tool_output_chars=400,
                breakdown={"fixed": 80, "skill": 20, "model_replies": 0, "tool_outputs": 0},
            )
            # File readable before close:
            lines = log_path.read_text(encoding="utf-8").strip().splitlines()
            self.assertEqual(len(lines), 1)
            parsed = json.loads(lines[0])
            self.assertEqual(parsed["run_id"], "test-run")
            self.assertEqual(parsed["variant"], "new")
            self.assertEqual(parsed["turn_no"], 1)
            self.assertEqual(parsed["tools_called"], ["read_file"])
            self.assertEqual(parsed["tool_output_chars"], 400)
            self.assertEqual(parsed["schema_version"], 1)
            self.assertEqual(parsed["evaluator_version"], "2")
            t.close()

    def test_no_prompts_outputs_or_keys_in_record(self):
        with tempfile.TemporaryDirectory() as d:
            log_path = Path(d) / "eval-telemetry.jsonl"
            t = ge.Telemetry(log_path)
            t.record(
                variant="new",
                task_id="task1",
                run_no=1,
                turn_no=1,
                model="test-model",
                response={"usageMetadata": {"promptTokenCount": 50, "candidatesTokenCount": 10}},
                error="Unauthorized with key=AIzaSySecretFakeKey1234567890abcdef"
            )
            t.close()
            text = log_path.read_text(encoding="utf-8")
            self.assertNotIn("AIzaSySecretFakeKey1234567890abcdef", text)
            self.assertIn("[REDACTED]", text)

    def test_unwritable_path_raises(self):
        unwritable = Path("/nonexistent_dir_cannot_create/telemetry.jsonl")
        with self.assertRaises(OSError):
            ge.Telemetry(unwritable)


class ToolLineRangeTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.ws = Path(self.tmp.name)
        # Create a sample file with 15 lines
        lines = [f"Line {i}\n" for i in range(1, 16)]
        (self.ws / "sample.txt").write_text("".join(lines))

    def tearDown(self):
        self.tmp.cleanup()

    def test_range_5_to_10(self):
        res = ge.execute_tool("read_file", {"path": "sample.txt", "start_line": 5, "end_line": 10}, self.ws)
        self.assertIn("[Lines 5-10 of sample.txt (15 lines)]\n", res)
        self.assertIn("Line 5\n", res)
        self.assertIn("Line 10\n", res)
        self.assertNotIn("Line 4\n", res)
        self.assertNotIn("Line 11\n", res)

    def test_end_beyond_clamps(self):
        res = ge.execute_tool("read_file", {"path": "sample.txt", "start_line": 12, "end_line": 100}, self.ws)
        self.assertIn("[Lines 12-15 of sample.txt (15 lines)]\n", res)
        self.assertIn("Line 15\n", res)

    def test_start_beyond_errors(self):
        res = ge.execute_tool("read_file", {"path": "sample.txt", "start_line": 20, "end_line": 25}, self.ws)
        self.assertIn("ERROR: start_line 20 is past the end (15 lines)", res)

    def test_start_greater_than_end_errors(self):
        res = ge.execute_tool("read_file", {"path": "sample.txt", "start_line": 8, "end_line": 5}, self.ws)
        self.assertIn("ERROR: start_line (8) > end_line (5)", res)

    def test_non_integer_start_end_errors(self):
        res1 = ge.execute_tool("read_file", {"path": "sample.txt", "start_line": "5"}, self.ws)
        self.assertEqual(res1, "ERROR: 'start_line' must be an integer")
        res2 = ge.execute_tool("read_file", {"path": "sample.txt", "end_line": True}, self.ws)
        self.assertEqual(res2, "ERROR: 'end_line' must be an integer")

    def test_path_escape_rejected(self):
        res = ge.execute_tool("read_file", {"path": "../secret.txt"}, self.ws)
        self.assertIn("ERROR: path escapes workspace", res)

    def test_truncation_notice_on_20000_char_cap(self):
        (self.ws / "huge.txt").write_text("A" * 25000)
        res = ge.execute_tool("read_file", {"path": "huge.txt"}, self.ws)
        self.assertIn("[Truncated at 20000 characters; use start_line/end_line]", res)
        self.assertEqual(len(res), 20000 + len("\n[Truncated at 20000 characters; use start_line/end_line]"))


class GeminiGenerateMetaTests(unittest.TestCase):
    def test_meta_latency_and_retries(self):
        class FakeHTTPResponse:
            def __enter__(self): return self
            def __exit__(self, *a): pass
            def read(self):
                return json.dumps({
                    "candidates": [{"content": {"parts": [{"text": "hello"}]}}],
                    "usageMetadata": {"promptTokenCount": 10, "candidatesTokenCount": 5}
                }).encode("utf-8")

        calls = []

        def fake_urlopen(req, timeout=120):
            calls.append(req)
            if len(calls) == 1:
                # 429 on first attempt
                raise urllib.error.HTTPError(req.full_url, 429, "Too Many Requests", {}, io.BytesIO(b""))
            return FakeHTTPResponse()

        with mock.patch("time.sleep"):
            with mock.patch("urllib.request.urlopen", side_effect=fake_urlopen):
                with mock.patch.dict(os.environ, {"GEMINI_API_KEY": "fake-key"}):
                    res = ge.gemini_generate([{"role": "user", "parts": [{"text": "hi"}]}], ROOT)
                    self.assertIn("_meta", res)
                    meta = res["_meta"]
                    self.assertEqual(meta["retries"], 1)
                    self.assertIsInstance(meta["latency_ms"], int)


class RunAgentTests(unittest.TestCase):
    def test_three_turn_run_telemetry(self):
        responses = [
            # Turn 1: model calls tool read_file
            {"candidates": [{"content": {"parts": [{"functionCall": {"name": "read_file", "args": {"path": "sample.txt"}}}]}}],
             "usageMetadata": {"promptTokenCount": 100, "candidatesTokenCount": 20},
             "_meta": {"latency_ms": 10, "retries": 0, "model": "test-model"}},
            # Turn 2: model calls list_files
            {"candidates": [{"content": {"parts": [{"functionCall": {"name": "list_files", "args": {"path": "."}}}]}}],
             "usageMetadata": {"promptTokenCount": 150, "candidatesTokenCount": 25},
             "_meta": {"latency_ms": 12, "retries": 0, "model": "test-model"}},
            # Turn 3: final answer
            {"candidates": [{"content": {"parts": [{"text": "Done!"}]}}],
             "usageMetadata": {"promptTokenCount": 210, "candidatesTokenCount": 15},
             "_meta": {"latency_ms": 15, "retries": 0, "model": "test-model"}},
        ]

        with tempfile.TemporaryDirectory() as d:
            ws = Path(d)
            (ws / "sample.txt").write_text("sample content")
            log_path = ws / "telemetry.jsonl"
            t = ge.Telemetry(log_path, context={"run_id": "r1"})

            with mock.patch.object(ge, "gemini_generate", side_effect=responses):
                final_text, total_in, total_out, turns, first_in = ge.run_agent(
                    "do work", ws, ROOT, skill_content="test skill",
                    telemetry=t, variant="new", task_id="task1", run_no=1, fixed_tokens=80
                )

            t.close()
            self.assertEqual(final_text, "Done!")
            self.assertEqual(first_in, 100)
            self.assertEqual(len(turns), 3)

            records = [json.loads(line) for line in log_path.read_text().strip().splitlines()]
            self.assertEqual(len(records), 3)
            self.assertEqual([r["turn_no"] for r in records], [1, 2, 3])
            for r in records:
                bd = r["tokens"]["breakdown"]
                self.assertEqual(bd["fixed"] + bd["skill"] + bd["model_replies"] + bd["tool_outputs"], r["tokens"]["input"])


class ReportTests(unittest.TestCase):
    def test_synthetic_jsonl_matches_report_totals(self):
        with tempfile.TemporaryDirectory() as d:
            log_path = Path(d) / "eval-telemetry.jsonl"
            pricing = {"models": {"test-model": {"input_per_million": 1.0, "output_per_million": 2.0}}}
            t = ge.Telemetry(log_path, context={"run_id": "test-run", "git_sha": "test-sha"}, pricing=pricing)

            t.record(variant="baseline", task_id="t1", run_no=1, turn_no=1, model="test-model",
                     response={"usageMetadata": {"promptTokenCount": 100, "candidatesTokenCount": 20}},
                     breakdown={"fixed": 100, "skill": 0, "model_replies": 0, "tool_outputs": 0})
            t.record(variant="new", task_id="t1", run_no=1, turn_no=1, model="test-model",
                     response={"usageMetadata": {"promptTokenCount": 130, "candidatesTokenCount": 30}},
                     breakdown={"fixed": 100, "skill": 30, "model_replies": 0, "tool_outputs": 0})
            t.record(variant="judge_base_new", task_id="t1", run_no=1, turn_no=1, model="test-model",
                     response={"usageMetadata": {"promptTokenCount": 200, "candidatesTokenCount": 50}})
            t.close()

            records = ge.read_records(log_path)
            quality = [
                {"task_id": "t1", "run_no": 1, "variant": "baseline", "q": 75.0},
                {"task_id": "t1", "run_no": 1, "variant": "new", "q": 90.0},
            ]
            pass_scores = {"t1": 70}
            summary = ge.summarize(records, quality, pass_scores)
            rec_verdict, rec_reason = ge.recommend(summary)
            report = "\n".join(ge.format_telemetry_report(records, summary, rec_verdict, rec_reason, {"run_id": "test-run"}))

            # Verify token totals in report match records (Invariant 2)
            self.assertIn("120", report)  # baseline input(100) + output(20)
            self.assertIn("160", report)  # new input(130) + output(30)
            self.assertIn("250", report)  # judge tokens: 200 + 50


if __name__ == "__main__":
    unittest.main(verbosity=1)
