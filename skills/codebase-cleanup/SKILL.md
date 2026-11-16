---
name: codebase-cleanup
description: "Use when the user asks for a cleanup of the whole repository or a named area, beyond the current task: unused code, duplicates, needless complexity, weak tests, structural drift. Routes to the focused cleanup skills and keeps business logic unchanged. For cleaning only what you just changed use code-cleanup. Triggers on codebase cleanup, repo cleanup, clean up the codebase, tech debt sweep."
allowed-tools: Read, Write, Edit, Glob, Grep, Bash
---

# Codebase Cleanup (repository-wide sweep)

> A sweep is the one time cleanup may go beyond the current change. It runs only because the user asked, and it changes nothing before the user has seen the list.

## When to use

- The user asks to clean up the repository, a directory, or a module.
- A periodic pass before a release.

**Not this skill:** after an ordinary task, clean only your own change with `code-cleanup`.

## Routing

This skill holds the order and the safety rules. The knowledge lives in the focused skills; load each one when its step starts.

| Step | Skill | Finds |
|---|---|---|
| 1 | `architecture-audit` | Boundary leaks, cycles, layering, duplicated logic across modules |
| 2 | `dead-code-removal` | Unused code, files, dependencies, flags, obsolete tests |
| 3 | `code-simplifier` | Single-use abstractions, pass-through layers, needless options |
| 4 | `test-hygiene` | Tests that prove nothing, over-mocked, redundant, flaky |
| 5 | `code-cleanup` | Stale comments, commented-out code, debug output, leftover drafts |
| 6 | `code-review` | Review of the resulting diff |

Structure comes first because a structural move changes what counts as unused or duplicated.

## Procedure

1. **Agree on scope.** Whole repository or a named area. Exclude generated, vendored, and third-party code.
2. **Survey, read-only.** Run steps 1 to 5 as analysis only. Go breadth first; inspect the riskiest areas in depth and list what was only surveyed.
3. **Propose.** Show the list of changes grouped by step, each with evidence and risk. Wait for the user to choose.
4. **Apply in small groups.** One kind of change per group. Run tests, linter, and build after each group. If a group fails, undo it and report.
5. **Review the diff** with `code-review`, then finish with `verification-before-completion`.

## Safety requirements

- **Do not change business logic.**
- **Do not change public interfaces or stored data** unless the user approves that specific change.
- **Do not remove code that may be referenced dynamically** without the verification in `dead-code-removal`. If unsure, mark it "potentially unused" and leave it.
- **No test coverage, no change.** Pin the behavior with a test first, or report the item only.
- Explain why each file or function is removed.
- Never touch uncommitted work that is not part of the sweep.
- Follow `coding-standards` for everything you rewrite.

## Report

- **Summary of issues found:** overview of unused code and technical debt, by step.
- **Files and functions removed:** each with its evidence in one line.
- **Duplicate logic resolved:** where, and what it became.
- **Simplified:** what, and why.
- **Potentially unused:** items left in place and the check that could not be completed.
- **Recommendations:** structural moves not applied, ranked.
- **Surveyed but not inspected:** areas for a later pass.
- **Final status:** verification commands and their results, confirming behavior is preserved.
