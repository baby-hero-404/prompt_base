# Proposal: Enhance `golang-best-practices`

Source: `docs/discovery/DISCOVERY-golang-skills.md` (cexll `golang-base-practices-skills`: 53 rules; mfmezger `go-engineering`: philosophy and footguns). Same method as the flutter and nextjs skills.

## 1. Context
`skills/golang-best-practices` is one flat 140-line file with no `references/`, no `allowed-tools`, no `Triggers on`, and not listed in any agent. It lacks a footgun catalog, DB/transaction guidance, graceful shutdown, test strategy detail, and a version check.

## 2. Decisions (user-confirmed or carried over)
- **DDD is optional**: default is a flat `cmd/` + `internal/` layout; DDD four-layer lives in a reference with criteria for when it pays off.
- **DB scope**: GORM transaction closures, plain `database/sql` patterns, Goose migrations, connection pool.
- **HTTP**: standard `net/http` (ServeMux) by default; Gin only as a short note; Kratos not covered.
- **Version baseline (user-confirmed): Go 1.27+ only.** No workarounds for older Go; Step 0 stops and asks if `go.mod` is older. APIs newer than the author's knowledge are not listed; the skill tells the agent to check release notes.
- **Carried from previous skills**: Step 0 reads `go.mod` and tooling; lean rewrite of `SKILL.md` with detail in references; all old topics stay reachable; update an agent (`backend-specialist` gets the skill and a Go checklist); trigger cases and registry.

## 3. Corrections to the sources
- Source demands 99% coverage; skill uses meaningful coverage targets by layer (domain high, glue lower) and treats the number as a CI choice, not a rule.
- Source says channel size should be 0 or 1; skill keeps that as the default and allows a justified bounded buffer.
- Source captures loop variables with `id := id`; unnecessary on the target baseline, so removed.
- Source installs tools with `@latest`; skill says pin versions.
- Existing text "define interfaces in the testing package to mock" is replaced by "define at the consumer".

## 4. Out of scope
Kratos, gRPC detail, Redis, `pkg/` library design, other Go skills.

## 5. Risks
| Risk | Mitigation |
|---|---|
| Trigger word "go" collides with plain English | Triggers use `golang`, `goroutine`, `go.mod`, `errgroup`, `gorm`, `go test` |
| Over-prescribing DDD | Explicit "use when" criteria; default flat |
| Body over 150 lines | Lean body, details in references |
