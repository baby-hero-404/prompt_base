# Specification: golang-best-practices v2

## 1. Deliverables
```
skills/golang-best-practices/
├── SKILL.md                                  # lean body <= 150 lines
└── references/
    ├── concurrency-and-lifecycle.md          # goroutines, context, errgroup, channels, shutdown
    ├── ddd-and-architecture.md               # layout, optional DDD, DI, net/http services
    ├── db-and-transactions.md                # database/sql, GORM, Goose, pool
    └── testing-and-quality.md                # table tests, mocks, race, coverage, lint, bench
agents/backend-specialist.md                  # + skill, + Go checklist
registry.min.json, tests/skills/trigger_cases.json
```

## 2. Requirements
| ID | Requirement |
|---|---|
| G1 | Step 0: read `go.mod` (baseline Go 1.27+, stop and ask if older), lint config, existing framework/ORM; follow them |
| G2 | NEVER/footgun block: orphan goroutines, context in struct, ignored errors, string error compare, panic for control flow, premature interfaces |
| G3 | Concrete types first; interfaces at the consumer, small, only with a real need |
| G4 | Errors: wrap with `%w`, `errors.Is/As`, handle once |
| G5 | Every goroutine has an owner and an exit; `ctx` is the first parameter, never stored |
| G6 | Transactions: closure style or `defer` rollback; pass `ctx`; set pool limits |
| G7 | Mandatory validation loop: `gofmt`, `go vet`, `golangci-lint run`, `go test -race ./...` |
| G8 | All old topics remain reachable (concurrency table, interface table, generics, iterators, layout, performance, testing, tooling) |

## 3. Acceptance
`make registry`, `make skill-check`, `make test` pass; trigger precision/recall for the skill >= 0.9; `make install` done.
