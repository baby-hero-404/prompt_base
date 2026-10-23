# React 19 APIs and Composition

Applies to React 19+. On React 18 use the older forms (`forwardRef`, `useContext`, `useFormState`) and skip React 19 items. See also the react-patterns skill for general hook guidance.

## 1. React 19 API Changes

| Old | React 19 |
|---|---|
| `forwardRef((props, ref) => ...)` | `ref` is a normal prop |
| `useContext(Ctx)` | `use(Ctx)` (can be called conditionally) |
| `<Ctx.Provider value>` | `<Ctx value>` |
| `useFormState` | `useActionState` |
| Manual pending/error state for mutations | `useActionState`, `useFormStatus`, `useOptimistic`, `useTransition` with async functions |
| `<title>` via helper libraries | Render `<title>`, `<meta>`, `<link>` in components; Next Metadata API remains the Next.js way |

```tsx
// ref as a prop (no forwardRef)
function Input({ ref, ...props }: React.ComponentProps<'input'>) {
  return <input ref={ref} {...props} />;
}

// use() reads context, even conditionally
function Panel({ show }: { show: boolean }) {
  if (!show) return null;
  const theme = use(ThemeContext);
  return <div className={theme.panel} />;
}
```
`use(promise)` unwraps a promise created in a Server Component and passed to a Client Component, under a Suspense boundary. Do not create the promise during the Client Component's render.

## 2. Derived State: Compute, Do Not Sync

```tsx
// BAD: double render, stale intermediate state
const [fullName, setFullName] = useState('');
useEffect(() => setFullName(first + ' ' + last), [first, last]);

// GOOD
const fullName = first + ' ' + last;

// Expensive and Compiler is OFF and measured: useMemo
const visible = useMemo(() => items.filter(match(query)), [items, query]);
```
To reset state when a prop changes, change the component `key`, or store the previous value and compare during render, instead of an effect.

## 3. Effects

- Effects synchronize with **external systems** (subscriptions, timers, non-React widgets). They are not for deriving data, handling clicks, or fetching initial data.
- Dependencies must be primitives. If you need an object, depend on the fields you read, or build the object inside the effect.
- User actions go in event handlers.
- `useEffectEvent` (React 19.2+) reads the latest props/state inside an effect without making them dependencies; check the installed version.
- Always return a cleanup for subscriptions and timers.

## 4. State Updates

```tsx
// functional update: stable callback, no state in deps
const add = useCallback((item: Item) => setItems(prev => [...prev, item]), []);

// lazy initializer for expensive initial values
const [index] = useState(() => buildIndex(rows));

// non-urgent updates keep input responsive
const [isPending, startTransition] = useTransition();
startTransition(() => setFilter(value));
```
Use `useDeferredValue` for values that feed expensive renders. Use `useRef` for values that change often but do not affect rendering (mouse position, timers).

## 5. Memoization Policy

- React Compiler enabled: write plain code. Do not add `useMemo`, `useCallback`, `memo` for performance. Follow its rules (pure components, no mutation during render, destructure props/objects used as dependencies).
- Compiler off: memoize only profiled hot spots. `memo` helps only if props are stable; do not pass inline objects/functions to a memoized child. Hoist constant objects and static JSX to module scope. Extract components for non-primitive default props.

## 6. Hydration

Server and first client render must match.

```tsx
// BAD: throws on the server, mismatches on the client
const theme = localStorage.getItem('theme') ?? 'light';
```
Options:
- Store such preferences in a **cookie** and read `(await cookies())` on the server.
- For theme/flicker cases, inject a tiny inline script before hydration that sets a class/attribute, and use `suppressHydrationWarning` only on that element (known, intentional mismatch).
- Render a stable placeholder first and update in an effect only for non-critical UI.
- Never read `window`, `document`, `Date.now()`, `Math.random()` during render of server-rendered output.

## 7. Composition Patterns

### Avoid boolean-prop explosions
```tsx
// BAD: combinatorial props
<Button primary large outlined loading rounded />

// GOOD: explicit variants
<Button variant="primary" size="lg" />
// or separate components: <PrimaryButton />, <GhostButton />
```

### Compound components
Share state through context; consumers compose the parts.
```tsx
const Ctx = createContext<{ open: boolean; setOpen: (v: boolean) => void } | null>(null);

function Dialog({ children }: { children: ReactNode }) {
  const [open, setOpen] = useState(false);
  return <Ctx value={{ open, setOpen }}>{children}</Ctx>;
}
Dialog.Trigger = function Trigger({ children }: { children: ReactNode }) {
  const ctx = use(Ctx)!;
  return <button onClick={() => ctx.setOpen(true)}>{children}</button>;
};
Dialog.Content = function Content({ children }: { children: ReactNode }) {
  const ctx = use(Ctx)!;
  return ctx.open ? <div role="dialog">{children}</div> : null;
};
```
Define a typed context interface (state, actions, meta) so the provider implementation (local state, global store, server data) can change without touching consumers.

### Prefer `children` over render props
Use `children` and slots for static composition; use render props only when the parent must pass data back to the child.

### Lift state, decouple implementation
Put state in the lowest common provider. Components depend on the context interface, not on how the state is stored.

### Never define components inside components
Hoist to module scope or pass as props; inner definitions remount every render.

## 8. Forms (Next + React 19)

- Use `<form action={serverAction}>` with `useActionState`; see `references/server-components-and-actions.md` for the validated action.
- Progressive enhancement: forms work before hydration when `action` is a Server Action.
- Show `pending` state, field errors, and a reset path. Use `useOptimistic` only when rollback on failure is handled.
- Keep controlled inputs for live validation only; prefer uncontrolled inputs and `FormData` otherwise.

## 9. Review Checklist

- [ ] No `forwardRef`, no `useContext` on React 19 code
- [ ] No effect-based derived state or effect-based initial fetching
- [ ] Effect deps are primitives; every subscription has cleanup
- [ ] No component defined inside another component
- [ ] No server/client mismatch sources in render
- [ ] Memoization matches the Compiler setting (Step 0)
