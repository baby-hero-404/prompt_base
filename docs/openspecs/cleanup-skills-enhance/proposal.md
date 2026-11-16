# Proposal: Enhance the codebase cleanup skill family

## Problem
AI agents write code that works but leaves the codebase heavier: duplicate helpers, single-use wrappers, dead code, stale tests, over-mocked tests, leftover drafts. Cleanup guidance in this repo is thin and scattered:

| Where it lives today | What it covers | Gap |
|---|---|---|
| `skills/codebase-cleanup/SKILL.md` (53 lines, no `references/`, no `Triggers on`, no trigger case, in no agent) | Dead code, readability, structure, report | No removal protocol, no tools, no scope limit, never auto-triggers |
| `skills/coding-standards` (DRY, KISS, YAGNI, Boy Scout) | Principles | No "search before create"; Boy Scout rule conflicts with R8 (stay surgical) |
| `skills/openspec-authoring/references/extended-reference.md` §8, §9 | Staleness cleanup and doc sync inside a spec | Only applies when a spec exists |
| `skills/verification-before-completion/references/pre-commit-template.md`, `two-stage-review.md` | Review output format | No checklist for unintended changes, orphans, duplication |
| `skills/code-graph-analysis` | Dependency graph tools | Not connected to any audit step |
| `skills/testing-patterns` | How to write tests | Nothing on flaky, redundant, over-mocked, obsolete tests |

## Goal
Every agent owns the full lifecycle after each change: **Understand → Implement → Cleanup → Simplify → Verify**. Cleanup becomes six focused skills plus one workflow, grounded in what four reference repos actually do.

The seven user goals map to owners:

| User goal | Owner |
|---|---|
| 1. Prevent code bloat | `coding-standards` (write time), `code-review` (catch) |
| 2. Remove dead code | `dead-code-removal` |
| 3. Reduce complexity | `code-simplifier` |
| 4. Maintain architecture | `architecture-audit` |
| 5. Maintain test quality | `test-hygiene` |
| 6. Enforce code quality | `/cleanup` workflow → `lint-and-validate`, `verification-before-completion` |
| 7. Prevent technical debt | `code-cleanup` |

## Success
- After a normal feature task, the diff contains no unused code, no duplicate of an existing utility, no single-use abstraction without a reason, and no stale test; the agent states this in a short report.
- No deletion happens on a guess: each has an evidence record; uncertain items are reported, not removed.
- Cleanup never grows the diff beyond the task's own blast radius without the user asking.
- Each rule has one owning skill; a grep for the rule's key phrase finds one definition.

## Assumptions
- The four reference repos are public; nothing inside them is executed (R3).
- `references/` is gitignored (verified), so clones are never committed.
- `make registry`, `make skill-check`, `make test`, `make verify`, `make install` stay the delivery path.
- The user's pasted tables are the starting requirements; discovery may refine them.

## Decisions
- **Six focused skills** (user choice): `code-cleanup`, `code-simplifier`, `dead-code-removal`, `code-review`, `architecture-audit`, `test-hygiene`.
- **The skill is named `code-review` (user decision), although Claude Code ships a built-in `code-review` skill.** The repo skill is the cleanup-focused checklist for the final diff; it is deployed to Gemini and Codex too, where no built-in exists. Its description says it covers cleanup, not bug-hunting, and its trigger keywords avoid the bare phrase "code review" so it does not compete with the built-in on generic prompts.
- **No dependency on harness-only features.** Claude Code has built-in `simplify` and `code-review`, and this machine has a code-graph MCP server; Gemini and Codex do not. Skills must work with file search and shell alone, and may mention richer tools as optional.
- **`codebase-cleanup` stays** as the repo-wide, on-request sweep and routes to the others. `code-cleanup` is the per-task pass.
- **Scope rule resolves cleanup versus R8.** Per-task cleanup acts only on the *change set*: lines the task added or modified, plus what the task orphaned. Pre-existing problems seen along the way are reported under "Noticed, not changed". Only the repo-wide sweep, asked for by the user, goes further. The Boy Scout line in `coding-standards` is reworded to match.
- **One owner per topic:**

  | Topic | Owner | Others do |
  |---|---|---|
  | Search before create, reuse before duplicate, minimize dependencies | `coding-standards` | link |
  | AI slop in the change set: narrating comments, drafts, debug output, defensive boilerplate, leftover TODO | `code-cleanup` | link |
  | Single-use abstractions, wrappers, needless generics, nesting | `code-simplifier` | link |
  | Unused code, files, imports, dependencies, obsolete tests; removal protocol; tool table | `dead-code-removal` | `openspec-authoring` §8 keeps its `tasks.md` template and links here for the procedure |
  | What to look for in the final `git diff` | `code-review` | `verification-before-completion` keeps the output format (`pre-commit-template.md`) and links here |
  | Flaky, redundant, over-mocked, meaningless tests | `test-hygiene` | `testing-patterns` keeps how to write tests |
  | Boundaries, cycles, layering | `architecture-audit` | uses `code-graph-analysis` for graphs; `architecture` keeps design decisions |
  | Stale comments, docstrings, README | `code-cleanup` (in change set) | `openspec-authoring` §9 keeps spec-level doc sync |
  | Lifecycle order and report shape | workflow `/cleanup` | `/review`, `/enhance` link |
