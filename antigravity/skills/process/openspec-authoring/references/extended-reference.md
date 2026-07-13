### 2.3 `design.md` — Technical Design

| Section | Content |
|---------|---------|
| **Architecture Diagram** | Mermaid flowchart / sequence diagram |
| **Data Models & API** | JSON/YAML Schema, Go structs, API endpoints |
| **Security & Execution Boundaries** | Agent sandbox permissions (read/write scope) |
| **Risk Mitigation** | Risk table with severity and mitigation plan |

<details>
<summary>Template</summary>

````markdown
# Design: <Task Name>

## Architecture

```mermaid
flowchart TD
    A["Input"] --> B["Processor"]
    B --> C["Output"]
```

## Data Models

```go
type FeatureConfig struct {
    ID     string `json:"id"`
    Enabled bool  `json:"enabled"`
}
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/v1/feature` | Create feature |
| GET  | `/api/v1/feature/:id` | Get feature |

## Security & Execution Boundaries

| Agent | Allowed Paths | Permissions |
|-------|---------------|-------------|
| Coder | `internal/feature/` | Read, Write |
| Reviewer | `internal/` | Read only |

## Risk Mitigation

| Risk | Severity | Mitigation |
|------|----------|------------|
| Memory leak in loop | HIGH | Add context timeout |
| Schema drift | MEDIUM | JSON Schema validation |
````

</details>

### 2.4 `tasks.md` — Execution Task List

| Section | Content |
|---------|---------|
| **Task ID** | Numbered logically (e.g. `Task 1.1`, `Task 1.2`), linked to `specs.md` scenarios |
| **Priority** | `P0` (Critical) · `P1` (High) · `P2` (Medium) · `P3` (Low) |
| **Acceptance Criteria** | Specific, testable conditions for each task |
| **Checklist** | `[ ]` / `[x]` checkboxes for progress tracking |

<details>
<summary>Template</summary>

```markdown
# Tasks: <Task Name>

## P0 — Critical

### Task 1.1: <Title>
> Links to: REQ-001

**Acceptance Criteria:**
- [ ] Criterion A
- [ ] Criterion B

### Task 1.2: <Title>
> Links to: REQ-002

**Acceptance Criteria:**
- [ ] Criterion A

## P1 — High

### Task 2.1: <Title>
> Links to: REQ-M01

**Acceptance Criteria:**
- [ ] Criterion A
- [ ] Criterion B

## P2 — Medium
(none)

## P3 — Low
(none)
```

</details>

---

## 3. Golden Rules

| # | Rule | Rationale |
|---|------|-----------|
| 1 | **Single Source of Truth** | Agent Coder reads the Spec, not raw user descriptions. The OpenSpec must reflect actual execution structure. |
| 2 | **Parallel Decomposition** | Subtasks designed for parallel execution must be resource-independent, or define explicit file-change context flow. |
| 3 | **Validation & Security First** | Always define JSON Schema for agent output validation. Always constrain `execution_boundaries` to prevent memory leaks and security breaches. |

---

## 4. Authoring Decision Matrix

| Situation | Start With |
|-----------|------------|
| Bug fix with known root cause | `proposal.md` → `specs.md` → `tasks.md` (skip `design.md` if architecture unchanged) |
| New feature from scratch | `proposal.md` → `design.md` → `specs.md` → `tasks.md` |
| Refactoring / migration | `proposal.md` → `design.md` → `tasks.md` → `specs.md` |
| Hotfix / emergency patch | `tasks.md` only (backfill others after resolution) |

---

## 5. Anti-Patterns

| ❌ Don't | ✅ Do |
|----------|-------|
| Write vague requirements without scenarios | Use Gherkin-style `WHEN/THEN/AND` for every requirement |
| Mix multiple unrelated issues in one spec set | Create separate `docs/openspecs/<name>/` per logical scope |
| Skip the Impact table in `proposal.md` | Always list affected files — agents depend on this for context loading |
| Assign tasks without acceptance criteria | Every task must have at least one testable criterion |
| Leave status icons stale | Update `✅ ⚠️ ❌` as work progresses |

---

## 6. Checklist Before Submission

- [ ] All 4 files exist in `docs/openspecs/<task-name>/`
- [ ] `proposal.md` has Why, What Changes, Capabilities, Impact sections
- [ ] `specs.md` has at least one `WHEN/THEN` scenario per requirement
- [ ] `design.md` includes a Mermaid diagram (if architecture changes)
- [ ] `tasks.md` tasks link back to `specs.md` requirement IDs
- [ ] All status icons (`✅ ⚠️ ❌`) are current
- [ ] No task lacks acceptance criteria
