# Flutter Performance Optimization

## 1. Targeted Rebuilds (Stop `setState` Overuse)

### 🚫 Global `setState` (AVOID)
Rebuilds the entire widget tree.
- ✅ **ALWAYS** use targeted state management like `ValueListenableBuilder` or Riverpod's `ref.watch(provider.select(...))`.

### 2. The `const` Revolution
`const` constructors prevent widgets from rebuilding when their parent does.
- ✅ Use `const` on **EVERY** widget possible.

---

## 2. ListView Optimization

### 🚫 `ListView` with children
Renders all children at once.
- ✅ **ALWAYS** use `ListView.builder` for lazy rendering.
- ✅ Provide `itemExtent` for fixed-height items to bypass layout calculation.
- ✅ Use `ListView.separated` for lists with dividers.

---

## 3. Image & Asset Hygiene

### Caching & Sizing
- Use `CachedNetworkImage`.
- Set `memCacheWidth` and `memCacheHeight` to avoid loading massive images into memory.

---

## 4. Lifecycle Management

- **Dispose Pattern**: Always call `.dispose()` on `AnimationController`, `TextEditingController`, and cancel `StreamSubscription` in the `dispose()` method.
- **Reverse Order**: Dispose in reverse order of creation.

---

## 5. Summary Checklist

- [ ] `const` used wherever possible?
- [ ] `ListView.builder` used for long lists?
- [ ] All controllers and subscriptions disposed?
- [ ] Targeted rebuilds (not global `setState`)?
- [ ] Tested in `profile` mode (Dev mode performance is not representative)?
