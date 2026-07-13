## Execution Handoff

After saving the plan, offer execution choice:

**"Plan complete. Two execution options:**

**1. Subagent-Driven (recommended)** — Fresh subagent per task, review between tasks, fast iteration

**2. Inline Execution** — Execute tasks in this session, batch execution with checkpoints

**Which approach?"**

## Red Flags

- Plan with vague steps ("add appropriate handling")
- Steps without code blocks
- Missing file paths
- Tasks referencing undefined types/functions
- No test steps
- Plan longer than necessary (YAGNI violation)

## Common Rationalizations

| Excuse | Reality |
|--------|---------|
| "Plan is obvious, just start coding" | Plans catch assumptions. 10 min planning saves hours. |
| "Too detailed is wasteful" | Under-specified plans produce wrong code. Be explicit. |
| "I'll figure it out during implementation" | That's not a plan. That's winging it. |
| "Similar to Task N" | The engineer may read tasks out of order. Repeat the code. |
