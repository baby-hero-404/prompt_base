# Specs: Skill Quality Gates — 5-Tier Verification Pipeline

## Added Requirements

### REQ-001: Tier 1 — Static Lint
> ❌ Status: Not Started

**Scenario:**
- WHEN `scripts/skill_lint.py` runs against a skill whose `description` still contains `TODO`, whose `name` mismatches its folder, or whose body exceeds 300 lines
- THEN the script exits non-zero naming the exact violation and file
- AND `make registry` refuses to regenerate until lint passes
- AND a skill within budget with all required sections passes silently

### REQ-002: Tier 2 — Trigger Test
> ❌ Status: Not Started

**Scenario:**
- WHEN `scripts/trigger_test.py` replays `tests/skills/trigger_cases.json` against `registry.min.json`
- THEN it reports per-skill precision and recall
- AND exits non-zero if either falls below the configured threshold (default 0.9)
- AND it flags any keyword claimed by two or more skills as a collision warning

### REQ-003: Tier 0 — Contract Test
> ❌ Status: Not Started

**Scenario:**
- WHEN a skill cites a repo path that does not exist (e.g., after a rename), references an unregistered skill/agent, or instructs using a tool absent from its `allowed-tools`
- THEN `scripts/skill_contract.py` exits non-zero listing each broken claim with its line number
- AND fenced example blocks and `<!-- contract:ignore -->` regions are skipped
- AND a skill whose every claim verifies passes silently

### REQ-004: Tier 3 — Golden Eval A/B
> ✅ Status: Done — Grounding fixed (real tool access + fixture + judge_model wiring). Live confirmation run passed successfully using Gemini 2.5 Flash via paid-tier API key.

**Scenario:**
- WHEN `make skill-eval SKILL=<name>` runs on a skill with golden tasks under `evals/golden/<name>/`
- THEN each task executes twice via the Gemini API (`gemini-1.5-pro`, temperature 0, `GEMINI_API_KEY` from `.env`/env) — old version (from git HEAD) and new version (working tree)
- AND both outputs are scored against the task rubric by the judge (same API) at temperature 0
- AND a report `docs/reports/EVAL-<skill>-<date>.md` is written with per-task scores and a `BETTER | SAME | WORSE` verdict
- AND the command exits non-zero only on `WORSE`
- **AND** (not yet true) the model under test has real tool access (Read/Glob/Grep) against a non-empty fixture under `evals/golden/fixtures/`, so file-reading skills produce grounded, non-empty output — the 2026-07-14 run of `explore-codebase` returned empty output on all 3 tasks, confirming this gap
- **AND** (not yet true) the live `SKILL.md` is never mutated in place — old/new content must be run from a temp copy with the original always restored via `try/finally`

### REQ-005: Eval Enrollment Gate
> ❌ Status: Not Started

**Scenario:**
- WHEN a skill's frontmatter contains `eval: required`
- AND its `SKILL.md` changed since HEAD
- THEN `make skill-check` reminds that `skill-eval` must pass before merge
- AND skills without the key are never blocked on Tier 3

### REQ-006: Tier 4 — Production Feedback Journal
> ❌ Status: Not Started

**Scenario:**
- WHEN a skill disappoints during real usage
- THEN a one-line entry (date, skill, incident, severity, action) is appended to `docs/reports/skill-feedback.md`
- AND the rollback procedure (`git checkout <sha> -- <skill-path>` + `make registry && make install`) is documented in the same file's header

### REQ-007: Pipeline Orchestration
> ❌ Status: Not Started

**Scenario:**
- WHEN `make skill-check SKILL=explore-codebase` runs
- THEN Tiers 1, 2, and 0 execute in order, stopping at the first failure
- AND the whole command completes in under 10 seconds with zero LLM calls
- AND `make skill-check` without `SKILL=` checks every registered skill

## Modified Requirements

### REQ-M01: Scaffolder Seeds the Pipeline
> ❌ Status: Not Started

**Scenario:**
- WHEN `scripts/create_skill.py` scaffolds a new skill
- THEN it prompts for (or accepts via flag) one seed trigger case appended to `tests/skills/trigger_cases.json`
- AND the generated frontmatter supports an optional `eval:` key

## Removed Requirements
- None.
