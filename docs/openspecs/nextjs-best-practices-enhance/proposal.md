# Proposal: Enhance `nextjs-best-practices`

Source: `docs/discovery/DISCOVERY-nextjs-agent-skills.md` (Vercel Labs `agent-skills`, Accelint "NEVER Do React", modern App Router patterns). Same method as `docs/openspecs/flutter-best-practices/`.

## 1. Context
`skills/nextjs-best-practices` (137-line body) is a flat list of tables. It lacks: security of Server Actions, waterfall and bundle rules (Vercel's top two priorities), the React Compiler gate, the NEVER list, and a version check. The description has no `Triggers on`, so trigger tests cannot cover it.

## 2. Decisions (user-confirmed)
- **Versions**: baseline Next.js 15+ / React 19 with a mandatory Step 0 that reads `package.json` and `next.config.*` (`reactCompiler`, `cacheComponents`, `optimizePackageImports`). Differences for Next 16 are short notes, no separate reference.
- **Structure**: rewrite `SKILL.md` lean (priority order, NEVER list, compiler gate, loading table, checklist). Old sections 1, 2, 4, 5 move into three new references; section 3 (routing) stays compact in `SKILL.md`; `references/extended-reference.md` is kept (metadata, caching, project structure).
- **React-level rules** (NEVER list, derived state, ref as prop) live in this skill and link to `react-patterns`; `react-patterns` is not edited. Triggers stay narrow (`next.js`, `app router`, `server actions`, ...) to avoid collisions.
- **Agent**: update `agents/frontend-specialist.md` with a Next 15 / React 19 pre-flight checklist.

## 3. Corrections to the source report
- Report says import `lucide-react/dist/esm/icons/...`. The Vercel rule recommends **`experimental.optimizePackageImports`** first (keeps types), and direct imports only as fallback with a TypeScript `noImplicitAny` warning.
- Report implies React Compiler ships with Next 15. It is opt-in config; the gate is "check, don't assume".
- Report cites two links into a cached `~/.gemini/...` file for Accelint; the NEVER content is taken from the report text, not from that path.

## 4. Out of scope
`vercel-optimize`, `deploy-to-vercel`, view transitions, React Native rules, edits to `react-patterns`, `mobile-design`.

## 5. Risks
| Risk | Mitigation |
|---|---|
| Body > 150 lines warning | Lean body, detail in references |
| Trigger collisions with `react-patterns` | Narrow triggers; cases avoid the bare word "react" or expect both |
| Cache semantics differ per Next version | Step 0 + wording "uncached by default since 15" |
