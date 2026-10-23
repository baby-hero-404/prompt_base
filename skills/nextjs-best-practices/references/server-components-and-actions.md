# Server Components, Server Actions, Route Handlers

Next.js 15+ App Router. Check Step 0 in `SKILL.md` for the project's actual versions.

## 1. Server vs Client Components

| Use | Component |
|---|---|
| Data fetching, secrets, DB access, static content, layouts | **Server** (default) |
| `useState`, `useEffect`, event handlers, browser APIs, context providers | **Client** (`'use client'`) |
| Both | Server parent fetches; small Client child holds interaction |

Rules:
- `'use client'` marks a **module boundary**: everything it imports becomes client code. Keep it at the leaf (a button, a form field), not a page.
- Client Components can render Server Components passed as `children`/props. Use this to keep providers client-side while pages stay on the server.
- Server-only code (DB, secrets) belongs in modules that import `server-only` so a client import fails the build.
- Props crossing the boundary are serialized: pass only the fields the client renders.

```tsx
// BAD: serializes all 50 fields into the page payload
<Profile user={user} />
// GOOD
<Profile name={user.name} />
```

- Never keep request data in mutable module-level variables on the server. Renders run concurrently in one process, so request A can read request B's data. Pass data through props or `React.cache`.

## 2. Data Fetching

| Need | Pattern |
|---|---|
| Database / internal service | `await` directly in a Server Component or a data function |
| External API | `fetch` in a Server Component |
| Interactive refetch, polling, optimistic UI on the client | SWR or React Query (request dedup, cache) |
| Never | `useEffect` + `fetch` + `useState` for initial data |

Caching in Next 15: `fetch` is **uncached by default**. Opt in with `cache: 'force-cache'` or `next: { revalidate: 60, tags: ['posts'] }`. Route-level and `use cache` details live in `references/extended-reference.md`.

### Parallel Fetching
Server Components run sequentially down the tree. An `await` in a parent delays its children.

```tsx
// BAD: Sidebar waits for the header fetch
export default async function Page() {
  const header = await fetchHeader();
  return <div>{header}<Sidebar /></div>;
}

// GOOD: sibling async components fetch at the same time
export default function Page() {
  return <div><Header /><Sidebar /></div>;   // each does its own await
}

// GOOD: independent calls in one component
const [user, posts] = await Promise.all([getUser(id), getPosts(id)]);
```
For dependent chains, start the independent promise first and `await` it later; do not `await` unrelated work before starting it.

### Per-Request Dedup with `React.cache`
`fetch` calls with the same URL and options are memoized within a request. Non-fetch work (DB, auth, computation) is not; wrap it.

```ts
import { cache } from 'react';

export const getCurrentUser = cache(async () => {
  const session = await auth();
  return session?.user?.id ? db.user.findUnique({ where: { id: session.user.id } }) : null;
});
```
Call `getCurrentUser()` freely in layout, page, and components; it runs once per request. Pass **primitives** as arguments (`getUser(id)`); inline object arguments never hit the cache because equality is by reference.

### Async Request APIs (Next 15+)
```tsx
import { cookies, headers } from 'next/headers';

export default async function Page({ params, searchParams }: {
  params: Promise<{ id: string }>;
  searchParams: Promise<{ q?: string }>;
}) {
  const { id } = await params;
  const { q } = await searchParams;
  const theme = (await cookies()).get('theme')?.value;
  const ua = (await headers()).get('user-agent');
  /* ... */
}
```
Using `cookies()`, `headers()` or `searchParams` makes the route dynamic. Read them as late and as deep as possible, ideally inside a Suspense boundary, so the rest of the page can stay static.

## 3. Server Actions

Server Actions (`'use server'`) are **public HTTP endpoints**. Anyone can POST to them. Middleware, layout guards, and hidden buttons are not protection.

Order inside every action: **validate input -> authenticate -> authorize -> mutate -> revalidate -> return typed result**.

