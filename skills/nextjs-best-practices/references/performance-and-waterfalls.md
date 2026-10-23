# Performance and Waterfalls

Order of attack: **1. waterfalls, 2. bundle size, 3. server work, 4. client re-renders, 5. micro-optimizations.** Measure first (Network panel, `next build` output, bundle analyzer, React DevTools Profiler, Vercel Speed Insights if present).

## 1. Eliminate Waterfalls (CRITICAL)

A waterfall is work that waits on something it does not depend on.

### Defer `await` until the branch that needs it
```ts
// BAD: always waits for userData, even when skipping
async function handle(userId: string, skip: boolean) {
  const userData = await fetchUserData(userId);
  if (skip) return { skipped: true };
  return process(userData);
}

// GOOD
async function handle(userId: string, skip: boolean) {
  if (skip) return { skipped: true };
  return process(await fetchUserData(userId));
}
```
Order guards so cheap checks come before expensive ones: fetch the resource (404 check) before fetching permissions.

### Cheap synchronous condition before an async flag
```ts
// BAD: pays for the flag call even when the cheap guard fails
const enabled = await getFlag();
if (enabled && isPremiumRoute) { /* ... */ }

// GOOD
if (isPremiumRoute) {
  const enabled = await getFlag();
  if (enabled) { /* ... */ }
}
```
Keep the original order only if the cheap condition is itself expensive, depends on the flag, or side effects must run in order.

### Parallelize independent work
```ts
const [user, posts, flags] = await Promise.all([getUser(id), getPosts(id), getFlags()]);
```
For partial dependencies, start promises early: `const a = fetchA(); const b = await fetchB(); const c = await fetchC(await a);`. In Server Components prefer sibling async components (see `references/server-components-and-actions.md`).

### Stream with Suspense boundaries
```tsx
// BAD: whole page waits for one slow query
export default async function Page() {
  const data = await fetchData();
  return <Layout><Data data={data} /></Layout>;
}

// GOOD: shell paints now, slow part streams in
export default function Page() {
  return (
    <Layout>
      <Suspense fallback={<Skeleton />}>
        <Data />            {/* async component that awaits its own data */}
      </Suspense>
    </Layout>
  );
}
```
Place boundaries around slow or dynamic components, not around the whole page. `loading.tsx` is a Suspense boundary for the segment. With Partial Prerendering (`cacheComponents` / `experimental.ppr`, check version) the static shell is served immediately and dynamic holes stream.

## 2. Bundle Size (CRITICAL)

### Barrel imports
Barrel files (`index.ts` re-exporting hundreds or thousands of modules) make dev boot, builds and cold starts slow (200-800 ms import cost for large icon/UI libraries). Affected: `lucide-react`, `@mui/material`, `@mui/icons-material`, `react-icons`, `@tabler/icons-react`, `@headlessui/react`, `lodash`, `date-fns`, `rxjs`.

Preferred fix (Next 13.5+): keep normal imports, let the compiler rewrite them.
```js
// next.config.js
module.exports = {
  experimental: { optimizePackageImports: ['lucide-react', '@mui/material'] },
};
```
Fallback (non-Next or unsupported library): import from the specific module path, e.g. `import Button from '@mui/material/Button'`. Some packages ship no types for deep paths, which gives an implicit `any` under `strict`; check that `tsc --noEmit` stays clean before using deep imports. Many libraries are already optimized by Next by default; check the config first.

### Dynamic imports for heavy client code
```tsx
import dynamic from 'next/dynamic';

const Editor = dynamic(() => import('./Editor'), { ssr: false, loading: () => <Skeleton /> });
const Chart = dynamic(() => import('./Chart'));
```
Use for editors, charts, PDF viewers, maps, modals opened rarely. `ssr: false` is only allowed in Client Components. Load behind a condition (open modal, feature flag) rather than on every page.

### Other bundle rules
- Defer non-critical third-party scripts: `<Script strategy="lazyOnload">` or `afterInteractive`.
- Preload on intent (hover/focus) for likely next interactions.
- Avoid dynamic `import(variable)` paths that make the bundler include whole folders.
- Analyze: `ANALYZE=true next build` with `@next/bundle-analyzer`, or `next experimental-analyze` on versions that include it. Check what Client Components pull in.

## 3. Server Work (HIGH)

- Deduplicate DB/auth calls with `React.cache` (primitive args).
- Hoist static I/O (fonts, config, templates read from disk) to module scope so it runs once per process; never hoist per-request data.
- Use `after()` for logging and analytics.
- Keep RSC payloads small: pass fields, not records.
- Cross-request cache for hot data: tag-based revalidation or an LRU where `React.cache` (per request) is not enough.

## 4. Dynamic vs Cached Data (Next 15)

| Goal | How |
|---|---|
| Always fresh (default) | `fetch(url)` with no options, or `cache: 'no-store'` |
| Static at build | `fetch(url, { cache: 'force-cache' })` or `export const dynamic = 'force-static'` |
| Time-based refresh (ISR) | `fetch(url, { next: { revalidate: 60 } })` or `export const revalidate = 60` |
| On-demand refresh | `next: { tags: ['posts'] }` then `revalidateTag('posts')` / `revalidatePath('/posts')` in an action |
| Opt a function into caching | `use cache` directive (requires `cacheComponents`; check the Next version and config) |

Reading `cookies()`, `headers()`, `searchParams` or using `no-store` makes that route dynamic. Isolate such reads in small Suspense-wrapped components to keep the rest cacheable.

## 5. Images and Fonts

```tsx
import Image from 'next/image';
<Image src={hero} alt="..." priority sizes="(max-width: 768px) 100vw, 50vw" placeholder="blur" />
```
- Use the Image component for all content images; set `width`/`height` (or `fill` with a sized parent) to prevent layout shift.
- `priority` only for the LCP image (above the fold).
- Provide `sizes` for responsive images; allow remote hosts in `images.remotePatterns`.
- Use `next/font` (self-hosted, no layout shift) instead of a CSS `@import` of web fonts.

## 6. Development and Rendering

- Turbopack: `next dev --turbo` (default dev bundler on newer Next versions; verify).
- Static shell + streaming via Suspense / PPR for pages mixing static and personalized content.
- Move work off the critical path: `after()`, `requestIdleCallback`, deferred scripts.

## 7. Client Re-render Rules (when Compiler is OFF)

See `references/react19-and-composition.md`. Short list: derive state during render, functional `setState`, primitive effect deps, no inline components, `useTransition` for non-urgent updates, `memo` only for profiled hot components with stable props.

## 8. Micro-optimizations (only if profiled)

Combine iterations, early exit, `Set`/`Map` for lookups, hoist RegExp creation, `toSorted()` instead of mutating `sort()`, cache repeated property access in hot loops. Never trade clarity for these without a measurement.

## Task Progress (slow page)

- [ ] Reproduce and measure (Network waterfall, LCP, TTFB, bundle report)
- [ ] Find sequential awaits and parent-child fetch chains; parallelize or move into Suspense
- [ ] Check client bundle for barrel imports and heavy libraries; apply `optimizePackageImports` / `next/dynamic`
- [ ] Check cache mode per fetch and per route (dynamic by accident?)
- [ ] Re-measure; keep only changes that help
