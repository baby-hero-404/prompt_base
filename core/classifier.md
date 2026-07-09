# Request Classifier

**Before ANY action, classify the request:**

| Request Type | Trigger Keywords | Active Tiers | Result |
|--------------|------------------|--------------|--------|
| **QUESTION** | "what is", "how does", "explain" | TIER 0 only | Text Response |
| **SURVEY/INTEL**| "analyze", "list files", "overview" | TIER 0 + Explorer | Session Intel (No File) |
| **SIMPLE CODE** | "fix", "add", "change" (single file) | TIER 0 + TIER 1 (lite) | Inline Edit |
| **COMPLEX CODE**| "build", "create", "implement", "refactor" | TIER 0 + TIER 1 (full) + Agent | **docs/plans/PLAN-YYYYMMDD-{slug}.md Required** |
| **DESIGN/UI** | "design", "UI", "page", "dashboard" | TIER 0 + TIER 1 + Agent | **docs/plans/PLAN-YYYYMMDD-{slug}.md Required** |
| **SLASH CMD** | /brainstorm, /create, /debug, /deploy, /enhance, /orchestrate, /plan, /status, /test, /init-context, /deep-solve, /restructure, /review, /ux-ui-pro | Command-specific flow | Variable |
