# Implementation Map: Cleanup skill family

**Goal:** Six focused cleanup skills, a routed `codebase-cleanup`, and a `/cleanup` lifecycle workflow, based on analysis of four reference repos.
**Tech Stack:** Markdown skills and workflows, `scripts/create_skill.py`, Makefile gates (`registry`, `skill-check`, `test`, `verify`, `install`), bash.

---

## Phase 0: Discovery (ends with a user checkpoint)

### Add and clone sources
**Why:** The user asked for these four repos, cloned through the existing script.
**Files:** `scripts/clone_references.sh`
**Changes:**
- [x] Add `clone_repo` lines for `davidfstr/revise-skill`, `rohitg00/pro-workflow`, `github/awesome-copilot`, `VoltAgent/awesome-agent-skills`
- [x] Four repos cloned `--depth 1` with plain `git clone` (the script was not run, so the five existing clones were not pulled); the user was told before the network access
**Verify:**
- [x] `bash -n scripts/clone_references.sh` passes
- [x] Four new directories exist under `references/`; `git status` shows only the script changed

### Analyse each source alone
**Why:** Adopt on evidence, and keep one source's framing from colouring the next.
**Depends on:** Add and clone sources
**Files:** `docs/discovery/DISCOVERY-cleanup-skills.md`
**Changes:**
- [x] `revise-skill`, using the template in `design.md`
- [x] `pro-workflow` (the `deslop` material and the workflow around it)
- [x] `awesome-copilot` (no `cleanup-specialist` exists in the clone; read the closest agents and skills instead; plus filtered entries, cap about ten)
- [x] `awesome-agent-skills` (filtered entries, cap about ten; if an entry only links to an outside repo, record the link and do not clone it without asking)
- [x] Record licence and commit per source, and any R1 red flags
**Verify:**
- [x] Every claim in the document cites a file path in the clone (line numbers only where read; index entries marked approximate)
- [x] Each source section has adopt, adapt, and reject lines

### Synthesise
**Depends on:** Analyse each source alone
**Files:** `docs/discovery/DISCOVERY-cleanup-skills.md`, this spec set
**Changes:**
- [x] Idea → target skill → conflict with existing rules → decision
- [x] List user-table items that no source supports, with keep or drop
- [x] Update `proposal.md` and `design.md` where discovery changes a decision (keyword plan, skill list, the `cleanup-specialist` agent question)
**Verify:**
- [x] Each of the six skills has adopted ideas or a stated reason it has none
- [x] **Checkpoint:** user approves the synthesis

## Phase 1: Skills

### Scaffold
**Why:** The scaffolder owns folder, frontmatter, and duplicate checks; `--no-install` defers deployment.
**Depends on:** Phase 0 checkpoint
**Files:** `skills/<six names>/SKILL.md`, `tests/skills/trigger_cases.json`
**Changes:**
- [x] Read `scripts/create_skill.py`, then run it six times with `--no-install`, a real description, and `--trigger-case`
**Verify:**
- [x] Six directories exist; nothing under the home directory changed

### Write the six skills
**Depends on:** Scaffold
**Files:** `skills/{code-cleanup,code-simplifier,dead-code-removal,code-review,architecture-audit,test-hygiene}/SKILL.md`, `skills/dead-code-removal/references/tools.md`
**Changes:**
- [x] `code-cleanup`: slop checklist for the change set, stale comments and docs
- [x] `code-simplifier`: when an abstraction earns its place; inline rules; behavior-preservation check
- [x] `dead-code-removal`: dynamic-use checklist, two verdicts, evidence record, tool table
- [x] `code-review`: unintended changes, duplication of existing utilities, orphans, secrets, untracked files; output in the existing pre-commit format
- [x] `architecture-audit`: boundaries, cycles, layering; run conditions; uses `code-graph-analysis`
- [x] `test-hygiene`: meaningless, over-mocked, redundant, flaky, obsolete
- [x] All six use the shared skeleton and state the change-set scope
**Verify:**
- [x] Lint shows no error and no "Body > 150 lines" warning for the six
- [x] No sentence copied verbatim from a reference repo (spot check five distinctive phrases per skill with a search in `references/`)

