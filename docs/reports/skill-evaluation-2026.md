# Skill Evaluation & Modernization Report (2026)

## 📊 Overview
This report evaluates all **54** skills in the Prompt Base framework (`core`: 9, `tech`: 17, `process`: 27, `custom`: 1) against the 2026 technology landscape. Every `SKILL.md` was read in full and cross-checked before being classified — see **⚠️ Corrections to Prior Assessment** for claims from the previous version of this report that didn't hold up.

---

## 🔴 Skills Outdated / Needing Major Refactoring

### 1. `database-design`
* **Current State:** Decision-tree covering PostgreSQL, Neon, Turso, SQLite, Drizzle, Prisma, Kysely, indexing, and migrations — all relational/SQL-oriented.
* **Modernization Need:** Zero mention of vector databases or embedding stores (pgvector, Pinecone, Milvus) or RAG data-modeling patterns, which are now standard for AI-app backends. Confirmed via full read of the skill's content map — no reference file covers this at all.

### 2. `mcp-builder`
* **Current State:** Covers MCP fundamentals correctly (Tools/Resources/Prompts, schema design, security) but frames **SSE** as a current transport option and only documents a basic "Claude Desktop Config" auth flow.
* **Modernization Need:** The MCP spec moved to **Streamable HTTP** as the standard replacement for SSE and added an **OAuth 2.1**-based auth framework in the 2025 revision. This skill still teaches the pre-revision transport model without noting the deprecation — a meaningful gap since MCP is core to this framework's own AI-tooling story.
* **Note:** This was rated "up-to-date" in the previous version of this report; a full read shows otherwise.

---

## 🟡 Skills Needing Enhancement (Missing Modern Paradigms)

### 1. `react-patterns`
* **Current State:** Already has a dedicated "React 19 Patterns" section covering `useActionState`, `useOptimistic`, and the `use` hook — this is **not** the Hooks-only skill the prior report described.
* **Enhancement:** RSC, Server Actions, and concurrent rendering each get only a one-line mention rather than real treatment. Deepen these three, don't rewrite the whole skill.

### 2. `nextjs-best-practices`
* **Current State:** Covers App Router, Server/Client component split, and the pre-15 `fetch`/`revalidate` caching model. No Next.js version is ever stated in the file.
* **Enhancement:** Add Next.js 15's changed caching defaults (uncached `fetch` by default), Partial Prerendering (PPR), Turbopack, and the `use cache` directive.

### 3. `api-patterns`
* **Current State:** Solid REST/GraphQL/tRPC decision tree via `api-style.md`.
* **Enhancement:** No mention of Server Actions as an API style or AI streaming response patterns (Vercel AI SDK, SSE for LLM tokens) — confirmed zero matches for "Server Action" or "streaming" in the file.

### 4. `docker-expert`
* **Current State:** Strong on multi-stage builds, non-root users, and Compose orchestration; explicitly defers Kubernetes elsewhere.
* **Enhancement:** No mention of WASM containers or microVM/Firecracker-style runtimes, which are increasingly used for serverless/edge deployment alongside traditional containers.

### 5. `mobile-design`
* **Current State:** Covers React Native, Flutter, native Swift/Kotlin, iOS HIG, and Material 3 across 16 reference files.
* **Enhancement:** No coverage of spatial computing (visionOS/XR) or voice-driven/conversational mobile UI — absent from both the platform-selection questions and every reference file.

### 6. `game-development`
* **Current State:** Solid engine-selection and pattern coverage (state machine, ECS, object pooling) for Unity/Godot/Unreal/Phaser.
* **Enhancement:** No patterns for integrating LLMs/AI agents into the game loop (dynamic NPC behavior, procedural narrative) — an increasingly standard 2025-26 pattern.

### 7. `coding-standards`
* **Current State:** Strong evergreen SOLID/DRY/naming principles, but also pins a "Modern Tech Mandate" stack: Next.js 15+, Node.js 22+, Drizzle-over-Prisma, Bun/Hono/Fastify-over-Express.
* **Enhancement:** Several pins are now dated snapshots of 2024-25 opinion rather than 2026 fact (Next 16 has since shipped; Node LTS has moved past 22). Revisit the version pins and soften the "avoid Express/Prisma" framing to a trade-off note rather than a mandate.

### 8. `typescript-expert`
* **Current State:** A thin router file — core substance (type gymnastics, build performance, decision checklists) is deferred entirely to three unread reference files.
* **Enhancement:** No TypeScript version is pinned anywhere in the main file. Verify the reference files are current, and consider pulling forward a version target into the main `SKILL.md` so currency is checkable without opening sub-files.

### 9. `seo-fundamentals`
* **Current State:** Solid on E-E-A-T, Core Web Vitals, and schema markup, with an "AI Content Guidelines" section.
* **Enhancement:** Doesn't cross-reference or defer to the sibling `geo-fundamentals` skill for Generative Engine Optimization (ranking in AI chat answers/AI Overviews) — the two skills currently overlap and split a topic that a 2026 SEO practitioner would treat as one.

