# Proposal: Evaluator & Architecture Hardening

## Problem
A deep audit of the evaluator, quality gates, and system architecture revealed several critical correctness, safety, and reliability gaps:
1. **Schema Mismatch & Loose Validation (P0)**: The judge template requested relative scoring while the evaluator expected absolute scores; additionally, `normalize_verdict()` does not validate the presence and range of the `scores` object (`first` and `second`), allowing judge calls with missing scores to pass and silently pollute quality metrics with `None`.
2. **Unpriced Telemetry & Inflexible Pricing (P1)**: `evals/pricing.json` models were initialized with `null`, resulting in constant `UNPRICED` reports. Furthermore, there is no distinction between Google AI Studio Free Tier ($0) and Paid Tier ($0.25/$1.50).
3. **Soft Quality Gates (P1)**: `make skill-eval` does not pass `--strict`, meaning unverified skills (no golden tasks) exit 0 and appear as successful checks in pipelines.
4. **Unbounded `read_files` (P1)**: `read_files` truncated individual files at 20,000 characters without a truncation notice and had no global character/file cap, risking payloads over 400,000 characters (~100K tokens) in a single tool call.
5. **Debug Artifact Leakage (P1)**: `gemini_generate()` unconditionally persisted raw `request.md` and `response.md` (containing full system instructions, prompts, and tool history) to `.tmp/` on every call, leaving sensitive data permanently on disk after evaluation.
6. **Destructive Installation (Architecture Risk)**: `Makefile` install targets (`install-claude`, `install-gemini`, `install-codex`) executed blanket `rm -rf` on entire user directories (`~/.claude/skills`, `~/.gemini/config/skills`, etc.), destroying any user-created custom skills or agents not tracked by Prompt Base.
7. **Documentation Drift**: `ARCHITECTURE.md` depicted a legacy hierarchical tree (`skills/core/`, `tech/`, `process/`) that diverged from the flat `skills/<name>/` reality, and `docs/quality-gates-summary.md` claimed "Exact breakdown" for an attribution model that is inherently derived/estimated.

## Goal
Harden the testing and runtime infrastructure across 5 pillars:
1. **P0 Contract Enforcement**: Validate `scores` strictly in judge verdicts (`first` and `second` within [0, 100]), failing closed with `judge_error` if missing.
2. **Tiered Pricing**: Support `free` ($0) and `paid` tiers with official rates in `evals/pricing.json`, selectable via `--tier` / `PRICING_TIER`, and recorded in telemetry.
3. **Strict Quality Gates & Safe Tools**: Wire `--strict` through `make skill-eval STRICT=1`, enforce a global 40,000-char / 10-file cap on `read_files` with explicit truncation warnings, and silence disk logging to `.tmp/` by default (opt-in via `GOLDEN_EVAL_DEBUG=1`).
4. **Non-Destructive Manifest Installation**: Refactor `make install-*` targets to synchronize managed files instead of blanket `rm -rf` of entire skill directories.
5. **Accurate Documentation**: Realign `ARCHITECTURE.md` directory trees to the flat layout and rebrand prompt attribution to "Estimated / Derived Token Attribution".

## Success
- A judge response omitting `"scores"` or with invalid numbers is caught immediately as an `ERROR` verdict (never silent `None`).
- Running `golden_eval.py` produces non-null USD costs when using the paid tier profile.
- A skill without golden tasks fails `make skill-eval SKILL=... STRICT=1` with exit code 1.
- `read_files` with 15 large files returns at most 10 files and 40,000 total characters with clear truncation notices.
- `.tmp/` is empty after an eval run unless `GOLDEN_EVAL_DEBUG=1` is specified.
- Running `make install` preserves untracked user skills in `~/.claude/skills` and `~/.gemini/config/skills`.
- `make verify` and offline unit tests pass 100%.

## Assumptions
- Standard Python 3 standard library remains the sole dependency for evaluator scripts (no external packages beyond `yaml`).
- Model pricing defaults to the standard published Google AI Studio rates for Gemini 3.1 Flash-Lite, Gemini 2.5 Flash, and Gemini 2.5 Pro.

## Decisions
| Decision | Rationale |
|---|---|
| Strict `scores` validation in `normalize_verdict` | If a judge fails to score an output, treating it as `SAME` or `None` distorts benchmark averages. Failing closed as `ERROR` prevents silent regressions. |
| Two-tier pricing profile (`free` / `paid`) | Free tier users see accurate $0.00 cost; paid tier users see realistic USD consumption based on official Google AI Studio rates. |
| Global character cap (`40,000` chars) on `read_files` | Prevents runaway context expansion when agents read multiple large files in one turn. |
| Opt-in debug logs (`GOLDEN_EVAL_DEBUG=1`) | Prevents accidental persistence of confidential code/prompts in `.tmp/` during standard evaluation runs. |
| Managed installation via manifest | Closes the data-loss risk where `make install` deleted existing user-authored skills. |

## Trade-offs
- Strict judge scoring will fail older tasks if an external custom judge prompt does not produce the `"scores"` key. (Mitigated by updating `judge_template.txt`).
- `read_files` truncation cap might force agents to make an additional tool turn for very large codebases, but protects against context exhaustion.

## Non-goals
- Building a full code execution sandbox for action/writing skills (e.g. Docker container runner for `golang-best-practices`). That belongs to a dedicated Phase 2 benchmark sandbox project.
- Replacing static keyword matching in `trigger_test.py` with an LLM semantic judge (that is out of scope for a fast local linter gate).

## Out of Scope
- Cloud telemetry streaming (LangSmith/Phoenix) or remote database storage.
- Real-time token counting per sub-token during API streaming.

## Decisions Needing Your Confirmation
1. **Judge Score Enforcement (P0)**: Should missing or invalid `scores` from the LLM judge immediately fail the run as `ERROR` (strict fail-closed), or retry the judge prompt once before failing?
2. **Default Pricing Tier**: Should the default tier in `evals/pricing.json` be set to `"free"` ($0.00) or `"paid"` (official Google AI Studio rates)?
3. **`read_files` Global Limit**: Is `40,000` characters (~10,000 tokens) across a maximum of `10` files appropriate as the safety ceiling?
4. **Install Cleanup Scope**: In `make install-*`, should we clean up only files explicitly listed in Prompt Base's `install.manifest.json` (leaving user files untouched)?

---

## Impact

### Components
- `scripts/golden_eval.py`: Validator, pricing loader, tool executor, privacy guard.
- `evals/pricing.json`: Pricing profiles and tier definitions.
- `Makefile`: Strict evaluation flags, coverage target, non-destructive installation.
- `ARCHITECTURE.md` & `docs/quality-gates-summary.md`: Accurate structure and terminology.

### Files
- `scripts/golden_eval.py`
- `scripts/test_golden_eval.py`
- `evals/pricing.json`
- `Makefile`
- `ARCHITECTURE.md`
- `docs/quality-gates-summary.md`
- `docs/ai/manifest.json`

### Backward Compatibility
- Existing CLI flags (`--baseline`, `--runs`, `--fast`, `--strict`) retain full compatibility.
- Telemetry format version remains compatible with Schema Version 1, adding optional `tier` field.

