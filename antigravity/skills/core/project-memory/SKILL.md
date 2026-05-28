---
name: project-memory
description: "Use when loading or managing persistent project-level context from global memory."
triggers:
  - session-start
  - "project"
  - "architecture"
  - "system overview"
  - "init-context"
  - "project memory"
  - "context cache"
---
# Project Memory & Context Cache

> **Core Principle:** Transform "AI discovers the project" into "AI reads structured project memory."
> Every session should bootstrap from cached context files — never rescan the full codebase unless explicitly required.

---

## 1. Purpose

Eliminate redundant project scanning across AI sessions by maintaining a set of **structured context files** inside the repository. These files serve as the AI's persistent memory — a pre-compiled understanding of the project's architecture, patterns, file layout, and task progress.

### Why This Matters

| Without Project Memory | With Project Memory |
|------------------------|---------------------|
| AI scans entire codebase each session | AI reads 4–5 small files |
| High token consumption on discovery | Tokens spent on actual work |
| Slow session startup | Instant productive context |
| Inconsistent understanding | Stable, versioned knowledge |
| Repeated pattern violations | Enforced pattern adherence |

---

## 2. Context File Structure

All project memory files live in the `docs/` directory at the repository root.

```
docs/
├── AI_PROJECT_CONTEXT.md    # Project overview & architecture summary
├── PROJECT_INDEX.md         # File map — where everything lives
├── CODING_PATTERNS.md       # Established code patterns & conventions
├── TASK_STATUS.md           # Current task progress & notes
└── PHASE_PLAN.md            # Roadmap phases & milestones (optional)
```

### 2.1 `AI_PROJECT_CONTEXT.md` — Project Overview

The single source of truth for project identity and architecture.

**Must contain:**

```markdown
# Project Overview

- **Name**: <project-name>
- **Type**: <Backend | Frontend | Fullstack | Mobile | CLI | Library>
- **Language/Runtime**: <e.g., Go 1.22, Node 20, Python 3.12>
- **Framework**: <e.g., Gin, Next.js, FastAPI>
- **Database**: <e.g., PostgreSQL 16, MongoDB, SQLite>
- **Architecture**: <e.g., handler → service → repository>

# Key Architectural Decisions

- <Decision 1: e.g., Docker SDK for container management, not shell commands>
- <Decision 2: e.g., LLM execution is stubbed until Phase 4>

# Entry Points

- Main: <e.g., server/main.go>
- Router: <e.g., server/internal/router/router.go>
- Migrations: <e.g., server/migrations/>

# External Dependencies

- <e.g., Docker SDK, Redis, RabbitMQ>

# Environment & Config

- Config source: <e.g., .env, config.yaml>
- Key env vars: <list critical ones>
```

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

Every new AI session **MUST** begin with this bootstrap sequence:

```
1. Read docs/AI_PROJECT_CONTEXT.md
2. Read docs/PROJECT_INDEX.md
3. Read docs/TASK_STATUS.md
4. Read docs/CODING_PATTERNS.md (if touching code)
5. Do NOT scan the whole repository unless a needed file is missing from the index
```

### 3.2 Bootstrap Prompt Template

Use this as the internal session bootstrap directive:

```
Before coding, read the project memory files:
1. docs/AI_PROJECT_CONTEXT.md — understand the project
2. docs/PROJECT_INDEX.md — know where files live
3. docs/TASK_STATUS.md — know current progress
4. docs/CODING_PATTERNS.md — follow established patterns

Do not rescan the whole project unless required.
Follow existing patterns exactly.
Before coding, explain which files you will touch and why.
```

### 3.3 Fallback: Missing Context Files

If context files don't exist:

1. **Check for `ARCHITECTURE.md`** — may contain partial context (legacy format).
2. **Auto-generate** the missing files by scanning the codebase once.
3. **Prompt the user** to run `/init-context` for guided generation.

---

## 4. Context Update Protocol

### 4.1 After Every Task Completion

> 🔴 **MANDATORY**: After finishing any implementation, update the relevant context files.

| What Changed | Files to Update |
|-------------|-----------------|
| New feature/module added | `PROJECT_INDEX.md`, `AI_PROJECT_CONTEXT.md`, `TASK_STATUS.md` |
| New pattern established | `CODING_PATTERNS.md` |
| Task completed | `TASK_STATUS.md` |
| Architecture decision made | `AI_PROJECT_CONTEXT.md` |
| Phase milestone reached | `PHASE_PLAN.md`, `TASK_STATUS.md` |

### 4.2 Update Rules

- **Append, don't overwrite** — preserve history in task status.
- **Be concise** — these files should remain scannable (aim for < 200 lines each).
- **Date-stamp** significant changes in `TASK_STATUS.md`.
- **Never store raw code** — only patterns, references, and summaries.
- **Keep paths current** — if files move, update `PROJECT_INDEX.md` immediately.

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
- Review context files during code review — they are living documentation.
- Run periodic audits: ensure `PROJECT_INDEX.md` matches actual file structure.

---

## 6. Integration with Other Skills

| Skill | Integration Point |
|-------|-------------------|
| `context-management` | Project memory files are the primary MVC (Minimal Viable Context) source |
| `plan-writing` | Plans reference `TASK_STATUS.md` for current state |
| `architecture` | `AI_PROJECT_CONTEXT.md` feeds architectural decisions |
| `clean-code` | `CODING_PATTERNS.md` enforces consistency |
| `verification-before-completion` | Must verify context files are updated before claiming completion |

---

## 7. Quick Reference

```
┌─────────────────────────────────────────────────────┐
│              SESSION BOOTSTRAP FLOW                  │
│                                                      │
│  New Session                                         │
│      │                                               │
│      ▼                                               │
│  Read AI_PROJECT_CONTEXT.md  ← What is this project? │
│      │                                               │
│      ▼                                               │
│  Read PROJECT_INDEX.md       ← Where are things?     │
│      │                                               │
│      ▼                                               │
│  Read TASK_STATUS.md         ← What's the state?     │
│      │                                               │
│      ▼                                               │
│  Read CODING_PATTERNS.md     ← How do we code here?  │
│      │                                               │
│      ▼                                               │
│  START WORK (no full scan needed)                    │
│      │                                               │
│      ▼                                               │
│  FINISH → Update context files                       │
└─────────────────────────────────────────────────────┘
```
