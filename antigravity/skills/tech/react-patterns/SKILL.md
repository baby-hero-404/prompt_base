---
name: react-patterns
description: "Use when building React applications, working with Hooks, composing components, or optimizing React performance."
allowed-tools: Read, Write, Edit, Glob, Grep
---

# React Patterns

> Principles for building production-ready React applications.

---

## 1. Component Design Principles

### Component Types

| Type | Use | State |
|------|-----|-------|
| **Server** | Default. Fetch data, access DB, pass serializable props. | None (Server side) |
| **Client** | Add `use client`. Interactivity, DOM access, React hooks. | useState, effects |
| **Presentational** | UI display | Props only |
| **Container** | Logic/state | Heavy state |

### Server vs. Client Decision Rule
- **Default to Server Components**.
- Only add `'use client'` when you need: interactivity (onClick), React state (useState), browser APIs (window), or custom hooks depending on state/effects.

### Design Rules

- One responsibility per component
- Props down, events up
- Composition over inheritance
- Prefer small, focused components

---

## 2. Hook Patterns

### When to Extract Hooks

| Pattern | Extract When |
|---------|-------------|
| **useLocalStorage** | Same storage logic needed |
| **useDebounce** | Multiple debounced values |
| **useFetch** | Repeated fetch patterns |
| **useForm** | Complex form state |

### Hook Rules

- Hooks at top level only
- Same order every render
- Custom hooks start with "use"
- Clean up effects on unmount

---

## 3. State Management Selection

| Complexity | Solution |
|------------|----------|
| Simple | useState, useReducer |
| Shared local | Context |
| Server state | React Query, SWR |
| Complex global | Zustand, Redux Toolkit |

### State Placement

| Scope | Where |
|-------|-------|
| Single component | useState |
| Parent-child | Lift state up |
| Subtree | Context |
| App-wide | Global store |

---

## 4. React 19 Patterns

### New Hooks

| Hook | Purpose |
|------|---------|
| **useActionState** | Form submission state |
| **useOptimistic** | Optimistic UI updates |
| **use** | Read resources in render |

### React Server Components (RSC) & Server Actions

- **RSC (Server Components):** The default in modern React. They never ship JS to the client, can safely access backend resources (DBs, file systems), and pass serializable data as props to Client Components. Use them for *fetching and rendering*.
- **Server Actions:** The modern way to mutate data. They are async functions executed on the server but callable directly from Client Components (e.g., `<form action={myServerAction}>`). They eliminate the need for manual API routes for form submissions.
  ```tsx
  // Server Action Example
  async function updateUser(formData: FormData) {
    'use server';
    const name = formData.get('name');
    await db.users.update({ name });
  }
  // Client usage: <form action={updateUser}>
  ```
- **Concurrent Rendering:** React can interrupt rendering to handle higher-priority updates (like typing). Use `useTransition` to mark non-urgent state updates, keeping the UI responsive during heavy renders or data fetching.
  ```tsx
  const [isPending, startTransition] = useTransition();
  const updateTab = (tab) => {
    startTransition(() => {
      setTab(tab); // Non-urgent update
    });
  };
  ```

### Compiler Benefits

- Automatic memoization (React Compiler)
- Less manual `useMemo`/`useCallback`
- Focus on pure components

---

## 5. Composition Patterns

### Compound Components

- Parent provides context
- Children consume context
- Flexible slot-based composition
- Example: Tabs, Accordion, Dropdown

### Render Props vs Hooks

| Use Case | Prefer |
|----------|--------|
| Reusable logic | Custom hook |
| Render flexibility | Render props |
| Cross-cutting | Higher-order component |

---

## 6. Performance Principles

### When to Optimize

| Signal | Action |
|--------|--------|
| Slow renders | Profile first |
| Large lists | Virtualize |
| Expensive calc | useMemo |
| Stable callbacks | useCallback |

### Optimization Order

1. Check if actually slow
2. Profile with DevTools
3. Identify bottleneck
4. Apply targeted fix

---

## 7. Error Handling

### Error Boundary Usage

| Scope | Placement |
|-------|-----------|
| App-wide | Root level |
| Feature | Route/feature level |
| Component | Around risky component |

### Error Recovery

- Show fallback UI
- Log error
- Offer retry option
- Preserve user data

---

## 8. TypeScript Patterns

### Props Typing

| Pattern | Use |
|---------|-----|
| Interface | Component props |
| Type | Unions, complex |
| Generic | Reusable components |

### Common Types

| Need | Type |
|------|------|
| Children | ReactNode |
| Event handler | MouseEventHandler |
| Ref | RefObject<Element> |

---

## 9. Testing Principles

| Level | Focus |
|-------|-------|
| Unit | Pure functions, hooks |
| Integration | Component behavior |
| E2E | User flows |

### Test Priorities

- User-visible behavior
- Edge cases

---

## 10. Modern UI Architecture (Pro Max)
 
### Tailwind CSS v4 Integration
- **CSS-first**: Prefer `@theme`, `@utility`, and `@container` queries.
- **Color Palettes**: Use semantic tokens over raw hex codes (e.g., `text-primary` not `text-blue-500`).
- **Dynamic Classes**: Avoid template literal logic for classes when possible; use `clsx` or `tailwind-merge`.

### Premium Component Patterns
- **Glassmorphism**: Use `backdrop-blur-md bg-white/10 border border-white/20`.
- **Micro-interactions**: Every button must have `active:scale-95 transition-all`.
- **Skeleton Loading**: Prefer custom SVGs or Tailwind-driven skeletons over generic spinners.

### Lucide Icons Standard
- Use `lucide-react` for all iconography.
- Standardize icon sizes: `size={20}` for standard, `size={16}` for inline, `size={24}` for highlights.

---

## 11. Testing & Quality
 
- **Vitest + Testing Library**: The modern standard for React unit tests.
- **Playwright**: For E2E flows and visual regression.
- **Accessibility**: Use `aria-*` attributes and test with `axe-core`.

Mandatory Quality Check:
```bash
python tools/lint_runner.py .
```

---

## 12. Decision Checklist

- [ ] **Functional or Class?** (Always functional/hooks)
- [ ] **Server or Client Component?** (Default to server)
- [ ] **State level correct?** (Lifted high enough?)
- [ ] **Tailwind v4 tokens used?**
- [ ] **Accessibility (Aria) labels included?**
- [ ] **Error boundaries placed?**
- [ ] **Tested in both Dark & Light mode?**

---

## 13. Anti-Patterns to Avoid

| ❌ Don't | ✅ Do |
|----------|-------|
| Giant `useEffect` with many deps | Primitive hooks or server actions |
| `any` types for props | Strict Interfaces / Generics |
| Hardcoded magic numbers | Use Design Tokens (Spacing/Colors) |
| Props drilling > 3 levels | Context API or Zustand |
| Ignoring `loading` states | Suspense or Shimmer/Skeleton |

---

> **Remember:** React is about composition and user experience. If it looks generic, it's not "Pro Max".
