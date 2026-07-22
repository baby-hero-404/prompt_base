## 9. Objects & Data Structures

- **Hide Internals**: Objects should hide structure (encapsulation). Data structures (DTOs) expose it.
- **No Hybrids**: Avoid structures that are half-object and half-data.
- **Small Classes**: Focus on one thing with few instance variables.
- **Prefer Non-Static**: Use instance methods when behavior depends on state.

---

## 10. Error Handling

- **Result Pattern**: Prefer `{ success: true, data: T } | { success: false, error: E }`.
- **Never Swallow**: Treat catch blocks as mandatory handlers. No empty catches.
- **Contextual Errors**: Wrap errors with context (e.g., `fmt.Errorf` in Go or custom Error classes in TS).

---

## 11. Comments Rules

- **Explain in Code**: Code should be self-explanatory. Re-write before commenting.
- **Why, not What**: Only comment to explain *intent* or *reasoning* for non-obvious code.
- **No Noise**: Delete commented-out code. Avoid "closing brace" markers.
- **JSDoc**: Use only for public-facing Library/API documentation.

---

## 12. Quality & Tests (FIRST)

- **Fast**: Tests must run quickly.
- **Independent**: Tests should not depend on each other.
- **Repeatable**: Must work in any environment, every time.
- **Self-Validating**: Clear pass/fail result.
- **Timely**: Written just before (TDD) or with production code.
- **Readable**: Test code is as important as production code.

---

## 13. File & Folder Structure

- **Feature-Based**: Colocate components, hooks, api, and types inside a feature folder.
- **Colocation**: Keep code as close as possible to where it's used.
- **Shared**: Use `shared/` for truly global utilities and `lib/` for third-party wrappers.
- **Single Responsibility (File Level)**: A file must answer the question: *"What is this file responsible for?"* If the answer takes more than one sentence, it should be split into multiple files.

---

## 14. Code Smells (Red Flags)

- **Rigidity**: Hard to change; small changes cause a cascade of effects.
- **Fragility**: Easily breaks in many places due to a single change.
- **Immobility**: Code can't be reused because it's too coupled.
- **Needless Complexity**: Over-engineered solutions for simple problems.
- **Opacity**: Hidden intent or difficult-to-understand logic.

---

## 15. Security & Performance Checklist

- **Security**: Validate with Zod at every boundary. No `dangerouslySetInnerHTML`. No secrets in source.
- **React Performance**: Server Components first. Memoize heavy calcs. Debounce user input.
- **Data Fetching**: Parallelize independent requests. Use TanStack Query for caching.
- **Dependencies**: Audit bundle size and maintenance before adding packages.

---

## 16. Clean Code by Language
 
### 16.1 TypeScript
- Use **Zod** for all I/O boundary validation.
- Exhaustive switch checks with `never` type.
- Prefer `interface` for shapes, `type` for unions/aliases.
 
### 16.2 Python
- Use **Pydantic v2** for schemas.
- Mandatory type hints (PEP 484).
- Use **Ruff** for lint/fmt and **uv** for management.
 
### 16.3 Go
- Errors are values; check them immediately.
- Accept interfaces, return structs.
- Concurrency: Know how goroutines stop. Use `context.Context`.

---

## 17. Quick Reference

### 17.1 Component Template
```typescript
import type { ComponentProps } from 'react';

interface ButtonProps extends ComponentProps<'button'> {
  variant?: 'primary' | 'secondary';
  isLoading?: boolean;
}

export function Button({ 
  variant = 'primary',
  isLoading = false,
  children,
  ...props 
}: ButtonProps) {
  if (isLoading) return <LoadingButton />;
  return <button className={cn(styles[variant])} {...props}>{children}</button>;
}
```

---

> **Remember:** Clean code is about making code **easy to read, easy to change, and hard to break**. Use modern tools to achieve this with less effort.
