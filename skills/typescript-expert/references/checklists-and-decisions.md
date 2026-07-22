# TypeScript Code Review & Decision Support

## 1. Code Review Checklist

### Type Safety
- [ ] No implicit `any` (prefer `unknown`).
- [ ] Strict null checks handled.
- [ ] Explicit return types for public APIs.
- [ ] Branded types used for domain IDs.

### Organization
- [ ] Types co-located with implementation.
- [ ] No circular dependencies.
- [ ] Type-only imports used where appropriate (`import type { ... }`).
- [ ] Barrel exports (`index.ts`) used sparingly to avoid over-bundling.

---

## 2. Tooling Decision Trees

### Linter/Formatter
- **Biome**: Use for 100x speed and simplicity (all-in-one).
- **ESLint**: Use for complex, project-specific custom rules or non-TS frameworks.

### Testing Types
- Use **Vitest `expectTypeOf`** for general unit tests.
- Use **`tsd`** for standalone library type testing.

---

## 3. Migration Strategies

### JS to TS
1. Enable `allowJs` and `checkJs` in `tsconfig`.
2. Gradual rename `.js` → `.ts`.
3. Fix errors file-by-file starting with core utilities.

### Tool Migration
| Target | Effort | Why? |
|--------|--------|------|
| ESM | High | Future-proofing, node compatibility. |
| Nx | Medium | Caching and dependency graph. |
| Biome | Low | DX speed improvement. |

---

## 4. Error Pattern Solutions
- **"Inferred type cannot be named"**: Export the missing type or use `ReturnType`.
- **"Excessive stack depth"**: Use interface inheritance or break recursion with aliases.
