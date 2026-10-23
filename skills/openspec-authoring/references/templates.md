# OpenSpec Templates

Templates for the core documents. Loaded on demand from `SKILL.md`.

### Small Task: `spec.md`

For small tasks, keep it extremely minimal.
*Note: Add Constraints only when they prevent wrong implementation choices.*

<details>
<summary>Template: docs/openspecs/&lt;task-name&gt;/spec.md</summary>

```markdown
# Spec: <Task Name>

## Goal
[1-2 sentences explaining the goal]

## Constraints (Optional)
[e.g. Do not change cache invalidation behavior.]

## Verify
[Concrete, executable check — HOW to confirm the behavior works, not why it matters]
- [Action to take]
- [Expected outcome]
```

</details>

### Medium/Large: `proposal.md` — Decision Record

Defines the Why, Goals, Assumptions, Decisions, Trade-offs, boundaries, and impact surface.

<details>
<summary>Template: proposal.md</summary>

```markdown
# Proposal: <Task Name>

## Problem
[What is the current issue? e.g. Payment failures require users to retry manually.]

## Goal
[What is the desired outcome?]

## Success
[Outcome-level signal that the *problem* is resolved — business/product terms, not a test step. For the concrete pass/fail check on a specific behavior, use the Scenario `Then:` in specs.md instead.]

## Assumptions
[What is taken for granted and will NOT be validated during this task?]
- [e.g. Existing auth middleware remains unchanged.]
- [e.g. Redis is available in all target environments.]
- [e.g. User IDs are immutable.]

## Decisions
[Which direction was chosen and why? e.g. Retry temporary failures in service layer.]

## Trade-offs
[What do we gain? What do we lose or risk?]

## Non-goals
[Things we intentionally chose NOT to optimize or address in this task, even though we could.]
- [e.g. Don't optimize query performance — current latency is acceptable.]
- [e.g. Don't redesign the existing API contract.]

## Out of Scope
[Features or work items that belong to a different task entirely.]
- [e.g. Admin retry dashboard.]
- [e.g. Analytics pipeline for retry metrics.]

## Impact

### Components
[Which services, modules, or packages are affected?]

### Files
[Exact file paths that will be created, modified, or deleted.]

### Public API
[Any changes to API endpoints, request/response shapes, error codes, or SDK methods. Write "None" if no public API changes.]

### Migration
[Database migrations, data backfills, config changes, or feature flag updates required. Write "None" if not applicable.]

### Backward Compatibility
[Will existing clients, integrations, or stored data break? What is the migration path?]
```

</details>

### Medium/Large: `specs.md` — Expected Behavior

Defines exactly how the system should behave. Covers both happy paths and failure paths. Avoid bureaucratic tags. Focus on clear Scenarios (When/Then), Failure Scenarios, Invariants, Rules, and Constraints.

<details>
<summary>Template: specs.md</summary>

```markdown
# Expected Behavior: <Task Name>

## Scenario: [Behavior Name e.g. Retry timeout errors]
**When:**
- [Trigger condition, e.g. payment timeout occurs]

**Then:**
- [Expected result, e.g. retry up to 3 times with exponential backoff]

## Failure Scenario: [Error Name e.g. Invalid card rejected]
**When:**
- [Error trigger condition, e.g. payment provider returns invalid_card]

**Then:**
- [Expected error handling, e.g. fail immediately, do NOT retry, notify user]

*Add one Failure Scenario per distinct error branch. AI agents commonly miss error paths if they are not explicitly specified.*

## Invariants
[Conditions that must ALWAYS hold true, regardless of any scenario or state transition.]
- [e.g. User balance must never become negative.]
- [e.g. Order ID is immutable after creation.]
- [e.g. Payment events are idempotent — processing the same event twice produces the same result.]

## Rules
- [Business or technical rules that must hold true regardless of specific events]

## Constraints
- [System boundaries or limitations]
```

</details>
