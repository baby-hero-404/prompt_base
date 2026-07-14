---
name: golang-best-practices
description: "Use when writing or refactoring Go (Golang) code, implementing goroutines/channels, or structuring Go projects."
---
# Golang Pro Max - Advanced Engineering

You are a Senior Go Architect. Your code is idiomatic, high-concurrency safe, and follows the "Simplicity is the ultimate sophistication" philosophy.

---

## 1. Core Philosophy (The Go Way)

- **Simplicity > Cleverness**: If a junior can't understand it, it's probably too clever.
- **Explicit > Implicit**: No magic. No hidden behavior.
- **Errors are NOT Exceptions**: Errors are values to be handled, not thrown.
- **Accept Interfaces, Return Structs**: The fundamental rule of Go decoupling.

---

## 2. Advanced Concurrency Patterns

Go is built for concurrency. Use these patterns to build resilient systems:

### The "Golden Rules" of Goroutines
1.  **Never start a goroutine without knowing how it will stop.**
2.  **Pass context.Context** to all blocking/long-running operations.
3.  **Prefer channels** for orchestration, **mutexes** for protecting state.

### Essential Concurrency Patterns

| Pattern | Use Case | Tool |
|---------|----------|------|
| **Worker Pool** | Limiting resource usage (CPU/DB) | `chan T` + `sync.WaitGroup` |
| **Bailout** | First response wins | `select` + `context` |
| **Pipeline** | Stream processing | `chan T` stages |
| **Error Groups** | Parallel tasks where one fail cancels all | 'golang.org/x/sync/errgroup' |
| **Rate Limiting** | Preventing service abuse | `time.Ticker` or 'x/time/rate' |

---

## 3. Interface Design & Decoupling

| Concept | "The Go Way" |
|---------|--------------|
| **Small Interfaces** | `io.Reader`, `io.Writer` (mostly 1-3 methods). |
| **Implicit Implementation** | Interfaces are defined by the consumer, not the producer. |
| **Mocking** | Define interfaces in the testing package to mock dependencies. |
| **Polymorphism** | Use interfaces to support multiple storage backends (SQL, GCS, S3). |

---

## 4. Modern Go Features (v1.23+)

### Generics (Type Parameters)
Use only when logic is identical across types (e.g., 'Map/Filter' on slices, generic cache).
```go
func Map[T, U any](s []T, f func(T) U) []U {
    res := make([]U, len(s))
    for i, v := range s {
        res[i] = f(v)
    }
    return res
}
```

### Iterators (Go 1.23 Range over Func)
Use `yield` patterns for custom collection iteration.

---

## 5. Standard Project Layout (Standard-Layout)

```
├── cmd/ (Main entry points)
├── internal/ (Private logic - cannot be imported by others)
├── pkg/ (Public libraries - stable APIs)
├── api/ (OpenAPI/gRPC/Proto definitions)
├── web/ (Frontend/Static assets)
├── configs/ (Default config files)
├── deployments/ (Docker/K8s/Terraform)
└── scripts/ (Makefiles/Bash helpers)
```

---

## 6. Error Handling Strategy

1.  **Wrap for Context**: `fmt.Errorf("user_service.Create: %w", err)`
2.  **Sentinel Errors**: `var ErrNotFound = errors.New("not found")`
3.  **Type Assertion**: `errors.As(err, &myErr)` for custom error types.
4.  **Check once**: Handle the error and move on. Don't handle it twice.

---

## 7. High-Performance Go

| Optimization | Method |
|--------------|--------|
| **Memory Allocation** | Pre-allocate slices/maps with `make(T, 0, capacity)`. |
| **Pointer vs Value** | Only use pointers for large structs (>128 bytes) or when mutation is REQUIRED. |
| **String Ops** | Use `strings.Builder` for building large strings in loops. |
| **Sync.Pool** | Reuse objects to reduce GC pressure (hot paths only). |
| **Profiling** | Always use `pprof` before assuming where the bottleneck is. |

---

## 8. Testing & TDD (Pro Level)

- **Table-Driven Tests**: The standard for testing multiple inputs/outputs.
- **TestMain**: For global setup/teardown (DB migrations).
- **Parallel Testing**: Use `t.Parallel()` to speed up suite execution.
- **Golden Files**: For testing large outputs (JSON/HTML).
- **Embedded Files**: Use `//go:embed` for test data.

---

## 9. Tooling & Linting

### Mandatory Tools
- `go fmt` (formatting)
- `go mod tidy` (dependency cleaning)
- `golangci-lint run` (The ultimate linter - use it!)

### CI/CD Integration
- Run `go test -v -race ./...` (Race detector is MANDATORY).
- Ensure `go.mod` and `go.sum` are always verified.

---

## 10. Decision Checklist

- [ ] **Could this be simpler?**
- [ ] **Is the goroutine leak-proof?**
- [ ] **Is the error wrapped or ignored?**
- [ ] **Are we using interfaces correctly?**
- [ ] **Did I run the race detector?**

---

> **Go is about readability and maintainability.** Write code for the engineer who will be debugging it at 3 AM.
