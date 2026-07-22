# TypeScript Performance & Monorepo Architecture

## 1. Type Checking Performance

### Diagnostics
```bash
npx tsc --extendedDiagnostics --incremental false | grep -E "Check time|Files:|Lines:"
```

### Common Fixes
1. **Interfaces > Intersections**: `interface X extends Y` is faster for the compiler than `type X = Y & Z`.
2. **skipLibCheck**: Enable `true` in `tsconfig` to skip checking `.d.ts` files in node_modules.
3. **Incremental**: Enable `incremental: true` to cache build info.

---

## 2. Monorepo Management (Nx vs Turbo)

- **Turborepo**: Choose for simple speed, caching, and <20 packages.
- **Nx**: Choose for complex dependencies, visualization, and >50 packages.

### Project References (Composite)
Mandatory for large monorepos to allow incremental compilation of packages.
```json
{
  "references": [{ "path": "./packages/core" }],
  "compilerOptions": { "composite": true }
}
```

---

## 3. ESM vs CJS
- Use `"type": "module"` in `package.json`.
- Use `"moduleResolution": "bundler"` for modern toolstacks.
- **Top-level await**: Native in ESM, but check target environment compatibility.

---

## 4. Debugging Module Resolution
```bash
npx tsc --traceResolution > resolution.log 2>&1
npx tsc --generateTrace trace
```
Use `@typescript/analyze-trace` to visualize compile-time bottlenecks.
