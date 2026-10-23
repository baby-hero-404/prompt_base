---
name: nextjs-best-practices
description: "Use when developing Next.js App Router applications, implementing Server Components or Server Actions, defining data fetching and routing, or fixing Next.js performance (waterfalls, bundle size). Triggers on next.js, nextjs, app router, server actions, server components, route handlers."
allowed-tools: Read, Write, Edit, Glob, Grep
references: [server-components-and-actions.md, performance-and-waterfalls.md, react19-and-composition.md, extended-reference.md]
---

# Next.js Best Practices

> **Baseline: Next.js 15+ / React 19, App Router.** Server Components by default. Fix network and bundle problems before touching JavaScript micro-optimizations.

---

## Step 0: Read the project first (MANDATORY)

1. Read `package.json`: `next`, `react` majors, `babel-plugin-react-compiler`, data libs (SWR, React Query), validation (Zod), auth library.
2. Read `next.config.*`: `reactCompiler`, `cacheComponents` / `experimental.ppr`, `experimental.optimizePackageImports`, image config.
3. Follow the version you find. On Next 14 or earlier, `params`, `cookies()`, `headers()` are synchronous and fetch is cached by default; on 15+ they are async and fetch is uncached by default. Next 16 projects may use `use cache` with `cacheComponents`.
4. Prefer existing project conventions (folder layout, auth helper, validation schema style) over the defaults here.

## NEVER Do (React and Next.js)

1. **Define a component inside a component.** It remounts on every parent render (lost state, lost input focus, effect churn). Hoist it to module scope.
2. **Subscribe to `searchParams` / `localStorage` in the body when only a callback needs it.** Read it inside the callback (`new URLSearchParams(window.location.search)`).
3. **Put objects or arrays in `useEffect` dependencies.** New reference each render. Use primitives (ids, strings, numbers).
4. **Sync derived state with `useState` + `useEffect`.** Compute during render: `const fullName = first + ' ' + last`.
5. **Read client-only values (`window`, `localStorage`) while initializing state in code that renders on the server.** Causes hydration mismatch. See `references/react19-and-composition.md`.
6. **Use `forwardRef` on React 19.** `ref` is a regular prop.
7. **Pass inline callbacks or objects to memoized components** (defeats `memo`), unless the React Compiler is enabled.
8. **Run user interactions in `useEffect`.** Clicks and submits belong in event handlers.

## Before Optimizing Manually, Ask

1. Is the React Compiler on (`babel-plugin-react-compiler` in `package.json`, `reactCompiler` in `next.config.*`)? **Yes** -> do not hand-write `useMemo` / `useCallback` / `memo`; fix structure only. **No** -> apply the rules below.
2. Is this measured? Memoize only a profiled bottleneck.
3. Is it a waterfall or bundle problem? Those win over any re-render tweak.

## Priority Order (highest impact first)

| # | Category | Typical fix | Reference |
|---|---|---|---|
| 1 | **Waterfalls** (CRITICAL) | Parallel fetch, defer `await`, `<Suspense>` boundaries | `references/performance-and-waterfalls.md` |
| 2 | **Bundle size** (CRITICAL) | `optimizePackageImports`, next/dynamic, no barrel imports | `references/performance-and-waterfalls.md` |
| 3 | **Server** (HIGH) | Auth in actions, `React.cache`, `after()`, small RSC props | `references/server-components-and-actions.md` |
| 4 | **Client data** (MEDIUM) | SWR / React Query dedup; never `useEffect` fetch | `references/server-components-and-actions.md` |
| 5 | **Re-renders** (MEDIUM) | Derived state in render, functional `setState`, transitions | `references/react19-and-composition.md` |
| 6 | **Micro / JS** (LOW) | Hoist regex, Set/Map lookups, early exit | only if profiled |

## Selective Loading Rule

| Task | Load |
|---|---|
| Server vs Client split, data fetching, Server Actions, route handlers, auth, cookies/headers | `references/server-components-and-actions.md` |
| Slow pages, waterfalls, bundle size, images, Turbopack, PPR, caching matrix | `references/performance-and-waterfalls.md` |
| React 19 APIs, forms (`useActionState`), derived state, compound components, hydration | `references/react19-and-composition.md` |
| Metadata, cache layers and revalidation, project structure | `references/extended-reference.md` |

For generic hook and component patterns, also see the react-patterns skill.

## Core Rules

### Server vs Client
```
Needs useState / useEffect / event handlers / browser APIs?  -> Client Component ('use client')
Fetches data or reads secrets, no interactivity?             -> Server Component (default)
Both?                                                        -> Server parent fetches, small Client child interacts
```
Push `'use client'` down to the leaf that needs it. Pass only the fields a Client Component uses, not whole records.

### Routing File Conventions
| File | Purpose |
|---|---|
| `page.tsx` | Route UI |
| `layout.tsx` | Shared layout (persists across navigation) |
| `loading.tsx` | Streaming fallback (wraps the segment in Suspense) |
| `error.tsx` | Error boundary (must be a Client Component) |
| `not-found.tsx` | 404 UI |
| `route.ts` | Route Handler (no `page.tsx` in the same segment) |

Organization: route groups `(name)` group without changing the URL; parallel routes `@slot` render several pages in one layout; intercepting routes `(.)` give modal overlays. Next 15: `params` and `searchParams` are Promises, so `const { id } = await params`.

### Data and Mutations
- Reads: fetch in Server Components (parallel, see references). No `useEffect` fetching; on the client use SWR or React Query.
- Writes: Server Actions with `useActionState` for forms. **A Server Action is a public endpoint**: authenticate, authorize and validate (Zod) inside it.
- `(await cookies())`, `(await headers())` in Next 15+.
- Non-critical work after the response (logging, analytics, audit): `after()` from next/server.

### Loading, Errors, Suspense
Give every data-dependent segment a `loading.tsx` or a `<Suspense fallback>`, and an `error.tsx`. Wrap only the slow component in Suspense so the static shell paints immediately.

## Anti-Patterns

| Don't | Do |
|---|---|
| `'use client'` at the top of every file | Server by default, client at the leaves |
| Sequential `await` for independent data | `Promise.all` or sibling components under Suspense |
| Barrel imports from icon/UI libraries | `optimizePackageImports` or direct imports |
| Trusting middleware or layout for action auth | Check session inside each action |
| `useEffect` + `useState` to fetch or derive | Server fetch, SWR/Query, or compute in render |
| Passing a whole DB row to a Client Component | Pass the fields it renders |
| Module-level mutable variables holding request data | Pass data through props or `React.cache` |
| `useMemo` everywhere with Compiler enabled | Trust the compiler, profile first |

## Task Progress

- [ ] Step 0 done (versions, compiler, config)
- [ ] Server/Client split decided; `'use client'` only on leaves
- [ ] Data fetched in parallel; Suspense / `loading.tsx` / `error.tsx` in place
- [ ] Server Actions: auth + authorization + Zod validation inside; typed result
- [ ] No barrel imports; heavy components via next/dynamic
- [ ] NEVER list checked against the diff
- [ ] **Validator loop:** `tsc --noEmit` -> lint -> tests -> `next build` -> fix -> re-run until clean
