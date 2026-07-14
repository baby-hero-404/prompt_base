# Tasks: Skill Quality Gates — 5-Tier Verification Pipeline

> Order follows the cost gradient: ship the free deterministic gates first (Tiers 1, 2, 0), then orchestration, then the LLM eval, then the journal.

## P0 — Critical

### Task 1.1: Tier 1 — `scripts/skill_lint.py`
> Links to: REQ-001

**Acceptance Criteria:**
- [x] Validates frontmatter: `name` == folder, `description` non-TODO ≥ 20 chars with "Triggers on" keywords, `allowed-tools` from the known tool set
- [x] Validates body: required sections present, warn > 150 lines, fail > 300 lines
- [x] Validates registry sync: entry exists in `registry.min.json` and matches frontmatter
- [x] `make registry` invokes lint first and aborts on failure
- [x] Run against all ~50 existing skills; fix or waive every failure found (1 warning: `ux-ui-pro-max` at 151 lines, waived)
- [ ] `KNOWN_TOOLS` allowlist only covers the 7 tools currently in use (Read/Write/Edit/Glob/Grep/Bash/Agent) — will false-fail the moment a skill legitimately declares WebFetch/WebSearch/TaskCreate etc.; extend before relying on this in CI

### Task 1.2: Tier 0 — `scripts/skill_contract.py`
> Links to: REQ-003

**Acceptance Criteria:**
- [x] Verifies backtick repo paths exist; skips fenced example blocks and `contract:ignore` regions
- [x] Verifies referenced skills exist in registry and agents in `antigravity/agents/`
- [x] Verifies named CLIs resolve via `command -v` (optional-marked CLIs warn only) — only matches an explicit `CLI: toolname` annotation, which no current skill body uses; effectively dormant
- [x] Verifies body-instructed tools ⊆ `allowed-tools` — only matches `use the X tool` phrasing (case-sensitive); same dormancy risk
- [ ] Regression proof: running it on the old `project-discovery` → `explore-codebase` rename scenario catches the dangling reference — **not yet verified**; passes today because nothing in current skills trips the two detectors above, not because a real violation was caught and reported

## P1 — High

### Task 2.1: Tier 2 — trigger cases + `scripts/trigger_test.py`
> Links to: REQ-002

**Acceptance Criteria:**
- [x] `tests/skills/trigger_cases.json` seeded with ≥ 30 labeled prompts covering ≥ 15 skills, including 5 negative cases (`expect: []`)
- [x] Precision/recall computed per skill; exit non-zero below threshold (default 0.9) — live run: 17/17 tested skills at 1.00/1.00
- [x] Keyword-collision report lists any trigger keyword shared by ≥ 2 skills
- [x] Warns for every registered skill that has zero cases

### Task 2.2: Orchestration — `make skill-check`
> Links to: REQ-007, REQ-005

**Acceptance Criteria:**
- [x] `make skill-check SKILL=<name>` runs Tier 1 → 2 → 0, fail-fast
- [x] No-arg form checks all registered skills in < 10 s, zero LLM calls
- [x] Prints the `skill-eval` reminder when a changed skill has `eval: required`

## P2 — Medium

### Task 3.1: Tier 3 — `evals/golden/` + `scripts/golden_eval.py`
> Links to: REQ-004

**Acceptance Criteria:**
- [x] Golden task YAML schema implemented (provider swapped to Gemini per implementation choice — see `design.md`)
- [x] Old version pulled from `git show HEAD:<path>`, new from working tree; identical prompts otherwise
- [x] Judge at temperature 0; status `BETTER | SAME | WORSE`; exit non-zero only on `WORSE`
- [x] Report `docs/reports/EVAL-<skill>-<date>.md` written with per-task status and reasoning
- [x] `explore-codebase` enrolled as the pilot (`eval: required`, 3 golden task files exist)
- [ ] **Live run produces real signal** — the 2026-07-14 pilot run returned empty output on both sides for all 3 tasks (`docs/reports/EVAL-explore-codebase-20260714115913.md`); not yet achieved

### Task 3.1b: Fix Golden Eval grounding (follow-up, blocks trusting REQ-004)
> Links to: REQ-004

**Acceptance Criteria:**
- [x] `run_agent` gives the model under test real tool access (`read_file`/`list_files`/`grep` as Gemini function declarations), sandboxed to the temp workspace with path-traversal rejection, looped up to `MAX_TOOL_TURNS`
- [x] `evals/golden/fixtures/mini-app/` added — a small Node.js fixture (TTL cache "hidden gem" in `cache.js`, a deliberate config-singleton anti-pattern) for the 3 `explore-codebase` tasks to actually explore
- [x] Old/new `SKILL.md` content is never written to disk — both versions are held in memory and passed as `system_instruction` per API call; the working-tree file is no longer touched at all (stronger fix than the planned temp-copy approach — there was no need to write the file to disk in the first place)
- [x] `judge_model` from the task YAML is now passed through to the judge call (`golden_eval.py` `judge_results(..., judge_model, ...)`); all 3 task YAMLs updated from a nonexistent Claude model name to `gemini-2.5-flash`
- [x] Verified the tool loop with a mocked API response: confirms `execute_tool` returns real fixture file content and the loop correctly resolves a `functionCall` → tool result → final-answer turn
- [ ] **Live confirmation blocked**: `gemini-1.5-pro` (the original default) is fully deprecated (404) and switching to `gemini-2.5-flash` hit the account's free-tier quota (20 req/day) while iterating on the fix. A real end-to-end run with non-empty judged output is still outstanding — retry once the daily quota resets, or supply a paid-tier key

### Task 3.2: Scaffolder integration
> Links to: REQ-M01

**Acceptance Criteria:**
- [x] `create_skill.py` accepts `--trigger-case "<prompt>"` and appends it to `trigger_cases.json`
- [x] Interactive prompt for a seed case when the flag is omitted
- [x] Optional `eval:` frontmatter key supported in the template (`--eval` flag)

## P3 — Low

### Task 4.1: Tier 4 — feedback journal + docs
> Links to: REQ-006

**Acceptance Criteria:**
- [x] `docs/reports/skill-feedback.md` created with the table format and rollback procedure in the header
- [x] `ARCHITECTURE.md` gains a "Skill Quality Gates" section with the pipeline diagram
- [x] `docs/skills-guide.md` documents the developer workflow: edit → `skill-check` → (`skill-eval`) → merge → journal
