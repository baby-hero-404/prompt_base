# Proposal: Token Telemetry & Evaluator Enhancement (golden_eval.py)

## Problem
`scripts/golden_eval.py` can say whether a new skill version is WORSE, SAME or BETTER, but not what the skill costs or how much it helps. Concretely:

1. **Token totals only.** The report sums input and output tokens per variant and lists per-turn input/output for the first New run. It does not say which part of the prompt the tokens went to (instructions, skill body, model replies, tool output), and judge calls are not counted at all.
2. **No cost.** There is no pricing, no cached-token discount, and thinking tokens (`thoughtsTokenCount`), which are billed as output, are ignored.
3. **No absolute quality.** The judge returns a relative verdict (A vs B). There is no per-output score, so "quality gain over baseline" (ΔQ) cannot be computed.
4. **No efficiency signal.** Without ΔQ and ΔT (token delta vs no skill) there is no basis for keep / optimize / review decisions.

What is *not* a defect: `run_agent()` re-sends the system instruction (global instruction + skill body) and the growing `contents` on every turn. That is how every stateless chat API works, and real agents (Claude Code, Gemini CLI, Codex) do the same. The input total over N turns grows roughly quadratically for the same reason. The evaluator must **measure** this faithfully, not change it, or the measurement stops representing real use.

## Goal
1. Write one structured JSONL record per API call (agent turns and judge calls), flushed immediately.
2. Attribute each agent call's input tokens to fixed prompt, skill body, previous model replies, and previous tool output, using the provider's own counts (no local tokenizer, no extra API calls).
3. Compute cost per call from a versioned pricing file, including cached input and thinking tokens; a model without a price is reported as unpriced, never given an invented rate.
4. Add an absolute 0–100 quality score per output, so ΔQ, ΔT, efficiency, and cost per success can be computed.
5. Print an advisory recommendation (KEEP / OPTIMIZE / REVIEW / REGRESSION / INSUFFICIENT_DATA) that never changes the exit code.

## Success
- Every run writes `docs/reports/eval-telemetry-<run_id>.jsonl`; a run aborted on turn 8 still holds turns 1–7.
- The Markdown report shows: token breakdown by source, agent cost vs judge cost, ΔQ, ΔT, efficiency, cost per success, and the recommendation, and links the JSONL file.
- Report totals are computed by reading the JSONL back, so the two can never disagree.
- Offline unit tests cover attribution, pricing, scoring, metrics, decision table, and JSONL writing; `make test` and `make verify` pass.
- No new dependency (standard library + existing `yaml`), no new network endpoint.

## Assumptions
- Gemini `usageMetadata` returns `promptTokenCount` (includes cached tokens), `candidatesTokenCount`, and optionally `cachedContentTokenCount` and `thoughtsTokenCount`. Verify against the API reference during Phase 1; any field may be absent.
- Within one variant, `contents` is append-only between turns, so the growth of `promptTokenCount` from turn k−1 to turn k equals the tokens appended in between.
- Baseline and New use the same prompt, tools, global instruction, and model, so their turn-1 difference is the skill body.

## Decisions
| Decision | Choice | Rejected alternative and why |
|---|---|---|
| Token attribution | Differences of provider counts (see design.md §2) | Character ratio (≈4 chars/token): error is unknown and varies by language and code; normalizing to the total hides the error instead of bounding it. `countTokens` API: exact but adds calls under a 15 RPM limit; kept as possible later option |
| Quality score | Extend the judge template so the same call also returns a 0–10 score per rubric item for each output | A separate scoring call per output: doubles judge cost |
| Unknown model price | `cost_usd: null`, report "UNPRICED" | Default fallback rate: produces numbers that look real and are not |
| Recommendation | Advisory text only | Gating on it: thresholds are heuristics and samples are small (2 tasks repo-wide) |
| Telemetry location | `docs/reports/*.jsonl`, gitignored | Committing traces: grows the repository with machine data |

## Decisions needing your confirmation
1. **Judge template change.** Adding absolute scores changes the judge prompt, so verdicts from before and after the change are not strictly comparable. Default: accept, and record `evaluator_version` in every record.
2. **Prices.** `evals/pricing.json` ships with structure and `source`/`retrieved` fields but prices must be copied by you from the official pricing page. Default: models without a price stay UNPRICED. No price is invented in this change.
3. **`read_file` behavior.** Line ranges (`start_line`, `end_line`) are added as optional parameters. The existing 20,000-character cap stays; it is not replaced by a 500-line cap, because changing the cap changes agent behavior for every variant and breaks comparison with earlier reports. Default: optional ranges + a truncation notice only.

## Trade-offs
- Attribution by difference is exact for the fixed prompt and the skill body, but the split of each turn's growth into "model reply" and "tool output" assumes a reply re-counts as input at about its `candidatesTokenCount`. The residual goes to tool output and is clamped at zero; records mark this field `derived`.
- The skill-body figure needs a baseline run. With `--fast` it is reported as unknown.
- Two tasks in the whole repository (2/63 skills covered) cannot support per-skill ROI decisions. The recommendation reports INSUFFICIENT_DATA until enough samples exist; writing golden tasks is a separate change.

## Non-goals
- A web dashboard (Phase 3 of the feedback).
- Telemetry from live Claude Code / Gemini CLI / Codex sessions.
- Editing skills automatically from eval results.
- Changing the agent loop, system instruction, or history handling to save tokens.

## Out of Scope
- New golden tasks or a benchmark dataset.
- Tools that edit files or run tests inside the evaluator sandbox.
- Replacing the existing `.tmp/` request/response Markdown dumps (debug output, stays as is).

## Impact

### Components
`scripts/golden_eval.py`, `evals/golden/judge_template.txt`, `evals/pricing.json`, `docs/reports/`, `.gitignore`

### Files
- **Modify:** `scripts/golden_eval.py`, `evals/golden/judge_template.txt`, `scripts/test_golden_eval.py`, `.gitignore`, `docs/quality-gates-summary.md`
- **Create:** `evals/pricing.json`
- **Generated at run time (gitignored):** `docs/reports/eval-telemetry-<run_id>.jsonl`

### Public API
None (internal evaluation tooling).

### Backward Compatibility
- CLI unchanged: positional `skill_name`, `--prompt`, `--fast`, `--baseline`, `--runs`, `--strict`, `--coverage`. Exit codes unchanged; the recommendation never affects them.
- Existing task YAML files work unchanged. New optional field `pass_score` (default 70).
- A judge reply without the new score fields is still a valid verdict; ΔQ for that sample is "n/a".