### Adjust existing skills
**Why:** Remove duplicates, add pointers, resolve the Boy Scout versus R8 conflict.
**Depends on:** Write the six skills
**Files:** `skills/codebase-cleanup/SKILL.md`, `skills/coding-standards/SKILL.md`, `skills/testing-patterns/SKILL.md`, `skills/architecture/SKILL.md`, `skills/lint-and-validate/SKILL.md`, `skills/verification-before-completion/SKILL.md`, `skills/openspec-authoring/references/extended-reference.md`
**Changes:**
- [x] `codebase-cleanup`: router; keep safety rules and report sections; add `Triggers on`; propose-then-apply in groups
- [x] `coding-standards`: "Before you write" (at most eight lines); reword Boy Scout to the change-set scope
- [x] One pointer line in each of the other five files

**Cleanup:**
- [x] Remove from `codebase-cleanup` the rule text now owned elsewhere
**Verify:**
- [x] For each row of the one-owner table, a search for its key phrase finds one definition; other hits are links
- [x] `coding-standards` body is at or under 150 lines

## Phase 2: Workflow and wiring

### `/cleanup` workflow
**Depends on:** Phase 1
**Files:** `global_workflows/cleanup.md`, `global_workflows/review.md`, `global_workflows/enhance.md`
**Changes:**
- [x] Write the workflow: seven ordered steps, audit condition, report block, sweep mode via argument
- [x] Link from `/review` and `/enhance`
**Verify:**
- [x] Step list matches the "Task finished" scenario in `specs.md` exactly
- [x] Contract check passes (every skill name the workflow mentions exists)

### Agents and trigger cases
**Depends on:** Phase 1
**Files:** `agents/test-engineer.md`, `agents/explorer-agent.md`, `tests/skills/trigger_cases.json`
**Changes:**
- [x] Add `test-hygiene` to `test-engineer`; `architecture-audit` and `codebase-cleanup` to `explorer-agent`
- [x] At least three cases per family skill: two hits, one near miss; include `code-cleanup` versus `codebase-cleanup` versus `code-simplifier`
**Verify:**
- [x] Collision report lists no keyword from the family
- [x] Precision and recall at or above 0.9 for all seven

## Phase 3: Documentation, gates, deploy

### Documentation sync
**Depends on:** Phase 2
**Files:** `ARCHITECTURE.md`, `README.md`, `docs/skills-guide.md` or `docs/components.md` only if they enumerate skills
**Changes:**
- [x] `ARCHITECTURE.md`: add six skills and `/cleanup`; set counts from `registry.min.json` and a listing of `global_workflows/`; remove `code-review-checklist`, `review-pre-commit-git`, `frontend-design` after confirming no directory exists; fix the `/review` description that names a missing skill
- [x] `README.md`: four rows in the acknowledgements table, linking the discovery document
**Verify:**
- [x] Every skill name in `ARCHITECTURE.md` skill tables exists under `skills/`

### Gates
**Depends on:** Documentation sync
**Changes:**
- [x] `make registry`
- [x] `python3 tools/memory_stale.py --root . --update`
- [x] `make verify` (audit, tests, skill gates, memory freshness)
**Verify:**
- [x] `make verify` exits 0, output quoted in the completion report
- [x] `git status`: no change to `CLAUDE.md`, `AGENTS.md`, `GEMINI.md`, `settings.json`, `requirements.txt`

### Deploy
**Depends on:** Gates
**Changes:**
- [x] Hand over to the user: they run `make install` themselves (it rebuilds skill directories under the home directory); the agent does not run it
**Verify:**
- [ ] `~/.claude/skills/dead-code-removal/SKILL.md` and `~/.claude/commands/cleanup.md` exist; same skills under `~/.gemini` and `~/.codex`

## Rollback Plan
- [ ] Revert the commit, run `make registry`; the user runs `make install` to redeploy the previous set.
- [ ] `references/` clones are untracked; delete the four directories by hand if unwanted (ask first).
