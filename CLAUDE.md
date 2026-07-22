# CLAUDE.md - Prompt Base

> Installed globally at `~/.claude`. Applies to every project.

## Layout

| What | Where | When it loads |
|---|---|---|
| Rules (this file) | `~/.claude/CLAUDE.md` | Always |
| Agents | `~/.claude/agents/*.md` | Delegated via the Agent tool |
| Skills | `~/.claude/skills/*/SKILL.md` | Auto-triggered by keyword match |
| Workflows | `~/.claude/global_workflows/*.md` | On-demand via `/slash` commands |
| Registry | `~/.claude/registry.min.json` | Discovery index for the above |

## How to work

1. **Classify the request** (table below) before touching any tool.
2. **Discover**: grep `registry.min.json` by keyword to find a matching skill/agent — don't read it upfront.
3. **Load**: read only the `SKILL.md` sections you need.
4. **Execute**, then **forget**: once a sub-task ends, stop referencing that skill's details.

### Request classifier

| Type | Trigger words | Requires |
|---|---|---|
| Question | "what is", "how does", "explain" | Just answer |
| Survey | "analyze", "list files", "overview" | Read-only exploration |
| Simple edit | "fix", "add", "change" (single file) | Confirm understanding, then edit |
| Complex build | "build", "create", "implement", "refactor" | 3+ clarifying questions first, then a plan artifact |
| Design/UI | "design", "UI", "page", "dashboard" | Same as complex build |
| Slash command | `/plan`, `/review`, `/debug`, etc. | Follow that command's own flow |

**Plan artifact** (for complex build / design work): use exactly one —
1. An OpenSpec set at `docs/openspecs/<task>/` if one exists or was requested — detail goes in `design.md`/`tasks.md`, progress tracked via `tasks.md` checkboxes.
2. Otherwise `docs/plans/PLAN-YYYYMMDD-{slug}.md`.

Never keep both for the same task.

## Rules

**Clarify before building.** For new features or ambiguous edits, ask at least 3 concrete questions (or confirm understanding for small fixes) before writing code. Don't touch code until that's resolved.

**Explore before asking.** Check the codebase, project docs/memory, and related patterns first; only escalate to the user when the answer genuinely isn't derivable and the decision affects architecture, security, data models, API contracts, or UX.

**Keep it minimal.** Write only what the task needs — no speculative abstractions. State assumptions and tradeoffs instead of guessing silently. Push back on requested complexity when a simpler approach exists.

**Stay surgical.** Touch only what's necessary, match existing style, remove imports/vars your change orphaned. Fix an adjacent bug the moment you see it and note the fix.

**Check dependencies.** Before editing a file, check `ARCHITECTURE.md` → File Dependencies and update everything affected together.

**Document as you go.** Update the relevant `.md` files for what you changed. For spec-driven work, keep an `implementation-notes.md` in `docs/implementation/` with decisions, deviations, and tradeoffs not in the spec.

**Test and review.** Add tests for the success and failure paths before/with the implementation. Follow the 5-phase deployment process for infra changes. Prefer modern, actively-maintained libraries over legacy patterns.

## Context hygiene

- Don't reread `registry.min.json` in full more than once a session — grep it.
- Don't reread full files when a snippet or line range answers the question.
- Don't repeat file contents already shown in this conversation; reference path:line instead.
- Rely on the active plan artifact for state, not chat history.
- No filler: no apologies, no restating the request, no "the user wants X?" — act.
- Long-term decisions (architecture calls, rejected alternatives) belong in an ADR, captured automatically by the context memory engine's hooks when installed (`make memory-setup`; see the `project-memory` skill). Without hooks, capture them manually under `docs/ai/`.

## Final checklist

When the user says "run final checks" or similar:

| Stage | Command |
|---|---|
| Audit | `python scripts/checklist.py .` |
| Deploy | `python scripts/checklist.py . --url <URL>` |

## Agents (14)

| Agent | Domain |
|---|---|
| `orchestrator` | Multi-agent coordination |
| `project-planner` | Discovery & task planning |
| `explorer-agent` | Codebase analysis |
| `backend-specialist` | Server-side & database logic |
| `frontend-specialist` | Web UI/UX & growth |
| `mobile-developer` | Cross-platform mobile apps |
| `database-architect` | Schema & query optimization |
| `test-engineer` | QA & TDD |
| `security-auditor` | Cybersecurity & audit |
| `devops-engineer` | CI/CD & production ops |
| `performance-optimizer` | Speed & Core Web Vitals |
| `seo-specialist` | Search visibility & GEO |
| `debugger` | Root cause investigation |
| `documentation-writer` | Technical writing (on-demand) |
