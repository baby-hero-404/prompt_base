# Expected Behavior: Token Telemetry & Evaluator Enhancement

Terms: a **variant** is `baseline` (no skill), `old` (skill at `--baseline` ref) or `new` (working copy). A **sample** is one (task, run) pair. **Agent calls** are calls made by `run_agent()`; **judge calls** are calls made by `compare()`.

## Scenario: One record per API call
**When:** any call to `gemini_generate()` returns, successfully or not.
**Then:** one JSON line is appended to `docs/reports/eval-telemetry-<run_id>.jsonl` and flushed before the next call starts. Fields:

| Field | Type | Notes |
|---|---|---|
| `schema_version` | int | Starts at 1 |
| `evaluator_version` | str | Bumped when the judge template or scoring changes |
| `run_id` | str | `<UTC yyyymmddThhmmss>-<4 hex>`; one per process |
| `timestamp` | str | ISO-8601 UTC |
| `git_sha` | str | `HEAD` of the repository at run time |
| `baseline_ref` | str | Value of `--baseline` |
| `skill` | str | |
| `skill_sha256` | str \| null | Hash of the skill body used by this variant; null for `baseline` and judge |
| `task_id` | str | Task file name, or `inline_task` |
| `variant` | str | `baseline`, `old`, `new`, `judge_old_new`, `judge_base_new` |
| `run_no` | int | 1-indexed |
| `turn_no` | int | 1-indexed; always 1 for judge calls |
| `model` | str | |
| `status` | str | `SUCCESS` or `ERROR` |
| `error` | str \| null | First 300 characters of the error; never request headers or bodies |
| `latency_ms` | int | Time of the successful HTTP attempt only; excludes the rate-limit sleep and retry waits |
| `retries` | int | Number of 429 retries before the final attempt |
| `tokens` | object | See below |
| `cost_usd` | float \| null | null when the model has no price |
| `tools_called` | list[str] | Tool names requested in this response |
| `tool_output_chars` | int | Characters returned by the tools executed after this response |

`tokens`: `input` (`promptTokenCount`), `cached` (`cachedContentTokenCount`, 0 if absent), `output` (`candidatesTokenCount`), `thinking` (`thoughtsTokenCount`, 0 if absent), `usage_missing` (bool), and for agent calls `breakdown` (next scenario).

**Never in a record:** prompts, skill text, model output, tool output, file contents, environment values, API keys.

## Scenario: Input attribution for agent calls
**When:** an agent call for variant V, sample S, turn k succeeds with usage present.
**Then:** `tokens.breakdown` holds four non-negative integers whose sum equals `tokens.input` exactly:

