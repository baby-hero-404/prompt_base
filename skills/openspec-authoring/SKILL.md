---
name: openspec-authoring
description: "Use when writing OpenSpec specification sets (proposal, specs, design, tasks), structuring requirement documents, creating Gherkin-style scenarios, or breaking down complex tasks into prioritized work items. Triggers on spec, specification, proposal, design doc, task breakdown, openspec, requirement."
allowed-tools: Read, Write, Edit
priority: HIGH
---

# OpenSpec Authoring

> **Single Source of Truth**: An OpenSpec set is the authoritative contract between human intent and agent execution. The Coder Agent reads Specs — not raw descriptions.

> 📌 **Plan Artifact Precedence**: A complete OpenSpec set **satisfies** the COMPLEX CODE plan requirement (see the request classifier in CLAUDE.md/GEMINI.md). Do NOT create a parallel `docs/plans/PLAN-*.md` for the same task — implementation detail (data structures, test code, exact commands) belongs in `design.md`/`tasks.md`, and execution state is tracked via `tasks.md` checkboxes. If `tasks.md` feels too high-level to code from, enrich it in place instead of writing a separate plan.

---

## 1. Directory Convention

Every OpenSpec set lives under `docs/openspecs/<task-name>/` and contains exactly **4 files**:

```
docs/openspecs/<task-name>/
├── proposal.md    # WHY & WHAT — context, scope, impact
├── specs.md       # HOW to verify — Gherkin-style scenarios
├── design.md      # HOW to build — architecture, data models, APIs
└── tasks.md       # WHAT to do — prioritized work items with checklists
```

---

## 2. Core Documents

### 2.1 `proposal.md` — Solution Proposal

| Section | Content |
|---------|---------|
| **Why** | Root cause or motivation (cite real logs/traces when available) |
| **What Changes** | Detailed change list, grouped by Issue |
| **Capabilities** | `New` / `Modified` / `Removed` capabilities |
| **Impact** | Table: `Area \| Files Affected` |

<details>
<summary>Template</summary>

```markdown
# Proposal: <Task Name>

## Why
<!-- Root cause, log traces, user pain points -->

## What Changes

### Issue 1: <Title>
- Change A
- Change B

### Issue 2: <Title>
- Change C

## Capabilities

### New Capabilities
- ...

### Modified Capabilities
- ...

### Removed Capabilities
- ...

## Impact

| Area | Files Affected |
|------|----------------|
| Router | `internal/router/router.go` |
| Service | `internal/feature/service.go` |
```

</details>

### 2.2 `specs.md` — Requirement Specifications

| Section | Content |
|---------|---------|
| **Requirements** | Grouped as `Added` / `Modified` / `Removed` |
| **Scenarios** | Gherkin-style `WHEN … THEN … AND …` |
| **Status Icons** | `✅` Done · `⚠️` In Progress · `❌` Not Started |

<details>
<summary>Template</summary>

```markdown
# Specs: <Task Name>

## Added Requirements

### REQ-001: <Title>
> ✅ Status: Implemented

**Scenario:**
- WHEN <precondition or action>
- THEN <expected outcome>
- AND <additional assertion>

### REQ-002: <Title>
> ❌ Status: Not Started

**Scenario:**
- WHEN ...
- THEN ...

## Modified Requirements

### REQ-M01: <Title>
> ⚠️ Status: In Progress

**Scenario:**
- WHEN ...
- THEN ...

## Removed Requirements
- REQ-R01: <removed capability description>
```

</details>


## Extended References
For less-frequently-needed detail, see [`references/extended-reference.md`](references/extended-reference.md):
- 2.3 `design.md` — Technical Design
- 2.4 `tasks.md` — Execution Task List
- 3. Golden Rules
- 4. Authoring Decision Matrix
- 5. Anti-Patterns
- 6. Checklist Before Submission
