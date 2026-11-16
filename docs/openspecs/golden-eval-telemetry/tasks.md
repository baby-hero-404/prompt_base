# Implementation Map: Token Telemetry & Evaluator Enhancement

**Goal:** per-call JSONL telemetry, exact prompt attribution, cost, absolute quality score, efficiency metrics and an advisory recommendation in `scripts/golden_eval.py`, without changing the agent loop, verdicts, or exit codes.
**Tech stack:** Python 3 standard library, existing `yaml`, Gemini REST API.
**Tests:** `scripts/test_golden_eval.py` (`unittest`, offline, run by `make test`).

---

## Phase 0: Confirm and prepare
- [x] User confirms the three items in proposal.md "Decisions needing your confirmation".
- [x] Check the current Gemini `usageMetadata` field names (`promptTokenCount`, `candidatesTokenCount`, `cachedContentTokenCount`, `thoughtsTokenCount`) against the API reference; record the result in design.md §2.
- [x] Add `docs/reports/` to `.gitignore`.
**Verify:**
- [x] `git check-ignore docs/reports/x.jsonl` prints the path.

## Phase 1: Pure functions (test first)
### 1.1 Usage and attribution
- [x] Tests: `usage_of` with full usage, missing usage, missing optional fields.
- [x] Tests: `attribute` for 1 turn; 3 turns; baseline (skill 0); `fixed=None`; negative growth (clamped flag); sum equals input on every turn.
- [x] Implement `usage_of`, `attribute`.

### 1.2 Pricing
- [x] Create `evals/pricing.json` with repository model ids and `null` prices.
- [x] Tests: priced model; model with null prices; unknown model; missing file; invalid JSON; cached rate absent (falls back to input rate); thinking tokens charged as output.
- [x] Implement `load_pricing`, `price`, one warning per unpriced model.

### 1.3 Quality and metrics
- [x] Tests: `quality_from_verdict` unswapped, swapped, missing `scores`, out-of-range score.
- [x] Tests: `summarize` for T, ΔT, Q, ΔQ, success rate, cost per success with 0 successes and with an unpriced call; judge tokens excluded from T.
- [x] Tests: `recommend`, one case per decision-table row, plus a boundary case on each threshold.
- [x] Implement `quality_from_verdict`, `summarize`, `recommend`; thresholds as module constants.

**Verify:**
- [x] `python3 scripts/test_golden_eval.py` passes.

## Phase 2: Telemetry writer
- [x] Tests: `record` writes one valid JSON line and flushes (file readable before `close`); fields match specs.md; no prompt, output or key text in the line (fake key in error).
- [x] Tests: unwritable path raises before any API call.
- [x] Implement `Telemetry`.
**Verify:**
- [x] Tests pass.

## Phase 3: Wire into the evaluator
### 3.1 `gemini_generate`
- [x] Return `_meta` (latency of the final attempt, retries, model); strip it in callers.
- [x] Test with a mocked `urlopen`: 429 once then success gives `retries == 1`; latency excludes the sleep (patch `time.sleep`).

### 3.2 `run_agent`
- [x] Accept `telemetry`, `variant`, `task_id`, `run_no`, `fixed_tokens`; record each turn with tools, tool output characters, breakdown; return the baseline's turn-1 input so `main()` can pass it to `old`/`new`.
- [x] Record the failing call before returning `ERROR:`.
- [x] Test with mocked `gemini_generate`: 3-turn run writes 3 records with `turn_no` 1..3 and exact breakdown sums.

### 3.3 `compare` / `judge_results`
- [x] Record judge calls as `judge_old_new` / `judge_base_new`.
- [x] Extend `judge_template.txt` (design.md §4.4); set `EVALUATOR_VERSION = 2`.
- [x] Return quality per variant, mapped back on swap.
- [x] Test: swapped order maps scores to the right variants; existing verdict tests still pass unchanged.

### 3.4 `read_file` line ranges
- [x] Add `start_line`, `end_line` to the declaration and executor; truncation notice on the 20,000-character cap.
- [x] Tests: range 5–10 returns 6 lines and the header; end beyond file clamps; start beyond file errors; start > end errors; non-integer errors; path escape still rejected.

**Verify:**
- [x] All tests pass; `python3 scripts/golden_eval.py --coverage` and the no-coverage path behave as before.

## Phase 4: Report
- [x] Build the report from the JSONL file (read back) plus quality data; add the five sections in design.md §4.7.
- [x] Test: a synthetic JSONL produces a report whose token totals equal the sum of the records (invariant 2).
**Verify:**
- [ ] One real run by the user: `make skill-eval SKILL=explore-codebase` (spends API quota; the agent does not run it). Check the JSONL and report sections.

## Phase 5: Documentation and gates
- [x] Update `docs/quality-gates-summary.md`: telemetry file, fields, cost, metrics, recommendation is advisory, prices are user-maintained.
- [x] Update `ARCHITECTURE.md` if a new file is added (`evals/pricing.json`).
- [x] `python3 tools/memory_stale.py --root . --update` if a tracked trigger changed.
- [x] `make verify` exits 0.

---

## Rollback Plan
- [ ] Before commit: `git restore scripts/golden_eval.py evals/golden/judge_template.txt scripts/test_golden_eval.py .gitignore docs/quality-gates-summary.md` and delete `evals/pricing.json`.
- [ ] After commit: `git revert <commit>`.
- [ ] Telemetry files under `docs/reports/` are gitignored run output; deleting them affects nothing else.