| Field | Turn 1 | Turn k > 1 |
|---|---|---|
| `fixed` | `baseline` turn-1 input of sample S (global instruction, user prompt, tool declarations) | same as turn 1 |
| `skill` | V's turn-1 input minus `fixed`; 0 for `baseline` | same as turn 1 |
| `model_replies` | 0 | previous value + min(growth, previous turn's `output`) |
| `tool_outputs` | 0 | previous value + max(0, growth − previous turn's `output`) |

where growth = input at turn k − input at turn k−1.

- If the `baseline` turn-1 input for S is unknown (`--fast`, or baseline failed), `fixed` and `skill` are merged into `fixed` and `breakdown.skill_known` is false.
- If growth is negative (provider counting changed), all of turn k's input above `fixed + skill` is put into `tool_outputs`, and `breakdown.derived_clamped` is true.
- `model_replies` and `tool_outputs` are marked derived in the report; `fixed` and `skill` are exact differences of provider counts.

## Scenario: Cost per call
**When:** a record is written and the model is in `evals/pricing.json`.
**Then:**
- `cost_usd = (input − cached) × input_rate + cached × cached_input_rate + (output + thinking) × output_rate`, rates per token.
- If the model has no `cached_input_per_million`, cached tokens are charged at `input_rate`.
- The pricing file's `version` is shown in the report.

## Scenario: Absolute quality score
**When:** a judge call returns.
**Then:** the verdict object holds, in addition to `status`, `score`, `reasoning`:
- `scores`: `{"first": <0–100>, "second": <0–100>}`, computed by the judge as the rubric-weighted mean of 0–10 item scores × 10.
- `compare()` maps `first`/`second` back to reference/candidate when the order was swapped, and attaches `quality` = `{ "<reference variant>": q, "<candidate variant>": q }`.
- A missing or out-of-range `scores` field does **not** make the verdict an ERROR; the sample's quality is "n/a" and the verdict logic is unchanged.

`Q(variant)` = mean of that variant's quality over all samples where it was scored. A `new` output is scored twice per sample (once in each judge call); its quality for that sample is the mean of the two.

## Scenario: Efficiency metrics
**When:** all tasks finish and at least one sample has quality for both `baseline` and `new`.
**Then:** the report shows, per variant and in total:

| Metric | Definition |
|---|---|
| `T(variant)` | Mean agent tokens per sample: sum over that sample's agent calls of `input + output + thinking` |
| ΔT | `T(new) − T(baseline)` |
| ΔQ | `Q(new) − Q(baseline)`, over samples that have both |
| Efficiency | `ΔQ / ΔT × 1000`; shown as "saves tokens" when ΔT ≤ 0 and ΔQ ≥ 0 |
| Success rate | Share of samples whose quality ≥ task `pass_score` (default 70) |
| Cost per success | Agent `cost_usd` of the variant / its successful samples; "n/a" with 0 successes or any unpriced call |
| Eval cost | Judge `cost_usd`, shown apart from agent cost |

Judge tokens never enter T, ΔT, or cost per success.

## Scenario: Advisory recommendation
**When:** the metrics above are computed.
**Then:** one recommendation is printed, by the first matching row:

| # | Condition | Recommendation |
|---|---|---|
| 1 | Fewer than 3 samples with quality for both `baseline` and `new` | INSUFFICIENT_DATA |
| 2 | ΔQ ≤ 0 | REGRESSION (no better than using no skill) |
| 3 | ΔQ ≥ 10 and ΔT ≤ 20,000 | KEEP |
| 4 | ΔQ ≥ 10 | OPTIMIZE (helps, but expensive) |
| 5 | ΔT ≤ 10,000 | KEEP (small gain, cheap) |
| 6 | otherwise | REVIEW (small gain, expensive) |

Thresholds are constants at the top of `golden_eval.py`. The recommendation never changes the exit code.

## Scenario: Line ranges in read tools
**When:** the agent calls `read_file` with optional `start_line` and/or `end_line` (1-indexed, inclusive).
**Then:**
- Only those lines are returned, after a header `[Lines a-b of <path> (<total> lines)]`.
- `start_line` beyond the end returns `ERROR: start_line <n> is past the end (<total> lines)`; `end_line` beyond the end is clamped; `start_line > end_line` returns an error.
- Without a range the behavior is unchanged, except that output cut at the existing 20,000-character cap ends with `[Truncated at 20000 characters; use start_line/end_line]`.
- `read_files` is unchanged.

## Failure Scenario: Usage metadata missing
**When:** a successful response has no `usageMetadata` or no `promptTokenCount`.
**Then:** counts are 0, `tokens.usage_missing` is true, no breakdown is written, `cost_usd` is null, and the report flags the sample as incomplete. No local estimate is substituted.

## Failure Scenario: Model has no price
**When:** the model is not in `evals/pricing.json`, or the file is missing or invalid.
**Then:** `cost_usd` is null, the console prints `[WARN] No price for model <name> in evals/pricing.json; cost is UNPRICED.` once per model, and the report shows UNPRICED instead of a number. The run continues.

## Failure Scenario: API error or abort
**When:** a call fails after retries, or the run aborts on a FATAL ERROR.
**Then:** the failed call is recorded with `status: "ERROR"` before `sys.exit`. All earlier records are already on disk.

## Failure Scenario: Telemetry cannot be written
**When:** the JSONL file cannot be opened or written.
**Then:** the run stops with exit 1 before the first API call if the file cannot be opened; a later write failure prints an error and exits 1. Quota is not spent on a run that cannot record its cost.

## Invariants
1. **Durability:** each record is flushed before the next API call.
2. **Single source:** every token and cost figure in the Markdown report is computed by reading the run's JSONL file back.
3. **Judge isolation:** judge calls are recorded and summed separately from agent calls.
4. **Exact attribution:** when `breakdown` is present, its four fields sum to `tokens.input`.
5. **Unchanged verdicts:** WORSE / SAME / BETTER / ERROR / UNVERIFIED logic and exit codes are unchanged by this work.
6. **Unchanged agent loop:** the system instruction, `contents`, tools, and prompts sent to the model are unchanged, except for the optional `read_file` parameters.

## Rules
- Standard library plus the existing `yaml` only. No new network endpoint, no tokenizer download.
- Existing CLI flags and exit codes stay compatible.
- `docs/reports/` is gitignored.

## Constraints
- No additional API calls: attribution uses usage from calls already made; scoring reuses the existing judge calls.
- Attribution and cost run in O(number of turns) per sample with no file reads.
