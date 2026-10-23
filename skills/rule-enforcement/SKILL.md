---
name: rule-enforcement
description: "Use when project rules (AGENTS.md, CLAUDE.md, .claude/rules) keep getting violated in long conversations, or when turning written rules into mechanical checks wired into a verify target. Triggers on: rule enforcement, enforce rules, architecture test, architecture linter, rule drift, agent violates rules, make verify."
allowed-tools: Read, Write, Edit, Glob, Grep, Bash
---

# Rule Enforcement

Prose rules are advisory. In long conversations the agent drops them. A check that fails the build is not. This skill converts written project rules into checks that run in the project's `verify` target.

## When to Use
- A project has a rule file and the agent keeps breaking the same rules.
- Writing or restructuring a project's `AGENTS.md` / `CLAUDE.md` / `.claude/rules/`.
- Adding or wiring a `verify` target so the Stop hook (`tools/verify_gate.py`) can gate completion.

## Core Principles
1. **Every rule gets an ID and an enforcement tag** (`[hook] [lint] [test] [review]`). Format and example: `projects/_template/rules/README.md`. Untagged means `[review]`, which means expect drift.
2. **Automate what a machine can decide.** Line counts, banned regexes, import boundaries, naming: always `[test]` or `[lint]`. Only judgment calls stay `[review]`.
3. **One check per rule ID, named after it.** A failure message must print the rule ID, the file, and the line, so the agent can fix it without reading the rule file again.
4. **Wire into `verify`, not into prose.** The project's `make verify` runs format, analyze, tests and the rule checks. The Stop hook runs it; a failure blocks the agent from finishing.
5. **Keep the always-on rule file short** (about 60 lines, invariants only), repeat the 3-5 most critical rules at its end, move topic rules to `.claude/rules/<topic>.md` with `paths:` frontmatter.

## Procedure
1. Read the project's rule file(s). List rules as `ID | severity | checkable?`.
2. For each checkable rule, pick a check type from `references/check-recipes.md` (line limit, banned pattern, import boundary, required pairing).
3. Generate the check in the project's own stack and test location (Dart: `test/architecture/`, Python: `tests/architecture/`, Go: `*_test.go` or a `go vet` analyzer). Prefer the project's test runner over a new tool; add no dependency without asking.
4. Add the check to `verify` (see `makefile-standards`). Confirm `make verify` exists and exits non-zero on failure. The Stop hook only runs it for projects trusted with `python3 tools/pb_trust.py --add`.
5. Prove each check bites: introduce one violation, see the failure with rule ID, revert.
6. Update the rule file: add `[test]` / `[lint]` tags, keep IDs stable.
7. If the project has no `CLAUDE.md` but has `AGENTS.md`, propose a `CLAUDE.md` containing `@AGENTS.md` (ask first).

## Anti-Patterns
- Tagging a rule `[test]` with no test behind it.
- Checks that print "failed" without rule ID and location.
- Exempting generated code by editing the rule instead of the check's exclude list.
- Putting enforcement only in chat reminders or `/review`.
- A `verify` target that is slow enough (minutes) that people bypass it; keep rule checks under a few seconds.
