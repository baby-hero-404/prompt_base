# Request Classifier

**Before ANY action, classify the request:**

| Request Type | Trigger Keywords | Active Tiers | Result |
|--------------|------------------|--------------|--------|
| **QUESTION** | "what is", "how does", "explain" | TIER 0 only | Text Response |
| **SURVEY/INTEL**| "analyze", "list files", "overview" | TIER 0 + Explorer | Session Intel (No File) |
| **SIMPLE CODE** | "fix", "add", "change" (single file) | TIER 0 + TIER 1 (lite) | Inline Edit |
| **COMPLEX CODE**| "build", "create", "implement", "refactor" | TIER 0 + TIER 1 (full) + Agent | **Plan artifact Required** (see Precedence below) |
| **DESIGN/UI** | "design", "UI", "page", "dashboard" | TIER 0 + TIER 1 + Agent | **Plan artifact Required** (see Precedence below) |
| **SLASH CMD** | /brainstorm, /create, /debug, /deploy, /enhance, /orchestrate, /plan, /status, /test, /init-context, /deep-solve, /restructure, /review, /ux-ui-pro | Command-specific flow | Variable |

## 📌 Plan Artifact Precedence

A "plan artifact" is satisfied by **exactly one** of the following, in priority order:

1. **OpenSpec set** — if `docs/openspecs/<task>/` exists for the task (or the user requested a spec), it IS the plan. Put implementation detail (data structures, test code, commands) in its `design.md`/`tasks.md`; track state via checkboxes in `tasks.md`. Do **NOT** create a parallel `docs/plans/PLAN-*.md`.
2. **Plan file (fallback)** — `docs/plans/PLAN-YYYYMMDD-{slug}.md`, only when no OpenSpec set covers the task.

Never maintain both artifacts for the same task — two sources of truth drift apart.
