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