- **Tools are guidance only.** `dead-code-removal/references/tools.md` covers deadcode, staticcheck, golangci-lint, Knip, Ruff, Vulture, Semgrep, SonarQube with report-only commands. Agents use what the project already has; nothing is installed without asking (R2).
- **Enforcement is a workflow, not a rule** (user choice). `CLAUDE.md`, `AGENTS.md`, `GEMINI.md` are untouched.
- **Agent wiring, minimal:** `test-engineer` gets `test-hygiene`; `explorer-agent` gets `architecture-audit` and `codebase-cleanup`. Other agents reach the family through `coding-standards`, which every agent already loads and which points to `/cleanup`.
- **Discovery before authoring.** Each source is analysed alone with the `explore-codebase` method, then synthesised in `docs/discovery/DISCOVERY-cleanup-skills.md`. The user reviews the synthesis before any skill is written.
- **Adopt ideas, not text.** Reference content is paraphrased, licences are recorded in the discovery document, and sources are credited in the `README.md` acknowledgements table.
- **New skills are scaffolded with `scripts/create_skill.py --no-install`** so deployment happens once, at the end, after the user agrees.

## Trade-offs
- Seven cleanup-related skills raise trigger-collision risk. Mitigated by a keyword plan (see `design.md`) and near-miss trigger cases.
- `code-cleanup` and `codebase-cleanup` are easy to confuse by name. Accepted because the user's table uses `code-cleanup` and the old name must keep working; descriptions state the split in their first sentence.
- The scope rule means some pre-existing mess stays after a task. Accepted: silent drive-by refactors are worse for review than a reported backlog.
- Sharing the name `code-review` with the Claude Code built-in may confuse which one runs on Claude Code; accepted by the user, mitigated by narrow keywords and a first-sentence scope.

## Non-goals
- Installing any analysis tool here or wiring one into this repo's `make verify`.
- Rewriting `coding-standards`, `testing-patterns`, `architecture`, `openspec-authoring` beyond pointers and the short write-time section.
- Running the new skills on this repo's own code.
- Language-specific cleanup rules beyond the tool table (those belong to the language skills).

## Out of Scope
- A rule R12 in the three rule files.
- CI or pre-commit templates for other projects.
- A new `cleanup-specialist` agent (revisit after discovery if a source makes a strong case).

## Resolved questions
1. Name: `code-review` (user).
2. Golden eval for `dead-code-removal`: not wanted (user).
3. `make install`: the user runs it themselves; the agent never runs it.

## Impact

### Components
`skills/`, `global_workflows/`, `agents/`, `tests/skills/`, `scripts/clone_references.sh`, `registry.min.json`, `ARCHITECTURE.md`, `README.md`, `docs/`.

### Files
- **Create:**
  - `skills/{code-cleanup,code-simplifier,dead-code-removal,code-review,architecture-audit,test-hygiene}/SKILL.md`
  - `skills/dead-code-removal/references/tools.md`; other `references/` only where a body would pass 150 lines
  - `global_workflows/cleanup.md`
  - `docs/discovery/DISCOVERY-cleanup-skills.md`
- **Modify:**
  - `scripts/clone_references.sh` (four `clone_repo` lines)
  - `skills/codebase-cleanup/SKILL.md` (router, `Triggers on`)
  - `skills/coding-standards/SKILL.md` (write-time section, Boy Scout wording; currently 138 lines, limit 150)
  - `skills/testing-patterns/SKILL.md`, `skills/architecture/SKILL.md`, `skills/lint-and-validate/SKILL.md`, `skills/verification-before-completion/SKILL.md`, `skills/openspec-authoring/references/extended-reference.md` (one pointer each)
  - `global_workflows/review.md`, `global_workflows/enhance.md` (link to `/cleanup`)
  - `agents/test-engineer.md`, `agents/explorer-agent.md` (`skills:` line)
  - `tests/skills/trigger_cases.json`
  - `ARCHITECTURE.md`: skill tables, workflow table, counts (workflows 17 → 18 in three places; skills count is already stale at 56 against 59 registered), and remove three entries with no skill directory: `code-review-checklist`, `review-pre-commit-git`, `frontend-design`
  - `README.md` acknowledgements table
  - `registry.min.json` (generated), `docs/ai/manifest.json` (checksums via `tools/memory_stale.py --update`; file is gitignored)
- **Delete:** none.

### Public API
None. New slash command `/cleanup`.

### Migration
`make install` (run by the user) redeploys to `~/.claude`, `~/.gemini`, `~/.codex`.

### Backward Compatibility
`codebase-cleanup` keeps its name, safety rules and report sections. No existing trigger keyword is removed.
