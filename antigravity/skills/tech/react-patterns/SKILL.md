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


## Extended References
For less-frequently-needed detail, see [`references/extended-reference.md`](references/extended-reference.md):
- Render Props vs Hooks
- 6. Performance Principles
- When to Optimize
- Optimization Order
- 7. Error Handling
- Error Boundary Usage
- Error Recovery
- 8. TypeScript Patterns
- Props Typing
- Common Types
- 9. Testing Principles
- Test Priorities
- 10. Modern UI Architecture (Pro Max)
- Tailwind CSS v4 Integration
- Premium Component Patterns
- Lucide Icons Standard
- 11. Testing & Quality
- 12. Decision Checklist
- 13. Anti-Patterns to Avoid
