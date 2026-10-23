---
name: golang-best-practices
description: "Use when writing or refactoring Go (Golang) code, implementing goroutines/channels, handling errors and context, accessing databases (database/sql, GORM), or structuring Go projects. Triggers on golang, goroutine, errgroup, gorm, go.mod, go test."
allowed-tools: Read, Write, Edit, Glob, Grep, Bash
references: [concurrency-and-lifecycle.md, ddd-and-architecture.md, db-and-transactions.md, testing-and-quality.md]
---

# Golang Best Practices

> **Philosophy:** Concrete types first, small interfaces where callers benefit, no goroutine without an owner. Simplicity over cleverness; explicit over implicit; errors are values.

---

## Step 0: Read the project first (MANDATORY)

1. Read `go.mod`: the `go` directive (this skill targets **Go 1.27+**; if a module is older, say so and stop to ask), module path, key dependencies (router, ORM, logger, test libs).
2. Check for `.golangci.yml`, `Makefile`, CI config. Use the project's lint and test commands.
3. Follow the existing layout, router, ORM and logging choices. Apply the defaults below to new code or when there is no convention.
4. Do not add a dependency the standard library already covers. Ask before adding one, and pin its version.

## NEVER Do (Go Footguns)

1. **Start a goroutine with no owner or exit.** Every `go` needs a stop condition (context, closed channel) and something that waits for it.
2. **Store `context.Context` in a struct.** Pass `ctx` as the first parameter of every function that does I/O or blocks.
3. **Ignore an error** (`_ = f()`, unchecked `Close`, `Scan`, `Rollback` without a reason). Handle it, return it wrapped, or document why it is safe to drop.
4. **Compare errors by string.** Use `errors.Is` and `errors.As`.
5. **Use `panic` for business errors.** Panic is for programmer bugs and failed startup invariants. Return `error` elsewhere.
6. **Create an interface before a second need exists.** One implementation and no test seam means use the struct.
7. **Share a slice's backing array by accident.** `append` and re-slicing can overwrite a sibling; copy when ownership is unclear.
8. **Copy large structs or lock-containing structs by value** on hot paths (`sync.Mutex` must never be copied; use pointers).
9. **Mutate maps or counters from several goroutines without sync.** Run `go test -race`.
10. **Leak resources.** `defer resp.Body.Close()`, `defer rows.Close()`, `defer cancel()` right after the call that creates them.

## Concrete Types First

- Start with a struct and functions. Introduce an interface when there are **2+ implementations**, or a consumer needs a **test seam**.
- Define the interface **in the consumer's package**, with only the methods that consumer calls (usually 1-3).
- "Accept interfaces, return structs": parameters can be small interfaces; constructors return concrete types.
- Do not export an interface just to mock your own package.

## Errors

1. **Wrap with context:** `fmt.Errorf("create user %q: %w", email, err)`
2. **Sentinels** for conditions callers branch on: `var ErrNotFound = errors.New("not found")`; check with `errors.Is`.
3. **Typed errors** for data callers need: `errors.As(err, &target)`.
4. **Handle once:** log or return, never both. Log at the boundary (handler, main).
5. Combine independent errors with `errors.Join`.

## Selective Loading Rule

| Task | Load |
|---|---|
| Goroutines, channels, context, errgroup, worker pools, graceful shutdown, races | `references/concurrency-and-lifecycle.md` |
| Project layout, optional DDD layers, dependency injection, HTTP server and middleware | `references/ddd-and-architecture.md` |
| SQL, GORM, transactions, migrations, connection pool | `references/db-and-transactions.md` |
| Table tests, mocks, integration tests, coverage, benchmarks, lint | `references/testing-and-quality.md` |

## Concurrency Quick Rules

1. Never start a goroutine without knowing how it stops.
2. Pass `ctx` to everything blocking or long-running.
3. Channels for orchestration and ownership transfer; mutexes for protecting state.
4. Default channel size 0 or 1; a bigger buffer needs a stated bound and reason.

| Pattern | Use | Tool |
|---|---|---|
| Worker pool | Bound CPU/DB use | channel + WaitGroup, or errgroup with `SetLimit` |
| Fan-out, first error cancels all | Parallel calls | errgroup.WithContext |
| First response wins | Hedged requests | `select` + context |
| Pipeline | Stream stages | channels, close by producer |
| Rate limiting | Protect services | x/time/rate limiter |

## Modern Go (baseline 1.27+)

Use the modern idioms directly; do not write workarounds for older versions.
- Standard library first: slog (standard logging package), `slices`, `maps`, `cmp`, builtin `min`/`max`/`clear`, `errors.Join`.
- Loop variables are per-iteration: no `v := v` copies. Use `for i := range n`.
- Standard ServeMux handles methods and path wildcards (`GET /users/{id}`).
- Iterators: range-over-func with `iter.Seq` / `iter.Seq2`.
- Tests: `t.Context()`, `b.Loop()`, `t.Parallel()` without `tt := tt`.
- Concurrency: `sync.WaitGroup.Go`, `errgroup` with `SetLimit`.
- Newer language and library additions (1.26 and later) are not listed here; check the release notes and `go doc` before assuming an API exists.
- Generics only when logic is identical across types (collections, `Map`/`Filter`, typed caches). Not for hiding a single use.

## Project Layout (default: flat)

```
cmd/<app>/main.go      # wiring only: config, dependencies, start, shutdown
internal/<feature>/    # private code, grouped by feature or domain
api/                   # OpenAPI / proto
migrations/            # SQL migrations
```
Add `pkg` only for code intended for other modules. For complex domains with several teams or adapters, use the optional layered structure in `references/ddd-and-architecture.md`.

## Performance (profile first)

| Optimization | Method |
|---|---|
| Allocation | Preallocate: `make([]T, 0, n)`, `make(map[K]V, n)` |
| Strings | `strings.Builder` in loops; `strconv` over `fmt` for conversions |
| Pointers vs values | Values for small structs; pointers for large structs, mutation, or types with locks |
| Pooling | `sync.Pool` only on measured hot paths |
| Diagnosis | `pprof` and benchmarks before changing code |

## Task Progress (validation loop)

- [ ] Step 0 done (go version, lint config, conventions)
- [ ] NEVER list checked against the diff
- [ ] Errors wrapped with `%w`; every goroutine has an owner; `ctx` first, not stored
- [ ] Tests: table-driven, success and failure paths, `t.Parallel()` where safe
- [ ] **Run:** `gofmt -l .` -> `go vet ./...` -> `golangci-lint run` -> `go test -race ./...` -> `go mod tidy` -> fix -> repeat until clean

> Write code for the engineer who will debug it at 3 AM.
