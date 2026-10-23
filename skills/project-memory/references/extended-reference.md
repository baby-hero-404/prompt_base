> **Superseded in part:** `AI_PROJECT_CONTEXT.md`, `PROJECT_INDEX.md` and `CODING_PATTERNS.md` (§2.2, §2.3) are replaced by `docs/ai/PROFILE.md` and `docs/ai/DOMAIN.md`. §2.4 and §2.5 stay optional under `docs/ai/progress/`. Sections 3 to 5 refer to the old file names; read them as `PROFILE.md` / `DOMAIN.md`. Current model: `SKILL.md` → Memory layers.

### 2.2 `PROJECT_INDEX.md` — File Map

A curated directory of important files grouped by domain. This replaces the need for `find`, `grep`, and `ls` exploration.

**Must contain:**

```markdown
# Project Index

## Entry Points
- server/main.go
- server/internal/router/router.go

## Auth
- server/internal/auth/handler.go
- server/internal/auth/service.go
- server/internal/auth/repository.go

## Domain: <Feature Name>
- server/internal/<feature>/handler.go
- server/internal/<feature>/service.go
- server/internal/<feature>/repository.go

## Migrations
- server/migrations/

## Config
- .env.example
- config.yaml

## Tests
- server/internal/<feature>/<feature>_test.go
```

> **Rule:** Every new module/feature added must be reflected in this index.

### 2.3 `CODING_PATTERNS.md` — Conventions & Patterns

Documents the established patterns that AI must follow. Prevents pattern drift across sessions.

**Must contain:**

```markdown
# Coding Patterns

## Handler Pattern
1. Parse & validate request (bind JSON/query params)
2. Call service layer
3. Return structured JSON response
4. Never access DB directly

## Service Pattern
1. Business logic & validation
2. Orchestrate repository calls
3. Return domain errors, not HTTP errors

## Repository Pattern
1. Database queries only
2. No business logic
3. Return domain models

## Error Handling
- <e.g., Wrap errors with context using fmt.Errorf>
- <e.g., Use custom error types for domain errors>

## Naming Conventions
- <e.g., Files: snake_case>
- <e.g., Functions: camelCase / PascalCase for exported>
- <e.g., DB tables: snake_case plural>

## Testing Conventions
- <e.g., Table-driven tests>
- <e.g., Mock interfaces, not implementations>
```

### 2.4 `TASK_STATUS.md` — Progress Tracker

Tracks what's done, what's in progress, and critical implementation notes.

**Must contain:**

```markdown
# Task Status

## ✅ Done
- Task 1: <description> — <date>
- Task 2: <description> — <date>

## 🔄 In Progress
- Task 3: <description>
  - Blocker: <if any>
  - Next step: <specific next action>

## 📋 Backlog
- Task 4: <description>

## 📝 Implementation Notes
- <e.g., Docker container management uses Docker SDK, not shell commands>
- <e.g., LLM execution is stubbed in Phase 3>
- <e.g., Auth tokens expire after 24h, refresh flow is in auth/service.go>
```

### 2.5 `PHASE_PLAN.md` — Roadmap (Optional)

For phased projects, tracks the overall roadmap and milestone boundaries.

```markdown
# Phase Plan

## Phase 1: Foundation ✅
- Database schema & migrations
- Auth system

## Phase 2: Core Features 🔄
- Feature A
- Feature B

## Phase 3: Infrastructure 📋
- CI/CD pipeline
- Monitoring
```

---

## 3. Session Bootstrap Protocol

### 3.1 On Session Start

Every new AI session begins with this bootstrap sequence:

```
1. Read docs/ai/PROFILE.md — identity, architecture, stack, repo map
2. Read docs/ai/DOMAIN.md — domain concepts, invariant rules, quirks
3. Check task state in docs/openspecs/<task>/tasks.md (or docs/ai/progress/ if used)
4. Check recall pointers (injected ADRs) if relevant
5. Do NOT rescan the repository unless a required file is missing from the repo map
```

### 3.2 Bootstrap Prompt Template

