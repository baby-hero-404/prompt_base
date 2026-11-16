# Dead Code and Quality Tools by Ecosystem

Loaded on demand from `SKILL.md`.

## Rules for using any tool

1. **Use what the project already has.** Look for the tool in the manifest, lock file, task runner, or continuous integration configuration. If it is absent, ask before installing (new dependency).
2. **Report mode first.** Run the command that only lists findings. Apply an automatic fix only inside the change set, and review the resulting diff.
3. **Tool output is a lead, not a verdict.** Every finding still goes through the verification checklist in `SKILL.md`.
4. **Check the installed version.** Flags change between releases. The commands below are common forms and were not executed while writing this file; confirm with the tool's help output or official documentation.

## Go

| Tool | Finds | Report-only command | Detect in project |
|---|---|---|---|
| `deadcode` | Functions unreachable from the program's entry points | `deadcode ./...` (add `-test` to count test entry points) | Mentioned in the task runner or continuous integration |
| `staticcheck` | Unused identifiers (check U1000), ineffective code, deprecated use | `staticcheck ./...` | A `staticcheck.conf` file, or enabled inside the linter runner |
| `golangci-lint` | Runs many linters, including unused code, unused parameters, ineffective assignments | `golangci-lint run` | A `.golangci.yml` or `.golangci.yaml` file |
| Go toolchain | Unused module requirements | `go mod tidy -diff` on recent toolchains (prints the change without writing) | Always available |

False positives: `deadcode` only sees what is reachable from the entry points it analyses, so library packages, code behind build tags, and code reached through reflection or code generation need manual checks.

## JavaScript and TypeScript

| Tool | Finds | Report-only command | Detect in project |
|---|---|---|---|
| Knip | Unused files, exports, types, and dependencies | `npx --no-install knip` | `knip` in development dependencies, or a Knip configuration file |
| TypeScript compiler | Unused locals and parameters | `npx --no-install tsc --noEmit --noUnusedLocals --noUnusedParameters` | A `tsconfig.json` file |
| ESLint | Unused variables and imports, per the project's rules | The project's own lint script | An ESLint configuration file |

The `--no-install` flag keeps `npx` from downloading a package that the project does not already have.

False positives: files loaded by a framework's file-system routing, configuration files discovered by name, exports consumed by another workspace package, and anything referenced only from the package manifest's script or binary fields. Knip needs correct entry-point configuration; a long list of unused files usually means the configuration is incomplete.

## Python

| Tool | Finds | Report-only command | Detect in project |
|---|---|---|---|
| Ruff | Unused imports (F401), unused local variables (F841), redefinitions (F811), commented-out code (ERA001) | `ruff check --select F401,F841,F811 .` | A Ruff section in `pyproject.toml`, or a `ruff.toml` file |
| Vulture | Unused functions, classes, variables, and unreachable code, with a confidence score | `vulture . --min-confidence 80` | Listed in development requirements; sometimes a whitelist file |

False positives: names used through `getattr`, framework decorators and registries, command-line entry points declared in the package metadata, test fixtures discovered by name, and names re-exported from a package's top-level module on purpose. Vulture's lower confidence levels are noisy; treat everything under 100 percent as "potentially unused" until checked.

## Any language

| Tool | Finds | Notes |
|---|---|---|
| Semgrep | Custom rules for architectural boundaries, banned patterns, and known anti-patterns | Use the project's own rule files. Rule sets fetched from the public registry need network access; mention that before running. |
| SonarQube | Code smells, duplication, coverage, maintainability trends | Needs a server. Read the existing project dashboard or the analysis results in continuous integration; do not set up a server for a cleanup task. |
| Compiler and type checker | Unused variables, imports, and unreachable code | Already part of the build; turn warnings on rather than adding a tool. |

## No tool available

1. Search the repository for each candidate name, including non-code files.
2. Use the dependency graph approach from the `code-graph-analysis` skill to find modules with no incoming edges.
3. Mark every result "lower confidence" in the evidence record.