```ts
'use server';

import { z } from 'zod';
import { revalidatePath } from 'next/cache';
import { verifySession } from '@/lib/auth';

const schema = z.object({
  postId: z.string().uuid(),
  title: z.string().min(1).max(120),
});

export type ActionState = { ok: true } | { ok: false; error: string; fieldErrors?: Record<string, string[]> };

export async function updatePost(_prev: ActionState, formData: FormData): Promise<ActionState> {
  const parsed = schema.safeParse(Object.fromEntries(formData));
  if (!parsed.success) {
    return { ok: false, error: 'Invalid input', fieldErrors: parsed.error.flatten().fieldErrors };
  }

  const session = await verifySession();
  if (!session) return { ok: false, error: 'Unauthorized' };

  const post = await db.post.findUnique({ where: { id: parsed.data.postId } });
  if (!post || post.authorId !== session.user.id) return { ok: false, error: 'Forbidden' };

  await db.post.update({ where: { id: post.id }, data: { title: parsed.data.title } });
  revalidatePath('/posts');
  return { ok: true };
}
```

Rules:
- Treat every argument as untrusted (`unknown` -> Zod). IDs from the client are not proof of ownership; check against the session.
- Return expected failures as values (`{ ok: false, error }`); throw only for unexpected errors so `error.tsx` handles them.
- Never return secrets, raw errors, stack traces, or whole DB rows.
- Rate-limit sensitive actions (login, email send).
- Do not create actions inline in Client files that close over server secrets; define them in a `'use server'` module.
- Use actions for mutations from your own UI. Use a Route Handler for webhooks and third parties.

### Using an Action in a Form (React 19)
```tsx
'use client';
import { useActionState } from 'react';
import { updatePost, type ActionState } from './actions';

const initial: ActionState = { ok: true };

export function EditForm({ postId }: { postId: string }) {
  const [state, action, pending] = useActionState(updatePost, initial);
  return (
    <form action={action}>
      <input type="hidden" name="postId" value={postId} />
      <input name="title" required />
      {!state.ok && <p role="alert">{state.error}</p>}
      <button disabled={pending}>{pending ? 'Saving...' : 'Save'}</button>
    </form>
  );
}
```
Add `useOptimistic` for instant feedback and `useFormStatus` in a child button component when the pending state is needed deeper in the tree.

### Non-Blocking Work with `after()`
Run logging, analytics, audit trails and notifications after the response is sent.

```ts
import { after } from 'next/server';

export async function POST(request: Request) {
  await updateDatabase(request);

  after(async () => {
    const ua = (await headers()).get('user-agent') ?? 'unknown';
    await logUserAction({ ua });          // does not delay the response
  });

  return Response.json({ status: 'success' });
}
```
Works in Server Actions, Route Handlers and Server Components. It runs even if the response redirects or fails, so keep it idempotent and handle its own errors.

## 4. Route Handlers (`route.ts`)

| Method | Use |
|---|---|
| GET | Read (uncached by default in Next 15; opt in with `export const dynamic = 'force-static'`) |
| POST | Create, webhooks |
| PUT / PATCH | Update |
| DELETE | Remove |

```ts
export async function POST(request: Request) {
  const body = bodySchema.safeParse(await request.json().catch(() => null));
  if (!body.success) return Response.json({ error: 'Invalid body' }, { status: 400 });
  const session = await verifySession();
  if (!session) return Response.json({ error: 'Unauthorized' }, { status: 401 });
  /* ... */
  return Response.json(result, { status: 201 });
}
```
- Validate input with Zod, return correct status codes, handle errors without leaking internals.
- Start independent promises early and `await` late; do not chain unrelated awaits (`async-api-routes`).
- Prefer Node runtime unless you need Edge latency and your dependencies support it.
- Do not call your own Route Handler from a Server Component; call the underlying function directly.

## 5. Security Checklist

- [ ] Every Server Action and Route Handler validates, authenticates, authorizes.
- [ ] Secrets only in server modules (`server-only`), never in `NEXT_PUBLIC_*`.
- [ ] Only needed fields cross the Server/Client boundary.
- [ ] No request data in module-level mutable state.
- [ ] Responses never include raw errors or internal ids the user should not see.
