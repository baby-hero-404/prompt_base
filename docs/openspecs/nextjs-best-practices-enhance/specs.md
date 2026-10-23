# Specification: nextjs-best-practices v2

## 1. Deliverables
```
skills/nextjs-best-practices/
├── SKILL.md                                   # lean body <= 150 lines
└── references/
    ├── server-components-and-actions.md       # NEW
    ├── performance-and-waterfalls.md          # NEW
    ├── react19-and-composition.md             # NEW
    └── extended-reference.md                  # KEPT (+ pointer in section 8)
agents/frontend-specialist.md                  # skills unchanged; add Next/React pre-flight
registry.min.json                              # description now has Triggers on
tests/skills/trigger_cases.json                # + nextjs cases
```

## 2. Requirements
| ID | Requirement |
|---|---|
| N1 | MUST read `package.json` / `next.config.*` before applying snippets (Step 0) |
| N2 | MUST list 8 NEVER rules at the top of the body |
| N3 | MUST gate manual `useMemo`/`useCallback`/`memo` on React Compiler absence |
| N4 | Server Actions MUST authenticate, authorize and validate input inside the action |
| N5 | Priority order: waterfalls > bundle > server > client > re-render > micro |
| N6 | MUST use `await cookies()` / `await headers()` / awaited `params` and `searchParams` (Next 15) |
| N7 | MUST prefer `optimizePackageImports` over deep imports for barrel libraries |
| N8 | Every old topic still reachable (RSC split, data fetching, routing files, route handlers, images, Turbopack, PPR, metadata, caching, structure) |
| N9 | Verify checklist includes `tsc --noEmit`/lint, `next build`, tests |

## 3. Acceptance
`make registry`, `make skill-check`, `make test` pass; trigger precision/recall for `nextjs-best-practices` >= 0.9; skill installed via `make install`.
