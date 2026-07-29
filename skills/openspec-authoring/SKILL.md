---
name: openspec-authoring
description: "Use when a coding task requires explicit expected behavior, verification criteria, or implementation coordination. Avoid for trivial changes."
allowed-tools: Read, Write, Edit
priority: HIGH
---

# OpenSpec Authoring

> **Decision-Preserving Execution Contract**: OpenSpec is NOT a heavy, bureaucratic requirement document. It is a contract that preserves intent, decisions, boundaries, and validation methods so that neither humans nor AI agents misunderstand the goal.

> 📌 **Plan Artifact Precedence**: A complete OpenSpec set **satisfies** the COMPLEX CODE plan requirement. Do NOT create a parallel `docs/plans/PLAN-*.md`.

---

## 1. Style Guidelines

**Write for the next developer reading this 6 months later.**

**✅ Prefer:**
- Explain *why*
- State decisions explicitly — prefer decisions over descriptions (the choice made and why beats a plain description of what the system does)
- Mention trade-offs
- Define strict boundaries
- Distinguish **Success** (outcome-level: how we know the *problem* is solved) from **Verify** (action-level: the concrete check that proves a *behavior* works)

**❌ Avoid:**
- Empty sections
- Bureaucratic requirement IDs (e.g. REQ-001) or duplicated acceptance criteria
- Repeating obvious implementation details

---

## 2. Directory Convention & Complexity Check

Specs should live under the single root `docs/openspecs/` unless the repository already has an established convention. Choose the output size based on risk and complexity.

### Complexity Signals
**Upgrade one level (e.g. Small -> Medium, Medium -> Large) if the task includes:**
- Database schema migration
- Public API change
- Security/authentication
- Cross-service communication
- Data migration
- Backward compatibility concerns

**Downgrade one level (e.g. Medium -> Small) if:**
- Change is isolated to one module
- No API/data contract changes
- Existing tests fully cover behavior

### 🟢 Small Task
**Use for:** Simple UI tweaks, minor bug fixes, single-file changes.
**Output:** `docs/openspecs/<task-name>/spec.md` (1 file)

### 🟡 Medium Task
**Use for:** Independent features, minor refactoring, changes contained within a single service.
**Output:** `docs/openspecs/<task-name>/` containing 3 files:
- `proposal.md` (Why do it + key decisions)
- `specs.md` (What must be true - expected behavior)
- `tasks.md` (How to execute - implementation map)

### 🔴 Large Task
**Use for:** New architecture, complex cross-service features, high-risk migrations.
**Output:** `docs/openspecs/<task-name>/` containing 4 files:
- `proposal.md` (Why do it + key decisions)
- `specs.md` (What must be true - expected behavior)
- `design.md` (How to build it - architecture & reasoning)
- `tasks.md` (How to execute - implementation map)

---

## 3. Core Documents

### 3.1 Small Task: `spec.md`

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

### 3.2 Medium/Large: `proposal.md` — Decision Record

Defines the Why, Goals, Decisions, Trade-offs, and what is NOT included.

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

## Decisions
[Which direction was chosen and why? e.g. Retry temporary failures in service layer.]

## Trade-offs
[What do we gain? What do we lose or risk?]

## Out of Scope
[Explicitly state what to NOT build. e.g. No admin retry dashboard.]

## Impact
[What areas/files are affected?]
```

</details>

### 3.3 Medium/Large: `specs.md` — Expected Behavior

Defines exactly how the system should behave. Avoid bureaucratic tags. Focus on clear Scenarios (When/Then), Rules, and Constraints.

<details>
<summary>Template: specs.md</summary>

```markdown
# Expected Behavior: <Task Name>

## Scenario: [Behavior Name e.g. Retry timeout errors]
**When:**
- [Trigger condition, e.g. payment timeout occurs]

**Then:**
- [Expected result, e.g. retry up to 3 times with exponential backoff]

## Rules
- [Business or technical rules that must hold true regardless of specific events]

## Constraints
- [System boundaries or limitations]
```

</details>

## Extended References
For Large tasks or detailed task breakdown rules, see [`references/extended-reference.md`](references/extended-reference.md):
- 3.4 `design.md` (Large Tasks only)
- 3.5 `tasks.md` (Medium/Large Tasks)
- 4. Golden Rules
- 5. Authoring Decision Matrix
- 6. Anti-Patterns
- 7. Checklist Before Submission
