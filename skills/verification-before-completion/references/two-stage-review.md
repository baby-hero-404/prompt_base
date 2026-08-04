# Code Review: Two-Stage Process & Dispatch

## Overview

Dispatch a code reviewer to catch issues before they cascade. The reviewer gets precisely crafted context — never your session's history.

**Core principle:** Review early, review often. Two stages: spec compliance first, then code quality.

## When to Request Review

**Mandatory:**
- After each task in subagent-driven development
- After completing major feature
- Before merge to main

## Two-Stage Review Process

```
Stage 1: SPEC COMPLIANCE
  → Did we build what was requested? Nothing more, nothing less?
  → ✅ Pass → Stage 2
  → ❌ Fail → Fix → Re-review Stage 1

Stage 2: CODE QUALITY
  → Is the implementation well-built? Clean, tested, maintainable?
  → ✅ Pass → Proceed
  → ❌ Fail → Fix → Re-review Stage 2
```

**CRITICAL: Never start Stage 2 before Stage 1 passes.**

## How to Request (Dispatch Instructions)

**1. Get git SHAs:**
```bash
BASE_SHA=$(git rev-parse HEAD~1)  # or origin/main
HEAD_SHA=$(git rev-parse HEAD)
```

**2. Dispatch reviewer with context:**
- `{WHAT_WAS_IMPLEMENTED}` — What you just built
- `{PLAN_OR_REQUIREMENTS}` — What it should do
- `{BASE_SHA}` — Starting commit
- `{HEAD_SHA}` — Ending commit

**3. Act on feedback:**
- Fix Critical issues immediately
- Fix Important issues before proceeding
- Note Minor issues for later
- Push back if reviewer is wrong (with reasoning)

## Quick Review Checklist

### Spec Compliance
- [ ] All requirements from the plan implemented
- [ ] Nothing extra built that wasn't requested (YAGNI)
- [ ] No requirements misinterpreted

### Code Quality (Critical Review Framework)

Focus strictly on deficiencies, required improvements, and potential risks. Avoid positive affirmations.

1. **Key Changes & Impacts**: Check for regressions, conflicts, or unwanted behavior alterations.
2. **Clarity Deficiencies**: Pinpoint obscure logic, excessive nesting, long methods, and "magic" values. Suggest concrete refactorings.
3. **Comments and Naming**: Identify misleading/terse names, missing comments for complex logic, and redundant comments.
4. **Complexity Reduction**: Highlight overly complex logic/structures. Suggest simpler alternative approaches.
5. **Bug Risks & Edge Cases**: Enumerate off-by-one errors, unhandled states, resource mismanagement, concurrency issues, and security vulnerabilities.
6. **Best Practices Violations**: Flag anti-patterns, hardcoded configs, inefficient algorithms, and poor error handling.
7. **Testing & Follow-up**: Ensure unit tests cover new code, edge cases are tested, and tests pass (verified). If this is a follow-up review, verify previously requested changes and provide a strict Merge Decision (Yes / Yes with minor changes / No).
