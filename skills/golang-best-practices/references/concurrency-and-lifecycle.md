# Concurrency and Lifecycle

Core: every goroutine has an **owner** (who starts, waits, and handles its error) and an **exit** (context cancel or closed channel).

## 1. Context Rules

- `ctx context.Context` is the **first parameter**, named `ctx`, of every function that does I/O, blocks, or calls something that does.
- Never store a context in a struct; never pass `nil` (use `context.TODO()` while refactoring).
- Derive, then cancel: `ctx, cancel := context.WithTimeout(ctx, d); defer cancel()`.
- Servers: use `r.Context()`; outgoing calls: `http.NewRequestWithContext`, `db.QueryContext`, `ExecContext`.
- Use context values only for request-scoped data crossing API boundaries (trace id, auth principal), with an unexported key type. Never for optional parameters.
- Map errors at the edge: `errors.Is(err, context.DeadlineExceeded)` -> 504, `context.Canceled` -> client went away, do not log as error.

```go
func (s *Service) Get(ctx context.Context, id string) (*Item, error) {
	ctx, cancel := context.WithTimeout(ctx, 2*time.Second)
	defer cancel()
	item, err := s.repo.Find(ctx, id)
	if err != nil {
		return nil, fmt.Errorf("get item %q: %w", id, err)
	}
	return item, nil
}
```

## 2. Goroutine Lifecycle

```go
// BAD: no way to stop, no error path
func Start() { go func() { for { work() } }() }

// GOOD: owned, cancellable, awaited
type Worker struct {
	tasks chan Task
	wg    sync.WaitGroup
}

func (w *Worker) Start(ctx context.Context) {
	w.wg.Add(1)
	go func() {
		defer w.wg.Done()
		for {
			select {
			case <-ctx.Done():
				return
			case t, ok := <-w.tasks:
				if !ok {
					return
				}
				w.process(ctx, t)
			}
		}
	}()
}

func (w *Worker) Stop() { close(w.tasks); w.wg.Wait() }   // producer side closes
```

Rules:
- The sender closes a channel; receivers never close. Never close twice or send after close.
- A goroutine blocked on a send or receive that nobody services leaks. Pair every send with a receiver or a `select` with `ctx.Done()`.
- Recover from panics at goroutine boundaries you own (workers), log, and decide: restart or fail. An unrecovered panic in any goroutine kills the process.
- Use `wg.Go(func() { ... })` to start and track a goroutine in one call instead of `Add(1)` plus `defer Done()`.
- Loop variables are per-iteration, so closures can capture them directly.

## 3. errgroup (fan-out with error and cancel)

```go
import "golang.org/x/sync/errgroup"

func Load(ctx context.Context, ids []string) ([]Item, error) {
	g, ctx := errgroup.WithContext(ctx)   // first error cancels ctx for the rest
	g.SetLimit(8)                         // bound concurrency

	items := make([]Item, len(ids))       // each goroutine writes its own index: no mutex needed
	for i, id := range ids {
		g.Go(func() error {
			it, err := fetch(ctx, id)
			if err != nil {
				return fmt.Errorf("fetch %s: %w", id, err)
			}
			items[i] = it
			return nil
		})
	}
	if err := g.Wait(); err != nil {
		return nil, err
	}
	return items, nil
}
```
- Writing to distinct slice indexes is safe; appending to a shared slice or writing a shared map needs a mutex.
- Always use the derived `ctx` inside goroutines, otherwise cancellation does not reach them.
- `errgroup` does not recover panics.

## 4. Channels

| Size | Meaning |
|---|---|
| `make(chan T)` | Synchronous handoff, backpressure |
| `make(chan T, 1)` | One pending signal; non-blocking send with `select { case c <- v: default: }` |
| `make(chan T, n)` | Only with a known bound (batch size, worker count) and a reason; a large buffer hides slow consumers and loses data on shutdown |

Patterns:
- **Pipeline:** each stage owns its output channel, closes it when input is drained, and exits on `ctx.Done()`.
- **Worker pool:** N goroutines read one jobs channel; close jobs to finish; collect results with a results channel or indexed slice.
- **Done signal:** `chan struct{}` closed once; use `sync.Once` if multiple callers may close.
- Prefer channels to pass ownership or events; prefer a mutex to protect a shared struct.

## 5. sync Primitives

| Need | Use |
|---|---|
| Protect shared state | `sync.Mutex` / `RWMutex` (RW only if reads dominate and are measured) |
| Counter / flag | `sync/atomic` types (`atomic.Int64`, `atomic.Bool`) |
| Run once | `sync.Once`, `sync.OnceValue(s)` |
| Await goroutines | `sync.WaitGroup` |
| Per-key dedupe of calls | `golang.org/x/sync/singleflight` |
| Reuse buffers on hot path | `sync.Pool` (measure first) |

Rules: lock then `defer Unlock()`; keep critical sections small; never call out to unknown code or block on I/O while holding a lock; keep lock order consistent; never copy a struct containing a mutex.

## 6. Graceful Shutdown (services)

```go
func run(ctx context.Context) error {
	ctx, stop := signal.NotifyContext(ctx, os.Interrupt, syscall.SIGTERM)
	defer stop()

	srv := &http.Server{
		Addr:              ":8080",
		Handler:           newRouter(),
		ReadHeaderTimeout: 5 * time.Second,
	}

	errc := make(chan error, 1)
	go func() {
		if err := srv.ListenAndServe(); !errors.Is(err, http.ErrServerClosed) {
			errc <- err
		}
		close(errc)
	}()

	select {
	case err := <-errc:
		return err
	case <-ctx.Done():
	}

	shutdownCtx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()
	if err := srv.Shutdown(shutdownCtx); err != nil {
		return fmt.Errorf("shutdown: %w", err)
	}
	return nil   // then close DB, flush logs, stop workers (wait on their WaitGroup)
}
```
Order: stop accepting -> drain requests -> stop background workers -> close DB and other resources. Set server timeouts (`ReadHeaderTimeout`, `ReadTimeout`, `WriteTimeout`, `IdleTimeout`); the default server has none.

## 7. Race Detection

```bash
go test -race ./...        # mandatory in CI
go run -race ./cmd/app     # during development
go build -race -o app ./cmd/app   # staging only (slower, more memory)
```
Common races: unsynchronized counters/maps, closing over a variable that another goroutine writes, returning internal slices/maps that callers mutate. A clean race run only covers executed paths; write tests that exercise concurrency.

## 8. Review Checklist

- [ ] Each `go` statement: owner, exit, error path, awaited on shutdown
- [ ] `ctx` first param, not stored, passed to all blocking calls
- [ ] errgroup uses the derived `ctx`; concurrency bounded
- [ ] Channel closed by sender only; buffer size justified
- [ ] No shared state without sync; `go test -race` passes
- [ ] HTTP server has timeouts and graceful shutdown
