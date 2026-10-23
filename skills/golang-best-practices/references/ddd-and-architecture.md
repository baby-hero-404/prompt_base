# Architecture, Optional DDD, and HTTP Services

Default is **flat and simple**. Move to layers only when the criteria in section 2 are met. Follow the project's existing structure first.

## 1. Default Layout (most services)

```
cmd/server/main.go        # parse config, build dependencies, run, shut down. No business logic
internal/
  user/                   # one package per feature/domain
    user.go               # types
    service.go            # business logic (concrete struct)
    store.go              # persistence (database/sql, GORM)
    handler.go            # HTTP handlers
    service_test.go
  platform/               # shared plumbing: config, logger, db, httpx
migrations/  api/  Makefile  go.mod
```
Rules:
- Package names are short, lowercase, singular nouns. No `utils`, `common`, `helpers`, `models`, `base`.
- `internal` keeps code private to the module. Create `pkg` only for code deliberately shared with other modules.
- Avoid import cycles by keeping dependencies one-way: handler -> service -> store. Define small consumer-side interfaces where the dependency crosses a boundary you want to fake in tests.
- Exported identifiers are API. Keep them few; prefer unexported helpers.
- Receivers: consistent per type (all pointer or all value), short names (`s *Service`).
- Constructors: `NewService(deps)` returns the concrete `*Service`. Use functional options only for many optional settings.

```go
// consumer-side interface in the handler package
type userGetter interface {
	Get(ctx context.Context, id string) (*user.User, error)
}

type Handler struct{ users userGetter }
func NewHandler(u userGetter) *Handler { return &Handler{users: u} }
```

## 2. When to Use DDD Layers

Use four layers when **most** of these hold: complex business rules (invariants, state machines), several delivery mechanisms (HTTP + gRPC + jobs), multiple persistence/external adapters, several teams, long-lived product. Skip for CRUD services, scripts, small APIs: the extra packages and mappers cost more than they give.

```
internal/
  domain/<aggregate>/        # entities, value objects, domain services, repository interfaces, domain errors
  application/<aggregate>/   # use cases: commands, queries, orchestration, transactions boundary
  infrastructure/            # persistence (sql/gorm), cache, external clients; implements domain interfaces
  interfaces/                # http, grpc, cli: parse input, call application, map output and errors
```

Dependency rule (enforce with a test or `depguard`/`go-arch-lint`):
- interfaces -> application -> domain
- infrastructure -> domain (implements its interfaces)
- **domain imports only the standard library** (no GORM tags in entities, no HTTP, no SQL driver).
- cmd wires everything together.

### Domain
```go
package user

type Status string
const (StatusActive Status = "active"; StatusBanned Status = "banned")

type User struct {
	ID     string
	Email  Email
	Status Status
}

var ErrBanned = errors.New("user is banned")

func (u *User) Activate() error {         // invariants live with the entity
	if u.Status == StatusBanned {
		return ErrBanned
	}
	u.Status = StatusActive
	return nil
}

type Email string
func NewEmail(s string) (Email, error) { /* validate once, then the type is always valid */ }

// repository interface lives in the domain (consumer of persistence)
type Repository interface {
	FindByID(ctx context.Context, id string) (*User, error)
	Save(ctx context.Context, u *User) error
}
```

### Application
One use case per type or function; it loads aggregates, calls domain methods, saves, and defines the transaction boundary (see `references/db-and-transactions.md` for a transaction-runner interface). It returns domain or DTO types, never database models.

### Infrastructure
Maps between persistence models (with `gorm` tags or sql scans) and domain entities. Translate storage errors to domain errors (`sql.ErrNoRows` -> `user.ErrNotFound`).

### Interfaces
Handlers decode and validate input, call one application use case, and map errors to status codes in one place.

## 3. Dependency Injection

- **Manual constructor injection in `main`** is the default: build dependencies bottom-up, pass them down.
- No global state, no `init()` side effects, no service locators.
- Use `wire`/`fx` only when the graph is large and the team already uses it.

```go
func main() {
	cfg := config.Load()
	db := mustOpenDB(cfg)
	users := user.NewService(user.NewStore(db))
	h := user.NewHandler(users)
	mux := http.NewServeMux()
	h.Register(mux)
	/* run with graceful shutdown: see references/concurrency-and-lifecycle.md */
}
```

## 4. HTTP Services with net/http

The standard `ServeMux` supports methods and path parameters.

```go
mux := http.NewServeMux()
mux.HandleFunc("GET /users/{id}", h.getUser)
mux.HandleFunc("POST /users", h.createUser)

func (h *Handler) getUser(w http.ResponseWriter, r *http.Request) {
	u, err := h.users.Get(r.Context(), r.PathValue("id"))
	if err != nil {
		writeError(w, r, err)
		return
	}
	writeJSON(w, http.StatusOK, toDTO(u))
}
```

Rules:
- Limit bodies and validate: `r.Body = http.MaxBytesReader(w, r.Body, 1<<20)`; `json.NewDecoder(r.Body)` with `DisallowUnknownFields()` where strictness helps; validate fields explicitly.
- One `writeError` maps errors to responses: `errors.Is(err, ErrNotFound)` -> 404, validation -> 400/422, unauthorized -> 401/403, default -> 500 with a generic body. Log details server-side with a request id; never leak internals.
- Middleware is `func(http.Handler) http.Handler`: request id, structured logging (`slog`), panic recovery, timeout, auth, CORS. Keep order explicit: recover -> request id -> log -> auth -> handler.
- Never use `http.DefaultClient` for outgoing calls without a timeout; create a configured `http.Client`.
- Set server timeouts and shut down gracefully (see concurrency reference).
- Gin (or chi, echo) is acceptable when the project already uses it: keep handlers thin, bind and validate input, call the same service layer, and keep framework types (`*gin.Context`) out of services and domain code.

## 5. Config and Logging

- Config from environment/flags parsed once in `main` into a typed struct; validate at startup and fail fast. Secrets never in code or logs.
- Use `log/slog` with key-value fields; include request id and user id when available; one log line per failure at the boundary.

## 6. Review Checklist

- [ ] Layout matches the project, or the flat default
- [ ] DDD only if criteria met; domain imports stdlib only
- [ ] Interfaces defined at consumers, small, justified
- [ ] `main` only wires; no globals or `init` side effects
- [ ] Central error mapping; timeouts and graceful shutdown set
- [ ] Framework types do not leak into services/domain
