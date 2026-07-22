---
name: project-memory
description: "Use when loading or managing persistent project-level context from global memory, including automated long-term memory (ADR capture/recall) via the context memory engine. Triggers on memory, adr capture."
triggers:
  - session-start
  - "project"
  - "architecture"
  - "system overview"
  - "init-context"
  - "project memory"
  - "context cache"
  - "long-term memory"
  - "adr"
  - "adr recall"
---
# Project Memory & Context Cache

> **Core Principle:** Transform "AI discovers the project" into "AI reads structured project memory."
> Every session should bootstrap from cached context files — never rescan the full codebase unless explicitly required.

---

## 0. Automated Long-Term Tier (Hook-Enforced)

The context files in `docs/ai/` below are this project's **current-state** memory — architecture, file map, task status. There is a separate, **automated long-term tier** for *why past decisions were made*, enforced by Claude Code hooks (not agent discipline):

| Layer | Location | Written by |
|-------|----------|------------|
| Decision records (source of truth, git-tracked) | `docs/ai/adr/YYYY-MM-DD-HHMMSS-<slug>.md` | `PreCompact` hook, from `<adr>` tags you emit |
| Session rollups (source of truth, git-tracked) | `docs/ai/archive/YYYY-MM-DD-HHMMSS-<slug>.md` | `PreCompact` hook, heuristic, every compaction |
| Derived index (disposable, stored globally) | `~/.claude/prompt_base_memory/{project_name}-{hash}/` (or `.ai-memory/` if `PB_LOCAL_MEMORY=1`) | Both hooks; rebuild anytime with `make memory-rebuild` |

**To get a decision captured**, emit this exact tag when you make (or the user confirms) an architecturally significant choice — the `PreCompact` hook extracts it by strict regex, not heuristic guessing, so the tag must match verbatim:

```
<adr title="Short decision title">
  <decision>What was decided, one or two sentences.</decision>
  <rationale>Why, including the alternative(s) rejected.</rationale>
</adr>
```

You do not need to do anything else — no manual file writing, no explicit "save this." The tag is enough; the hook handles extraction, dedup, secret-scrubbing, and embedding automatically at the next compaction.

**Recall is automatic too**: at the first prompt of a new session, a `UserPromptSubmit` hook injects the top-k most relevant past ADRs/rollups as `title — summary (path)` pointers (never full bodies, hard-capped in size). If a pointer looks relevant, read the file at that path — don't ask the user to repeat context that's already been surfaced.

If hooks are disabled or `sqlite-vec`/`fastembed` aren't installed, this tier degrades to keyword (FTS5) search automatically — recall still works, just without semantic ranking. Nothing about this tier changes the rest of this skill: the `docs/ai/` structure below remains the manually-maintained **current-state** memory.

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

All project memory files live in the `docs/ai/` directory, separated from human-facing documentation to avoid mixing concerns.

```
docs/ai/
├── context/                     # Project identity & discovery
│   ├── AI_PROJECT_CONTEXT.md    # Project overview & architecture summary
│   └── PROJECT_INDEX.md         # File map — where everything lives
├── patterns/                    # Code conventions & standards
│   └── CODING_PATTERNS.md      # Established code patterns & conventions
└── progress/                    # Task tracking & roadmap
    ├── TASK_STATUS.md           # Current task progress & notes
    └── PHASE_PLAN.md           # Roadmap phases & milestones (optional)
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


## Extended References
For less-frequently-needed detail, see [`references/extended-reference.md`](references/extended-reference.md):
- 2.2 `PROJECT_INDEX.md` — File Map
- 2.3 `CODING_PATTERNS.md` — Conventions & Patterns
- 2.4 `TASK_STATUS.md` — Progress Tracker
- 2.5 `PHASE_PLAN.md` — Roadmap (Optional)
- 3. Session Bootstrap Protocol
- 3.1 On Session Start
- 3.2 Bootstrap Prompt Template
- 3.3 Fallback: Missing Context Files
- 4. Context Update Protocol
- 4.1 After Every Task Completion
- 4.2 Update Rules
- 5. Memory Management
- 5.1 What Goes IN Project Memory
- 5.2 What Stays OUT of Project Memory
- 5.3 Staleness Prevention
- 6. Integration with Other Skills
- 7. Quick Reference
