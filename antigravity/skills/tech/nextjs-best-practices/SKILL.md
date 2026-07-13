---
name: nextjs-best-practices
description: "Use when developing Next.js App Router applications, implementing Server Components, or defining data fetching and routing."
allowed-tools: Read, Write, Edit, Glob, Grep
---

# Next.js Best Practices

> **Target Version: Next.js 15+**
> Principles for modern Next.js App Router development.

---

## 1. Server vs Client Components

### Decision Tree

```
Does it need...?
│
├── useState, useEffect, event handlers
│   └── Client Component ('use client')
│
├── Direct data fetching, no interactivity
│   └── Server Component (default)
│
└── Both? 
    └── Split: Server parent + Client child
```

### By Default

| Type | Use |
|------|-----|
| **Server** | Data fetching, layout, static content |
| **Client** | Forms, buttons, interactive UI |

---

## 2. Data Fetching Patterns

### Fetch Strategy

| Pattern | Use |
|---------|-----|
| **Default (Next 15+)** | Dynamic (Uncached by default, every request) |
| **Cached (`force-cache`)** | Static (cached at build) |
| **Revalidate** | ISR (time-based refresh using `next.revalidate`) |

### Data Flow

| Source | Pattern |
|--------|---------|
| Database | Server Component fetch |
| API | fetch with caching |
| User input | Client state + server action |

---

## 3. Routing Principles

### File Conventions

| File | Purpose |
|------|---------|
| `page.tsx` | Route UI |
| `layout.tsx` | Shared layout |
| `loading.tsx` | Loading state |
| `error.tsx` | Error boundary |
| `not-found.tsx` | 404 page |

### Route Organization

| Pattern | Use |
|---------|-----|
| Route groups `(name)` | Organize without URL |
| Parallel routes `@slot` | Multiple same-level pages |
| Intercepting `(.)` | Modal overlays |

---

## 4. API Routes

### Route Handlers

| Method | Use |
|--------|-----|
| GET | Read data |
| POST | Create data |
| PUT/PATCH | Update data |
| DELETE | Remove data |

### Best Practices

- Validate input with Zod
- Return proper status codes
- Handle errors gracefully
- Use Edge runtime when possible

---

## 5. Performance Principles

### Image Optimization

- Use next/image component
- Set priority for above-fold
- Provide blur placeholder
- Use responsive sizes

### Bundle Optimization

- Dynamic imports for heavy components
- Route-based code splitting (automatic)
- Analyze with bundle analyzer

### Turbopack & Rendering
- **Turbopack:** Use `next dev --turbo` for significantly faster local dev.
- **Partial Prerendering (PPR):** Wrap dynamic components in `<Suspense>` so the static shell can be served instantly while dynamic parts stream in.

---

## 6. Metadata


## Extended References
For less-frequently-needed detail, see [`references/extended-reference.md`](references/extended-reference.md):
- Static vs Dynamic
- Essential Tags
- 7. Caching Strategy
- Cache Layers
- Revalidation
- 8. Server Actions
- Use Cases
- Best Practices
- 9. Anti-Patterns
- 10. Project Structure
