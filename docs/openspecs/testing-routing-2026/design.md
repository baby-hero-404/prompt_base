# Design: Testing Skill Routing Clarification

## Approach
No architecture change either way — this is an investigation with a conditional, minimal follow-up. No Mermaid diagram: there's nothing structural to show until (and unless) REQ-001 confirms a real conflict.

## Security & Execution Boundaries

| Agent | Allowed Paths | Permissions |
|-------|---------------|-------------|
| Coder | `antigravity/skills/process/testing-patterns/SKILL.md`, `antigravity/skills/process/tdd-workflow/SKILL.md` | Read; Write only on `testing-patterns`'s YAML frontmatter, and only if REQ-001 confirms conflict |
| Coder | `registry.min.json` | Write (generated output only, via `make registry`, only if Task 2 executes) |

## Risk Mitigation

| Risk | Severity | Mitigation |
|------|----------|------------|
| Proceeding straight to subordinating `testing-patterns` without evidence, based on the original bundled proposal's unverified claim | MEDIUM | REQ-001 gates REQ-M01 — no description change happens without a cited overlap |
| Narrowing `testing-patterns`'s description accidentally removes a legitimate standalone use case (e.g. someone wanting mocking-strategy guidance without any TDD process attached) | LOW | If Task 2 executes, keep the description change minimal — add disambiguating language, don't remove existing trigger keywords wholesale |
