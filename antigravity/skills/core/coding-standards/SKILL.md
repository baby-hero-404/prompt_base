---
name: coding-standards
description: "Use when writing or refactoring any code to ensure it meets pragmatic coding standards for conciseness, directness, and modern practices."
allowed-tools: Read, Write, Edit
version: 3.1
priority: CRITICAL
---

# Clean Code - Standards & Fundamentals

> **Definition**: Code is clean if it can be understood easily by everyone on the team. It can be read and enhanced by a developer other than its original author. With understandability comes readability, changeability, extensibility, and maintainability.

---

## 1. Core Principles & General Rules

| Principle | Rule |
|-----------|------|
| **SRP** | Single Responsibility - each function/class does ONE thing. |
| **DRY** | Don't Repeat Yourself - extract duplicates, reuse. |
| **KISS** | Keep It Simple - the simplest solution is always better. Reduce complexity. |
| **YAGNI** | You Aren't Gonna Need It - don't build unused features. |
| **Boy Scout** | Leave the campground cleaner than you found it. |
| **Root Cause** | Always look for and fix the root cause, not just the symptom. |
| **Conventions** | Follow standard team/language conventions consistently. |
| **Fail Fast** | Validate early, throw early, recover gracefully. |

---

## 2. Design Rules

- **High-Level Config**: Keep configurable data at high levels (constants, env, config files).
- **Polymorphism**: Prefer polymorphism to `if/else` or `switch/case` for behavior selection.
- **Async/Threading**: Separate multi-threading or async orchestration code from business logic.
- **Dependency Injection**: Use DI to decouple classes from their direct dependencies.
- **Law of Demeter**: A class should know only its direct dependencies (don't reach through objects).
- **Prevent Over-Configurability**: Avoid adding too many options that aren't actually needed.
- **Base/Derivatives**: Base classes should know nothing about their derivatives.

---

## 3. Understandability & Logic

- **Consistency**: Doing similar things in the same way reduces cognitive load.
- **Explanatory Variables**: Use variables to break down complex expressions (Self-documenting).
- **Encapsulate Boundaries**: Put boundary condition processing in one dedicated place.
- **Value Objects**: Prefer dedicated value objects to primitive types (Primitive Obsession).
- **Logical Dependencies**: Avoid methods that work only if something else in the class is in a specific state.
- **Positive Conditionals**: Favor `if (shouldShow)` over `if (!isHidden)`.

---

## 4. Modern Tech Mandate (Priority Stack)

> **RULE**: Always prioritize modern, high-performance libraries and stable, next-generation frameworks. Avoid legacy patterns (e.g., use Next.js 15 over CRA, Tailwind v4 over CSS-in-JS).

### 4.1 Frontend Preferred
| Category | Preferred | Avoid |
|----------|-----------|-------|
| **Framework** | Next.js 15+ (App Router) | Create React App |
| **Styling** | Tailwind CSS v4 | CSS Modules, Styled-Comp |
| **State** | TanStack Query + Zustand | Redux (legacy) |
| **Animation** | Framer Motion | GSAP (unless complex) |
| **Components** | shadcn/ui + Radix | MUI, Ant Design |

### 4.2 Backend & Data Preferred
| Category | Preferred | Avoid |
|----------|-----------|-------|
| **Runtime** | Bun, Node.js 22+ | Node < 20 |
| **Framework** | Hono, Fastify | Express |
| **Validation** | Zod | Joi, Yup |
| **ORM** | Drizzle | Prisma (if speed-critical), TypeORM |
| **SQL** | Neon, Turso | Local-only SQLite |

---

## 5. TypeScript Standards

- **Strict Mode**: Mandatory `strict: true` and `noUncheckedIndexedAccess`.
- **Typing**: No `any`. Use `unknown` for external data. Let TS infer when obvious.
- **Organization**: Group imports (external → internal → absolute aliases → types).

---

## 6. Naming Conventions

- **Descriptive**: Choose unambiguous, pronounceable, and searchable names.
- **Meaningful Distinction**: Avoid `data1`, `data2` or `info`. Make distinctions clear.
- **Booleans**: Always use question forms: `isLoading`, `hasPermission`, `canEdit`.
- **Constants**: SCREAMING_SNAKE for magic numbers or global config.
- **No Encodings**: Don't append type info (e.g., no `strName` or `iCount`).

---

## 7. Function Rules

- **Small**: Aim for 5-15 lines. Do **one** thing.
- **Arguments**: Prefer 0-2. Max 3. Use objects for multiple parameters.
- **No Flags**: Split flag-based methods into independent methods.
- **No Side Effects**: A function should not change hidden state outside its scope.
- **Guard Clauses**: Use early returns to reduce nesting.

```typescript
// ✅ Good - Guard clauses first
function processUser(user: User | null) {
  if (!user) return null;
  if (!user.isActive) return { error: 'inactive' };
  return processValidUser(user);
}
```

---

## 8. Source Code Structure

- **Vertical Density**: Related code should be physically close. Declare variables near usage.
- **Caller Above Callee**: Place functions in downward direction (Caller first).
- **Vertical Separation**: Use blank lines to separate distinct concepts.
- **No Horizontal Alignment**: Avoid white space padding for variable alignment.

---

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
