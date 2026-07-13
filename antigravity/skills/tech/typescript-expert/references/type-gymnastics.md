# Advanced Type Gymnastics & Domain Modeling

## 1. Domain Modeling with Branded Types
Prevent "primitive obsession" by creating nominal types for critical domain IDs.

```typescript
type Brand<K, T> = K & { __brand: T };
type UserId = Brand<string, 'UserId'>;
type OrderId = Brand<string, 'OrderId'>;

function processOrder(orderId: OrderId, userId: UserId) { }
```

---

## 2. Advanced Conditional Types

### Recursive Type Manipulation
```typescript
type DeepReadonly<T> = T extends (...args: any[]) => any 
  ? T 
  : T extends object 
    ? { readonly [K in keyof T]: DeepReadonly<T[K]> }
    : T;
```

### Template Literal Types
```typescript
type PropEventSource<Type> = {
  on<Key extends string & keyof Type>
    (eventName: `${Key}Changed`, callback: (newValue: Type[Key]) => void): void;
};
```

---

## 3. Type Inference & Safety

### `satisfies` Operator
Preserves literal types while ensuring they meet a specific interface.
```typescript
const config = {
  api: "https://api.example.com",
  timeout: 5000
} satisfies Record<string, string | number>;
```

### Inferred Type Predicates (TS 5.5+)
Functions returning booleans now automatically infer type predicates, reducing manual `is T` casting.
```typescript
const isString = (x: unknown) => typeof x === "string";
const strs = ["a", 1, "b"].filter(isString); // inferred as string[] in TS 5.5+
```

### Const Assertions
```typescript
const routes = ['/home', '/about'] as const;
type Route = typeof routes[number]; // '/home' | '/about'
```

---

## 4. Solving Complex Recursive Errors
**Issue**: "Type instantiation is excessively deep"
**Fix**: Limit recursion depth manually using a counter or tuple indexing.
```typescript
type NestedArray<T, D extends number = 5> = 
  D extends 0 ? T : T | NestedArray<T, [-1, 0, 1, 2, 3, 4][D]>[];
```