Use this as the internal session bootstrap directive:

```
Before coding, read the project memory files:
1. docs/ai/PROFILE.md — understand the project and architecture
2. docs/ai/DOMAIN.md — adhere to invariant rules and domain concepts
3. docs/openspecs/<task>/tasks.md — current active task status

Do not rescan the whole project unless required.
Follow existing patterns and invariant rules exactly.
Before coding, explain which files you will touch and why.
```

### 3.3 Fallback: Missing Context Files

If context files don't exist:

1. **Check for `ARCHITECTURE.md`** — may contain partial context (spec format).
2. **Read-only orientation** via `/init-context`.
3. **Prompt the user** to run `/init-memory` if persistent cross-session memory is needed.

---

## 4. Context Update Protocol

### 4.1 After Every Task Completion

> 🔴 **MANDATORY**: After finishing any implementation, keep project memory fresh.

| What Changed | Files to Update |
|-------------|-----------------|
| New module/stack component | `docs/ai/PROFILE.md` (Repository Map / Stack) |
| Invariant rule / domain concept | `docs/ai/DOMAIN.md` |
| Architectural decision | Emit `<adr>` tag (automatically saved to `docs/ai/adr/`) |
| Trigger file or config updated | Run `python3 tools/memory_stale.py --root . --update` |
| Task progress | `docs/openspecs/<task>/tasks.md` |

### 4.2 Update Rules

- **Append, don't overwrite** — preserve history in task status and ADR records.
- **Be concise** — keep memory files scannable (PROFILE.md and DOMAIN.md each under ~60 lines).
- **Run staleness update** — always run `memory_stale.py --update` after modifying trigger files.

---

## 5. Memory Management

### 5.1 What Goes IN Project Memory

✅ Architecture overview & decisions
✅ File locations & module boundaries
✅ Established code patterns & conventions
✅ Task progress & implementation notes
✅ Key configuration & environment details
✅ Critical domain knowledge & constraints

### 5.2 What Stays OUT of Project Memory

❌ Raw source code or full file contents
❌ Verbose configuration files
❌ Dependency lock files or auto-generated content
❌ Temporary debugging notes
❌ Sensitive credentials or secrets

### 5.3 Staleness Prevention

- Context files are **versioned with the repo** (committed to git).
- `manifest.json` tracks checksums of `autoRefreshTriggers` (rule files, architecture, build files).
- `python3 tools/memory_stale.py --root .` detects stale memory when trigger files change; refresh via `/init-memory`.

---

## 6. Integration with Other Skills

| Skill | Integration Point |
|-------|-------------------|
| `context-management` | Project memory files are the primary MVC (Minimal Viable Context) source |
| `openspec-authoring` | Active task progress tracked in `docs/openspecs/<task>/tasks.md` |
| `architecture` | Project memory feeds architectural decisions; capture via `<adr>` tags |
| `coding-standards` | Invariant rules in `docs/ai/DOMAIN.md` enforce coding consistency |
| `verification-before-completion` | Must verify memory staleness before claiming completion |
| Automated long-term tier | `PreCompact`/`UserPromptSubmit` hooks handle ADR capture/recall (see Section 0) — no skill invocation needed, just emit the `<adr>` tag |

---

## 7. Quick Reference

```
┌────────────────────────────────────────────────────────────┐
│                  SESSION BOOTSTRAP FLOW                     │
│                                                            │
│  New Session                                               │
│      │                                                     │
│      ▼                                                     │
│  Read docs/ai/PROFILE.md                 ← What & Where?   │
│      │                                                     │
│      ▼                                                     │
│  Read docs/ai/DOMAIN.md                  ← Invariants?     │
│      │                                                     │
│      ▼                                                     │
│  Read docs/openspecs/<task>/tasks.md     ← Task status?    │
│      │                                                     │
│      ▼                                                     │
│  START WORK (minimal scan needed)                          │
│      │                                                     │
│      ▼                                                     │
│  FINISH → Update memory (emit <adr>, update manifest)     │
└────────────────────────────────────────────────────────────┘
```
