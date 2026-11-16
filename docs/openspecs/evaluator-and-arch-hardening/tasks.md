# Implementation Map: Evaluator & Architecture Hardening

**Goal:** Fix critical reliability, security, pricing, and installation safety issues identified in feedback.

---

## Phase 0: Confirmation & Preparation
- [ ] User confirms decisions in `proposal.md` (P0 judge validation fail-closed, default pricing tier, tool limits, install safety).

## Phase 1: P0 Judge Schema Enforcement
- [ ] Update `normalize_verdict()` in `scripts/golden_eval.py` to require a valid `scores` dict with numeric `first` and `second` in `[0, 100]`.
- [ ] Fail closed with `judge_error()` on any missing, non-dict, or out-of-bounds `scores`.
- [ ] Add offline unit tests in `scripts/test_golden_eval.py` testing strict score validation.
- [ ] **Verify:** `python3 scripts/test_golden_eval.py` passes.

## Phase 2: Multi-Tier Pricing Profiles
- [ ] Refactor `evals/pricing.json` to define `tiers` (`free` and `paid`), `default_tier: "paid"`, and official Google AI Studio rates.
- [ ] Update `load_pricing()` in `scripts/golden_eval.py` to accept and resolve the active tier (`--tier` CLI flag or `PRICING_TIER` env var).
- [ ] Record `pricing_tier` in telemetry JSONL records and the Markdown report.
- [ ] Add unit tests in `scripts/test_golden_eval.py` verifying tier resolution and cost calculations.
- [ ] **Verify:** Unit tests pass with non-null costs on `paid` tier and 0.0 costs on `free` tier.

## Phase 3: Tool Limits (`read_files`) & Privacy
- [ ] In `scripts/golden_eval.py`: add per-file truncation notice, 10-file ceiling, and 40,000-character global limit to `read_files`.
- [ ] In `scripts/golden_eval.py`: make `.tmp/` file writing opt-in via `GOLDEN_EVAL_DEBUG=1`, and ensure cleanup in `finally` unless `GOLDEN_EVAL_DEBUG_KEEP=1`.
- [ ] Add unit tests in `scripts/test_golden_eval.py` for `read_files` multi-file truncation and `.tmp/` privacy toggle.
- [ ] **Verify:** Unit tests pass.

## Phase 4: Strict Gate & Installation Safety
- [ ] In `Makefile`: wire `STRICT=1` into `skill-eval` (e.g. `$(if $(STRICT),--strict,)`).
- [ ] In `Makefile`: remove destructive blanket `rm -rf` on user skill directories (`~/.claude/skills`, `~/.gemini/config/skills`, `~/.codex/skills`) in `install-*` targets; switch to safe overwrites via manifest.
- [ ] **Verify:** `make skill-eval SKILL=api-patterns STRICT=1` exits with code 1; `make skill-eval SKILL=api-patterns` exits with code 0.

## Phase 5: Documentation & Gates
- [ ] In `ARCHITECTURE.md`: align directory structure to actual flat layout `skills/<skill-name>/` instead of obsolete `skills/core/`, `tech/`, `process/`.
- [ ] In `docs/quality-gates-summary.md`: rename to "Estimated Token Attribution" and document the heuristic difference-based nature of token splits.
- [ ] Update checksums via `python3 tools/memory_stale.py --root . --update`.
- [ ] Run `make verify` and confirm all gates pass.

---

## Rollback Plan
- [ ] `git restore scripts/golden_eval.py evals/pricing.json Makefile ARCHITECTURE.md docs/quality-gates-summary.md scripts/test_golden_eval.py`

