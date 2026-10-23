# Testing and Quality

Rule R11: add tests for success **and** failure paths with the implementation. Read the project's existing test style (testify? stdlib only? gomock?) and match it.

## 1. Table-Driven Tests with Subtests

```go
func TestParseAmount(t *testing.T) {
	t.Parallel()
	tests := []struct {
		name    string
		in      string
		want    int64
		wantErr error
	}{
		{name: "whole", in: "12", want: 1200},
		{name: "cents", in: "12.34", want: 1234},
		{name: "empty", in: "", wantErr: ErrEmpty},
		{name: "negative", in: "-1", wantErr: ErrNegative},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			t.Parallel()
			got, err := ParseAmount(tt.in)
			if !errors.Is(err, tt.wantErr) {
				t.Fatalf("err = %v, want %v", err, tt.wantErr)
			}
			if got != tt.want {
				t.Errorf("got %d, want %d", got, tt.want)
			}
		})
	}
}
```
- Name cases by behavior. Include error cases, boundaries, empty and nil inputs.
- Compare errors with `errors.Is`/`errors.As`, not strings.
- Use `t.Helper()` in helpers, `t.Cleanup` for teardown, `t.TempDir()` for files, `t.Setenv` for environment, `t.Context()` for a test-scoped context.
- `go-cmp` (`cmp.Diff`) gives readable struct diffs; testify (`require` for must-pass preconditions, `assert` for the rest) is fine when the project uses it. Do not mix styles in one package.

## 2. Test Doubles

- Prefer **hand-written fakes** (in-memory implementations) for small consumer-side interfaces. They are simple and refactor-proof.
- Use generated mocks (`go.uber.org/mock` with `mockgen`) when you must assert call sequences or arguments. Pin the tool version and regenerate with `go generate ./...`; commit or generate in CI consistently.
- Define the interface where it is consumed (the code under test), covering only the methods it calls.
- Never mock the standard library or types you do not own; wrap them in a small adapter instead.
- Use `net/http/httptest` for handlers and clients: `httptest.NewRecorder`, `httptest.NewServer`.
- Inject time and randomness (`func() time.Time`, a clock interface) instead of sleeping.

```go
type fakeRepo struct {
	byID map[string]*User
	err  error
}
func (f *fakeRepo) FindByID(_ context.Context, id string) (*User, error) {
	if f.err != nil { return nil, f.err }
	u, ok := f.byID[id]
	if !ok { return nil, ErrNotFound }
	return u, nil
}
```

## 3. Integration Tests

- Use real dependencies (Postgres, Redis) through containers (`testcontainers-go`) or a CI service. Do not fake the database for repository tests; SQL bugs hide behind mocks.
- Separate them: build tag (`//go:build integration`) or `testing.Short()` skip, run with `go test -tags=integration ./...`.
- `TestMain` for one-time setup (container, migrations); isolate each test with its own schema, transaction rollback, or unique data.
- Keep the suite deterministic: no sleeps, bounded timeouts via context.

## 4. Other Test Types

- **Golden files** for large outputs (JSON/HTML): store under `testdata`, update with a `-update` flag, review diffs.
- **Fuzzing** for parsers and decoders: `func FuzzParse(f *testing.F)`, run `go test -fuzz=FuzzParse -fuzztime=30s`.
- **Examples** (`func ExampleX()`) double as docs and tests.
- **Embedded fixtures**: `//go:embed testdata/*.json`.
- Test HTTP handlers through the router (`mux.ServeHTTP(rec, req)`) so routing and middleware are covered.

## 5. Race Detector

```bash
go test -race ./...
go test -race -count=3 ./pkg/concurrent/...   # repeat to expose flaky races
```
Mandatory in CI. If it reports a race, fix the synchronization; do not remove the test.

## 6. Coverage

```bash
go test -coverprofile=coverage.out ./...
go tool cover -func=coverage.out | tail -1
go tool cover -html=coverage.out -o coverage.html
```
Use coverage to find untested branches, not as the goal. Reasonable targets by layer (adjust to the project's CI gate): domain/business logic about 90-100%, application/use cases about 85-95%, handlers about 80-90%, infrastructure covered mainly by integration tests. Do not write assertion-free tests or test generated code to hit a number. If CI enforces a threshold, keep it and exclude generated files explicitly.

## 7. Benchmarks and Profiling

```go
func BenchmarkEncode(b *testing.B) {
	data := makeData()
	b.ReportAllocs()
	for b.Loop() {
		_ = Encode(data)
	}
}
```
```bash
go test -bench=. -benchmem -run=^$ ./...
go test -bench=Encode -cpuprofile=cpu.out -memprofile=mem.out
go tool pprof -http=:0 cpu.out
```
Compare before/after with `benchstat`. Optimize only measured hot spots (see performance table in `SKILL.md`).

## 8. Lint and Static Analysis

Required in CI: `gofmt` (or `goimports`), `go vet ./...`, `golangci-lint run`.

Suggested linters (enable per project, start small): `errcheck` (unchecked errors), `staticcheck`, `govet`, `revive`, `gosec`, `errorlint` (`%w`, `errors.Is`), `bodyclose`, `noctx` (missing context), `ineffassign`, `unused`, `gocritic`. Pin the golangci-lint version in CI and document it. Fix findings; do not blanket-disable linters. A `//nolint:name // reason` comment must be specific and justified.

Also: `go mod tidy` leaves no diff, `go mod verify`, and `govulncheck ./...` for known vulnerabilities in dependencies.

## 9. Idiom Checks

- Names: short and clear; no stutter (`user.User` fine, `user.UserService` stutters); acronyms in caps (`ID`, `URL`, `HTTP`); no `Get` prefix on simple getters.
- Make the zero value useful; initialize structs with field names; use `defer` for cleanup right after acquiring; keep embedding for real composition, not inheritance.
- Doc comments start with the identifier name: `// Parse reads ...`.
- Do not use the blank identifier to hide errors.

## 10. Review Checklist

- [ ] Tests for success and failure paths; table-driven with `t.Run`
- [ ] Fakes preferred; mocks only where interaction matters
- [ ] Integration tests use real DB and are separated
- [ ] `go test -race ./...` passes; no sleeps in tests
- [ ] `gofmt`, `go vet`, `golangci-lint`, `go mod tidy` clean
- [ ] Benchmarks/pprof before any performance change
