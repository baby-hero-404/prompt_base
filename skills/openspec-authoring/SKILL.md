---
name: openspec-authoring
description: "Use when a coding task requires explicit expected behavior, verification criteria, or implementation coordination. Avoid for trivial changes. Triggers on openspec, proposal, design doc, spec."
allowed-tools: Read, Write, Edit
priority: HIGH
---

# OpenSpec Authoring

> **Decision-Preserving Execution Contract**: OpenSpec is NOT a heavy, bureaucratic requirement document. It is a contract that preserves intent, decisions, boundaries, and validation methods so that neither humans nor AI agents misunderstand the goal.

> 📌 **Sole Plan Standard**: An OpenSpec set is the sole planning and execution artifact for all non-trivial tasks. Never create legacy `docs/plans/` files.

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

Pick the files by task size (section 2). Copy the exact templates from [`references/templates.md`](references/templates.md):

| File | Size | Purpose |
|---|---|---|
| `spec.md` | Small | Goal, optional Constraints, concrete Verify steps |
| `proposal.md` | Medium/Large | Decision record: Problem, Goal, Success, Assumptions, Decisions, Trade-offs, Non-goals, Out of Scope, Impact |
| `specs.md` | Medium/Large | Expected behavior: When/Then Scenarios, one Failure Scenario per error branch, Invariants, Rules, Constraints |

Add Constraints to `spec.md` only when they prevent wrong implementation choices.

## Extended References
For Large tasks or detailed task breakdown rules, see [`references/extended-reference.md`](references/extended-reference.md):
- 3.4 `design.md` (Large Tasks only)
- 3.5 `tasks.md` (Medium/Large Tasks)
- 4. Golden Rules
- 5. Authoring Decision Matrix
- 6. Anti-Patterns
- 7. Checklist Before Submission
- 8. Code Staleness Cleanup
- 9. Documentation Sync

