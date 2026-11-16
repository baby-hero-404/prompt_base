# Expected Behavior: Evaluator & Architecture Hardening

## Scenario: Strict Judge Score Validation (P0)
**When:** A judge call returns and the JSON output is parsed by `normalize_verdict()`.
**Then:**
- The verdict object MUST contain:
  1. `status` in `("WORSE", "SAME", "BETTER")`
  2. `score` as a numeric value
  3. `reasoning` as a string
  4. `scores` as a dictionary with keys `"first"` and `"second"` whose values are numeric and within `0 <= score <= 100`.
- If any of these fields are missing, not of the expected type, or outside the range `[0, 100]`, `normalize_verdict()` MUST return `judge_error(reason)` with `status: "ERROR"`.
- It must NEVER silently pass a verdict with missing scores or return `None` quality.

## Scenario: Multi-Tier Pricing Profile (P1)
**When:** `golden_eval.py` calculates call costs with a selected pricing tier (via CLI `--tier <name>` or env `PRICING_TIER`, defaulting to the `default_tier` in `evals/pricing.json`).
**Then:**
- `evals/pricing.json` defines tiers:
  - `free`: All input, cached input, and output rates are `0.0`. Cost evaluates to `0.00000000`.
  - `paid`: Uses official Google AI Studio published rates:
    - `gemini-3.1-flash-lite`: input \$0.25, cached \$0.025, output \$1.50 per million.
    - `gemini-2.5-flash`: input \$0.30, cached \$0.03, output \$2.50 per million.
    - `gemini-2.5-pro`: input \$1.25, cached \$0.125, output \$10.00 per million.
- Telemetry records include `pricing_tier` (e.g. `"paid"` or `"free"`).
- Markdown report includes the active pricing tier and pricing file version.

## Scenario: Bounded and Safe `read_files` Tool Execution (P1)
**When:** An agent calls `read_files` with a list of `paths`.
**Then:**
- **Max Files Limit:** If `len(paths) > 10`, only the first 10 paths are processed. A warning header `[Notice: read_files capped at 10 files; additional files omitted]` is prepended.
- **Per-File Truncation Notice:** If any single file exceeds 20,000 characters, it is cut at 20,000 characters and appended with `\n[Truncated at 20000 characters; use read_file with start_line/end_line]`.
- **Global Character Limit:** The total aggregated character length of the result cannot exceed 40,000 characters. If the combined output exceeds 40,000 characters, it is clamped at 40,000 characters and ends with `\n[TRUNCATED: read_files exceeded maximum total limit of 40,000 characters]`.

## Scenario: Ephemeral Debug Logging (P1)
**When:** `gemini_generate()` sends requests to the API.
**Then:**
- By default, it does NOT write raw `request.md` and `response.md` to disk under `.tmp/`.
- If and only if the environment variable `GOLDEN_EVAL_DEBUG=1` is set, it creates `.tmp/call_xxx/` and writes full debug markdown files.
- On process completion (in `finally`), if `.tmp/` was created, it is completely removed unless `GOLDEN_EVAL_DEBUG_KEEP=1` is explicitly set.

## Scenario: Strict Evaluation Flag in Makefile (P1)
**When:** A developer or CI runs `make skill-eval SKILL=<name> STRICT=1`.
**Then:**
- The Makefile target invokes `golden_eval.py` with `--strict`.
- If the skill has no golden evaluation tasks, the evaluator outputs `NO COVERAGE` and exits with code 1.
- If run without `STRICT=1`, it retains the existing non-blocking behavior (exit 0).

## Scenario: Non-Destructive Manifest-Driven Installation
**When:** Running `make install-claude`, `make install-gemini`, or `make install-codex`.
**Then:**
- Existing user-authored skills (directories in `~/.claude/skills/`, `~/.gemini/config/skills/`, etc., that are NOT part of Prompt Base's tracked repository) MUST NOT be deleted.
- Only the specific Prompt Base skills, agents, workflows, and tools defined in `install.manifest.json` are overwritten/updated.
- The destructive commands `rm -rf ~/.claude/skills`, `rm -rf ~/.gemini/config/skills`, and `rm -rf ~/.codex/skills` are removed.

## Scenario: Documentation & Terminology Sync
**When:** Reading `ARCHITECTURE.md` and `docs/quality-gates-summary.md`.
**Then:**
- `ARCHITECTURE.md` illustrates the actual flat directory layout (`skills/<skill-name>/`).
- Prompt input attribution is accurately described as "Estimated Token Attribution" with documentation clarifying that `model_replies` and `tool_outputs` are derived splits from turn differences.

---

## Failure Scenarios

### Failure Scenario: Judge Omission of Scores
**When:** The LLM judge returns valid JSON with `status: "BETTER"`, but omits `"scores"` or provides non-numeric values.
**Then:** `normalize_verdict()` immediately returns `{"status": "ERROR", "score": 0, "reasoning": "Judge returned invalid or missing scores"}`. The evaluation task records an error and aborts to save quota.

### Failure Scenario: Unknown Pricing Tier
**When:** A user specifies `--tier custom_tier` but `custom_tier` does not exist in `evals/pricing.json`.
**Then:** `golden_eval.py` logs a warning, falls back to `default_tier` (or null if absent), and reports costs as `UNPRICED`.

---

## Invariants
1. **Validation Fail-Closed:** A judge verdict without valid scores is an ERROR, never a silent pass.
2. **Quota Protection:** All tool limiters (`read_file` line ranges, `read_files` 40K global cap) prevent unbounded context explosions.
3. **Data Privacy:** Evaluation runs do not leave plaintext prompt/response artifacts on disk unless debug mode is explicitly opted-in.
4. **User Data Integrity:** `make install` never clobbers or deletes unmanaged user customizations.

