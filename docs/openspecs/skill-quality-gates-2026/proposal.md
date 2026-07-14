# Proposal: Skill Quality Gates — 5-Tier Verification Pipeline

> Origin: `/brainstorm` session on "how do I know a new/updated skill is better or worse than the old one?" — combined Options A–D into one pipeline, plus a new Contract Test tier.

## Why
Editing a `SKILL.md` changes agent behavior, but the framework has **zero regression protection for prompts**. Today a skill update ships on faith:
- A bad `description` silently kills auto-triggering (the skill never loads again) — nothing detects it.
- A skill can cite files, commands, or agents that don't exist (or stop existing after a refactor like the `project-discovery` → `explore-codebase` rename) — nothing detects it.
- There is no way to compare output quality before/after an edit, so "is it better?" is unanswerable.
- Regressions are discovered days later during real work, with no structured way to record or roll back.

The fix is a tiered pipeline where cost increases per tier, so cheap deterministic checks run always and expensive LLM evals run only when justified:

```
Skill Changed
  → Tier 1: Static Lint        (form — deterministic, 0 tokens)
  → Tier 2: Trigger Test       (discovery — deterministic, 0 tokens)
  → Tier 0: Contract Test      (content claims — deterministic, 0 tokens)
  → Tier 3: Golden Eval        (output quality — LLM A/B, gated)
  → Merge
  → Tier 4: Production Feedback (field telemetry — journal + rollback)
```

## What Changes

### Issue 1: Tier 1 — Static Lint
- New `scripts/skill_lint.py`: validates frontmatter (name matches folder, description non-TODO with trigger keywords, valid `allowed-tools`), required sections present (Core Principles, Anti-Patterns), line/token budget (warn > 150 lines, fail > 300), registry sync (entry exists and matches frontmatter).
- Wired into `make registry` so no skill can be registered unlinted.

### Issue 2: Tier 2 — Trigger Test
- New `tests/skills/trigger_cases.json`: labeled sample prompts → expected skill(s).
- New `scripts/trigger_test.py`: replays cases against `registry.min.json` keyword matching; reports precision/recall per skill and flags keyword collisions between skills.

### Issue 3: Tier 0 — Contract Test
- New `scripts/skill_contract.py`: extracts and verifies the skill's machine-checkable claims — every cited repo path exists, every referenced skill/agent exists in `registry.min.json` / agent definitions, every shell command named in the skill is available (`command -v`), `allowed-tools` covers the tools the body instructs the agent to use (e.g., body says "use git log" → `Bash` must be allowed).
- This tier catches the rot that lint can't see: a skill that is well-formed but lies about the world.

### Issue 4: Tier 3 — Golden Eval (gated, core skills only)
- New `evals/golden/<skill>/` holding 3–5 golden tasks + a scoring rubric per enrolled skill.
- New `scripts/golden_eval.py`: runs each task twice via the **Gemini API** (`gemini-1.5-pro`, `generateContent`, temperature 0, key from `GEMINI_API_KEY` in `.env` or environment) — once with the old skill version (from git), once with the new — scores both against the rubric via LLM-as-judge (same API), and writes a comparison report to `docs/reports/`.
- Opt-in per skill; required only for skills marked `eval: required` in their frontmatter.
- **Known gap (tracked, not yet fixed):** the runner currently sends the skill body as a system instruction with no tool access and no fixture content, so it cannot actually exercise file-reading skills like `explore-codebase`. See `tasks.md` Task 3.1 follow-up.

### Issue 5: Tier 4 — Production Feedback
- New `docs/reports/skill-feedback.md` journal convention: one line per incident (date, skill, what disappointed, severity).
- Rollback procedure documented: every skill version is already in git; `git checkout <sha> -- antigravity/skills/<cat>/<name>` + `make registry`.

### Issue 6: Pipeline Orchestration
- `make skill-check SKILL=<name>` → Tiers 1, 2, 0 (seconds, free). Default gate for every skill edit.
- `make skill-eval SKILL=<name>` → Tier 3 (minutes, costs tokens). Required before merging edits to `eval: required` skills.

## Capabilities

### New Capabilities
- Deterministic 3-gate check (`skill-check`) for every skill change.
- A/B quality comparison (`skill-eval`) answering "better or worse?" with a scored report.
- Trigger precision/recall measurement and keyword-collision detection.
- Structured field-feedback journal + documented rollback.

### Modified Capabilities
- `make registry` now runs Tier 1 lint before generating.
- `scripts/create_skill.py` scaffold gains the sections Tier 1 requires (already present in template) and optional `eval:` frontmatter key.

### Removed Capabilities
- None.

## Impact

| Area | Files Affected |
|------|----------------|
| Scripts | `scripts/skill_lint.py` (new), `scripts/trigger_test.py` (new), `scripts/skill_contract.py` (new), `scripts/golden_eval.py` (new) |
| Test data | `tests/skills/trigger_cases.json` (new), `evals/golden/<skill>/*` (new) |
| Build | `Makefile` (targets `skill-check`, `skill-eval`; `registry` gains lint step) |
| Scaffolder | `scripts/create_skill.py` (optional `eval:` key) |
| Docs | `docs/reports/skill-feedback.md` (new), `ARCHITECTURE.md` (pipeline section), `docs/skills-guide.md` |
