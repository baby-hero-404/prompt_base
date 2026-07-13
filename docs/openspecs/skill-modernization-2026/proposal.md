# Proposal: Skill Modernization 2026

## Why
`docs/reports/skill-evaluation-2026.md` audited all 54 `SKILL.md` files against the 2026 tech landscape (full-text read + fact-check of every claim, not a skim). It found 2 skills with major content gaps and 13 with narrower, targeted gaps. Left unaddressed, agents invoking these skills give advice that omits current standard practice (e.g. `mcp-builder` still teaches SSE without noting it was superseded by Streamable HTTP in the 2025 MCP spec revision; `database-design` has no vector-DB/RAG path at all despite that being a default requirement for AI-app backends).

This proposal scopes the fixes identified by that report. It does not re-open skills the report verified as already current (`nodejs-best-practices`, `tailwind-patterns`, `vulnerability-scanner`, etc.) — see the report's "Corrections to Prior Assessment" section for why some skills that looked stale on a shallow read were not.

## What Changes

### Issue 1: Major content gaps (🔴)
- `database-design`: add vector database / embedding-store design guidance (pgvector, Pinecone, Milvus) and RAG data-modeling patterns.
- `mcp-builder`: replace SSE-as-current framing with Streamable HTTP as the standard transport; add OAuth 2.1 auth-flow coverage.

### Issue 2: Framework/runtime currency gaps (🟡)
- `react-patterns`: deepen RSC, Server Actions, and concurrent rendering beyond their current one-line mentions.
- `nextjs-best-practices`: add Next.js 15 caching-default changes, Partial Prerendering (PPR), Turbopack, and `use cache`.
- `api-patterns`: add Server Actions as an API style and AI streaming response patterns (SSE for LLM tokens, Vercel AI SDK).
- `docker-expert`: add WASM containers and microVM (Firecracker-style) runtimes alongside traditional Docker/Compose content.
- `mobile-design`: add spatial computing (visionOS/XR) and voice-driven UI guidance.
- `game-development`: add LLM/AI-agent integration patterns for the game loop (NPC behavior, procedural narrative).

### Issue 3: Stale pins & dating (🟡)
- `coding-standards`: refresh version pins (Next.js 15+, Node 22+) and soften the "avoid Express/Prisma" mandate to a documented trade-off.
- `red-teaming`: version-date its OWASP Top 10 reference to match `vulnerability-scanner`'s explicit "2025" dating.
- `behavioral-modes`: remove the hardcoded "(2025)" section heading and resolve the dangling empty "Combining Modes" heading.

### Issue 4: Missing/overlapping coverage (🟡)
- `typescript-expert`: pull a TypeScript version target into the main `SKILL.md` (currently deferred entirely to unread reference files).
- `seo-fundamentals`: resolve topical overlap with `geo-fundamentals` (decide: merge, or cross-reference explicitly).
- `red-team-tactics`: add OWASP-aligned web/cloud/container attack coverage and AI/LLM attack-surface techniques alongside its existing MITRE ATT&CK content.
- `parallel-agents`: replace the hardcoded "Available Agents" table with a reference to the live agent registry so it can't drift out of sync.

### Issue 5: Registry sync
- After all `SKILL.md` edits land, regenerate `registry.min.json` (`make registry`) and redeploy (`make install`), per this repo's own install pipeline (`scripts/generate_registry.py` reads each skill's YAML frontmatter `description` — stale descriptions mean stale skill discovery, independent of body content).

## Capabilities

### New Capabilities
- Vector-DB / RAG design guidance (within `database-design`)
- MCP Streamable HTTP + OAuth 2.1 guidance (within `mcp-builder`)
- AI/LLM-integration guidance in `game-development` and `api-patterns`

### Modified Capabilities
- `react-patterns`, `nextjs-best-practices`, `docker-expert`, `mobile-design`, `coding-standards`, `typescript-expert`, `seo-fundamentals`, `red-team-tactics`, `red-teaming`, `parallel-agents`, `behavioral-modes`

### Removed Capabilities
- None — this is additive/corrective content work, no skill is being deleted.

## Impact

| Area | Files Affected |
|------|----------------|
| Vector DB / RAG | `antigravity/skills/tech/database-design/SKILL.md` (+ possible new reference file) |
| MCP transport/auth | `antigravity/skills/tech/mcp-builder/SKILL.md` |
| React | `antigravity/skills/tech/react-patterns/SKILL.md` |
| Next.js | `antigravity/skills/tech/nextjs-best-practices/SKILL.md` |
| API patterns | `antigravity/skills/tech/api-patterns/SKILL.md` |
| Docker | `antigravity/skills/tech/docker-expert/SKILL.md` |
| Mobile | `antigravity/skills/tech/mobile-design/SKILL.md` |
| Game dev | `antigravity/skills/tech/game-development/SKILL.md` |
| Coding standards | `antigravity/skills/core/coding-standards/SKILL.md` |
| TypeScript | `antigravity/skills/tech/typescript-expert/SKILL.md` |
| SEO/GEO | `antigravity/skills/process/seo-fundamentals/SKILL.md`, `antigravity/skills/process/geo-fundamentals/SKILL.md` |
| Red team | `antigravity/skills/process/red-team-tactics/SKILL.md`, `antigravity/skills/process/red-teaming/SKILL.md` |
| Agent orchestration | `antigravity/skills/core/parallel-agents/SKILL.md` |
| Behavioral modes | `antigravity/skills/core/behavioral-modes/SKILL.md` |
| Registry sync | `registry.min.json` (generated, do not hand-edit), `scripts/generate_registry.py` (read-only reference) |