### 10. `red-team-tactics`
* **Current State:** Solid MITRE ATT&CK lifecycle coverage (recon through exfiltration, Kerberoasting, DCSync, pass-the-hash).
* **Enhancement:** Zero OWASP references and no cloud/container attack techniques or AI/LLM-specific attack surfaces — gaps a 2026 red-team skill would need, especially since the sibling `vulnerability-scanner` skill is explicitly OWASP-2025-dated.
* **Note:** The previous report grouped this skill with `vulnerability-scanner` as "already referencing OWASP 2025 methodologies." That claim is false for this skill — see corrections below.

### 11. `red-teaming`
* **Current State:** PTES-based methodology with an OWASP Top 10 attack-surface list.
* **Enhancement:** The OWASP Top 10 reference is unversioned/undated, unlike `vulnerability-scanner`'s explicit "OWASP Top 10:2025" — align the dating so it's unambiguous which revision this skill targets.

### 12. `parallel-agents`
* **Current State:** Good parallelization pattern and prompt-writing guidance.
* **Enhancement:** Includes a hardcoded "Available Agents" table (orchestrator, security-auditor, backend-specialist, etc.) that risks drifting out of sync with whatever agents are actually configured in a given project. Consider pointing to a live agent registry instead of a static table.

### 13. `behavioral-modes`
* **Current State:** Six well-defined operating personas (BRAINSTORM/IMPLEMENT/DEBUG/REVIEW/TEACH/SHIP).
* **Enhancement:** Minor cleanup — the "Multi-Agent Collaboration Patterns" section header is hardcoded as "(2025)" (now stale) and has a dangling empty "## Combining Modes" heading with no content underneath.

---

## 🟢 Skills That Are Up-To-Date (Good Standing)

**Core (6):** `architecture`, `brainstorming`, `context-management`, `plan-writing`, `project-memory`, `skill-loading` — all process/meta skills with no dated tech dependency.

**Tech (9):** `app-builder`, `golang-best-practices` (targets Go 1.23+ generics/iterators), `jupyter-notebooks`, `nestjs-expert`, `nodejs-best-practices` (already covers Bun, Deno, and Node 22+ — see correction below), `prisma-expert` (thorough and current for its intentionally Prisma-only scope), `python-patterns` (Ruff/uv/Pyright/Pydantic), `tailwind-patterns` (explicitly v4-dated), `ux-ui-pro-max` (covers shadcn/Jetpack Compose/SwiftUI).

**Process (24):** `bash-linux`, `code-graph-analysis`, `code-review-checklist`, `codebase-cleanup`, `deployment-procedures`, `documentation-templates` (already covers `llms.txt`/MCP-ready docs), `frontend-design` (actively bans "AI slop" design clichés), `geo-fundamentals`, `i18n-localization`, `lint-and-validate`, `openspec-authoring`, `performance-profiling` (uses current INP metric, not deprecated FID), `powershell-windows`, `readme-generator`, `receiving-code-review`, `review-pre-commit-git`, `server-management`, `subagent-driven-development`, `systematic-debugging`, `tdd-workflow`, `testing-patterns`, `verification-before-completion`, `vulnerability-scanner` (the most current skill in the set — explicit "OWASP Top 10:2025"), `webapp-testing` (Playwright-based, current config practices).

---

## ⚠️ Corrections to Prior Assessment

The previous version of this report made three claims that a full-text read disproved:

1. **`nodejs-best-practices`** was listed as needing Bun/Deno support "expanded in." It already has a "Runtime Selection" table naming Node, Bun, and Deno explicitly, plus Node 22+ native TypeScript stripping. No action needed beyond optionally pinning "Deno 2.x" by version number.
2. **`react-patterns`** was described as needing "a complete overhaul" for React 19. It already has a dedicated React 19 section. The real gap is narrower — see 🟡 #1 above.
3. **`vulnerability-scanner` & `red-team-tactics`** were both credited with "already referencing OWASP 2025 methodologies." Only `vulnerability-scanner` does; `red-team-tactics` has zero OWASP mentions and is scoped to MITRE ATT&CK only. See 🟡 #10 above.

Additionally, **`prisma-expert`** was flagged as needing a `modern-orms-expert` split. On inspection, ORM comparison (Drizzle vs. Prisma vs. Kysely) is already handled by `database-design`'s `orm-selection.md` reference file — `prisma-expert` is deep-dive documentation for teams that have already chosen Prisma, by design. No split needed; the real ORM-related gap is `database-design`'s missing vector-DB coverage (🔴 #1).

---

## 🚀 Recommended Action Items
1. **Fix the two 🔴 items first:** add vector-DB/RAG content to `database-design`, and update `mcp-builder` for Streamable HTTP transport + OAuth 2.1.
2. **Targeted deepening, not rewrites:** for `react-patterns` and `nodejs-best-practices`, resist re-doing work that's already current — only close the specific gaps listed above.
3. **Resolve the `seo-fundamentals` / `geo-fundamentals` overlap:** decide whether to merge or have one explicitly defer to the other.
4. **Re-date `coding-standards` and `red-teaming`:** both contain version/spec references that need refreshing or explicit dating so future audits can tell stale from current at a glance.
5. **Regenerate Registry:** after updating any `SKILL.md` descriptions, run `make registry` to refresh `registry.min.json`, then `make install` (or `install-claude` / `install-gemini`) to deploy.
