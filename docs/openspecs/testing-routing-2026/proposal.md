# Proposal: Testing Skill Routing Clarification

## Why
The original combined proposal claimed `testing-patterns` and `tdd-workflow` "often conflict when a user asks to write tests" and proposed subordinating `testing-patterns` under `tdd-workflow`. On review, this claim is weaker than the other three consolidations in the original bundle:

- `tdd-workflow` is a **process-discipline** skill (strict Red-Green-Refactor, "Iron Law" against writing code before a failing test).
- `testing-patterns` is a **reference/pattern-library** skill (testing pyramid, AAA pattern, mocking strategies, test data builders).

These aren't really competing answers to the same question — someone retrofitting tests onto existing legacy code wants pattern guidance *without* having strict TDD discipline forced on them, since Red-Green-Refactor assumes you're writing the implementation too. `antigravity/agents/test-engineer.md` already lists both skills together in its `skills:` frontmatter, which suggests the intended usage is "both, together" rather than "one competing with the other."

**This proposal does not commit to the original merge direction.** It scopes an investigation step first, with the subordination as a fallback only if the investigation confirms real routing conflict.

## What Changes
- **Task 1 (investigation):** compare `tdd-workflow` and `testing-patterns`'s YAML `description` fields for keyword overlap, and check whether any workflow/agent actually exhibits routing ambiguity between them (not just "both could theoretically match").
- **Task 2 (conditional):** only if Task 1 finds real overlap, tighten `testing-patterns`'s description to disambiguate it as pattern reference rather than a competing top-level entry point — do not delete or merge either skill.

## Capabilities

### Modified Capabilities
- `testing-patterns`'s YAML `description` may be narrowed for clarity — content itself is unchanged either way.

### Removed Capabilities
- None. Unlike the other three consolidations, this proposal keeps both skills standalone.

## Impact

| Area | Files Affected |
|------|----------------|
| Skill (description only, conditional) | `antigravity/skills/process/testing-patterns/SKILL.md` |
| Skill (reference only, conditional) | `antigravity/skills/process/tdd-workflow/SKILL.md` |
| Registry | `registry.min.json` (regenerated, only if Task 2 executes) |

No agent or workflow file needs updating — `antigravity/agents/test-engineer.md` already references both skills by name and that reference remains valid regardless of outcome.
