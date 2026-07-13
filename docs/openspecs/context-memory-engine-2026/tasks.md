# Tasks: Automated Context Memory Engine

## P0 — Critical (engine core)

### Task 1.1: Build `tools/memory_engine.py` (shared library)
> Links to: REQ-001, REQ-006, REQ-008, REQ-010, REQ-011

**Acceptance Criteria:**
- [x] `resolve_project_root(cwd)`: `PB_MEMORY_ROOT` override → upward walk for `.git` (dir or file), else `CLAUDE.md`/`GEMINI.md`/`ARCHITECTURE.md` → logged fallback to `cwd`; unit tests cover nested-dir launch, no-marker fallback, and env override (REQ-010)
- [x] Creates `.ai-memory/memory.db` **under the resolved root** with `meta`, `memory`, `memory_vec` (sqlite-vec `FLOAT[384]`), `memory_fts` (FTS5)
- [x] `drop_row(id)` removes a row from `memory`, `memory_vec`, and `memory_fts` atomically (used by recall's ghost-pruning, REQ-011)
- [x] `meta.embed_load_ms` read/write helpers for the latency budget (REQ-008)
- [x] `embed(text)`: local `fastembed` (`bge-small-en-v1.5`) by default; uses `PB_EMBED_API`/`PB_EMBED_KEY` if set; records model+dim in `meta`
- [x] `upsert(kind, title, body, source_path)`: dedupes on `content_sha`, populates both `memory_vec` and `memory_fts`
- [x] `query(text, k)`: cosine top-k when vec+model available; FTS5 keyword fallback otherwise; returns `degraded` flag
- [x] Query refuses and instructs `make memory-rebuild` when `meta` model/dim ≠ current (REQ-006)
- [x] Import failure of `sqlite-vec`/`fastembed` degrades instead of raising (REQ-001)

> Implemented in `tools/memory_engine.py`, unit tests in `tools/tests/test_memory_engine.py` (14 passing). `embed()`'s fastembed/API branches are code-complete but untested against a live backend since `fastembed`/`sqlite-vec` aren't installed outside the isolated venv (Task 3.2) — exercised so far only via the FTS5-degraded path.

### Task 1.2: Secret-scrubbing before persistence
> Links to: REQ-002 (secret handling)

**Acceptance Criteria:**
- [x] Chunks matching credential/secret patterns are skipped before write/embed
- [x] Unit test: a transcript containing a fake API key produces no `memory` row for that chunk

> Implemented as `contains_secret()` in `tools/memory_engine.py`, wired into `upsert()`. Patterns cover OpenAI/Anthropic-style keys, AWS access key IDs, GitHub tokens, PEM private keys, and generic `key/secret/token/password: <value>` assignments.

## P0 — Critical (hooks)

### Task 2.1: `tools/memory_compact.py` (PreCompact)
> Links to: REQ-002, REQ-004, REQ-009, REQ-010

**Acceptance Criteria:**
- [x] Parses stdin through the shared host adapter (REQ-009) and binds all output paths to `resolve_project_root(cwd)` (REQ-010); test: invoked from a repo subdirectory, files land at the repo root
- [x] Extracts `<adr title><decision><rationale></adr>` blocks by regex (one markdown file each) + writes a heuristic session rollup
- [x] ADR filenames are `YYYY-MM-DD-HHMMSS-<slug>.md`; on residual collision with different content, an 8-char `content_sha` suffix is appended — test: two ADRs with the same slug in one run yield two files, no overwrite
- [x] Unit test: a transcript with two `<adr>` tags yields exactly two files in `docs/ai/adr/`; a transcript with none yields a rollup and zero ADR files (no false positives)
- [x] Writes markdown to `docs/ai/adr/` and `docs/ai/archive/` BEFORE embedding (source-of-truth-first)
- [x] Embeds+upserts via `memory_engine`; re-run on same input adds zero duplicate rows
- [x] Any error → log to `.ai-memory/engine.log`, empty stdout, exit 0 (REQ-004)

> Implemented in `tools/memory_compact.py`; the shared host adapter lives in `memory_engine.normalize_payload()`. Tests in `tools/tests/test_memory_compact.py` (9 passing, 23 total across the engine+hook suite). Secret-scrubbing is also applied here (skips the markdown write, not just the embed) for a stronger guarantee than the REQ-002 wording strictly requires.

### Task 2.2: `tools/memory_recall.py` (UserPromptSubmit, first prompt only)
> Links to: REQ-003, REQ-004, REQ-008, REQ-009, REQ-011

**Acceptance Criteria:**
- [x] Registered on `UserPromptSubmit` (Claude Code's `SessionStart` carries no prompt); gates on `.ai-memory/last_recall_session` sentinel — test: second prompt in the same session produces empty output via one sentinel read
- [x] Reads `prompt`/`cwd`/`session_id` via the shared host adapter (REQ-009); retrieves top-k (`PB_RECALL_K`, default 5)
- [x] Uses vector search only when `meta.embed_load_ms` exists and < `PB_RECALL_BUDGET_MS` (default 2000); otherwise FTS5 over prompt terms without importing the model (REQ-008) — test: budget-exceeded env never triggers a `fastembed` import
- [x] Existence-checks each hit's non-NULL `source_path`; missing file → row dropped from all three tables and next-best candidate backfills (REQ-011) — test: delete an ADR file, recall never shows it and the row is gone afterwards
- [x] Prints title + ≤120-char summary + source path per hit — never full ADR bodies
- [x] Total output hard-capped at `PB_RECALL_MAX_CHARS` (default 2000); test with 10 long ADRs asserts output ≤ cap and drops lowest-scoring hits
- [x] Prints nothing when empty/degraded
- [x] Any error → log + empty stdout + exit 0 (REQ-004)

> Implemented in `tools/memory_recall.py`. `memory_engine.query()` gained a `budget_ms` parameter: when the recorded `meta.embed_load_ms` is missing or over budget, it routes straight to FTS5 *before* ever calling `embed()`, so no `fastembed` import is attempted — verified by monkeypatching `_get_fastembed_model` to raise if called. Tests in `tools/tests/test_memory_recall.py` (16 passing, 37 total across the full engine+hooks suite).
>
> **Interpreted "prints nothing when empty/degraded"** (REQ-003) as: prints nothing when the final hit list is empty (no matches, or all candidates were ghosts). It does **not** suppress output merely because `degraded=true` (i.e. FTS5 was used instead of vector) — `design.md`'s own hook-contract table describes FTS5 fallback as "still relevance-ranked" and expects it to render results normally. Treating `degraded` as a hard mute would contradict that and silently defeat the latency-budget fallback path. Flagging this reading here since the two docs read as slightly in tension.

### Task 2.3: Hook resilience test
> Links to: REQ-004

**Acceptance Criteria:**
- [x] Test feeds malformed stdin and a simulated missing-dependency env to both hooks; both exit 0 with empty stdout
- [x] Test asserts a diagnostic line was appended to `.ai-memory/engine.log`

> Implemented in `tools/tests/test_hook_resilience.py`. The "missing-dependency env" isn't simulated/mocked — this sandbox genuinely has no `sqlite-vec`/`fastembed` installed, so every test in the suite already exercises the real degraded path; `TestAmbientEnvIsMissingDependency` pins that assumption down so the coverage claim stays true if deps are ever installed here later.

## P0 — Critical (install & wiring)

### Task 3.1: `scripts/install_settings.py` + hook propagation
> Links to: REQ-M01, REQ-009

**Acceptance Criteria:**
- [x] Tracked `settings.json` at repo root registers `PreCompact` → `~/.claude/venv/bin/python tools/memory_compact.py` and `UserPromptSubmit` → `…memory_recall.py`
- [x] `scripts/install_settings.py` reads source + installed settings JSON, deep-merges hook entries, dedupes by (matcher, command), writes back — no bash/jq merge
- [x] `install-claude` invokes it with destination `~/.claude`; `install-gemini` skips hook registration and prints the "Gemini hooks pending adapter validation (Task 3.4)" notice (REQ-009)
- [x] After `make install-claude`, installed `settings.json` contains both hook entries; a second `make install-claude` leaves exactly one copy of each (idempotency test)

> Implemented in `scripts/install_settings.py` (18 tests in `tools/tests/test_install_settings.py`) plus edits to `settings.json` and `Makefile`. Verified end-to-end against a **fake `$HOME`** (never the real `~/.claude`) with `HOME=/tmp/... make install-claude`, twice, with a pre-existing custom hook + `permissions` block in place — both were preserved, our two hook entries were added exactly once each on both runs.
>
> **Two corrections made while implementing, both load-bearing:**
> 1. **Command paths are absolute (`$HOME/.claude/tools/memory_*.py`), not relative.** Verified against the official Claude Code hooks docs: a hook's `cwd` is the *project* working directory the user launched from, not `~/.claude`. `design.md`'s literal phrasing ("`~/.claude/venv/bin/python tools/memory_compact.py`") would resolve `tools/memory_compact.py` against the wrong directory and fail for every user whose project isn't literally `~/.claude` itself.
> 2. **Command falls back to `python3` when the venv is absent**, via inline shell (`PY="$HOME/.claude/venv/bin/python"; [ -x "$PY" ] || PY=python3; "$PY" ...`), instead of invoking the venv interpreter unconditionally. Without this, REQ-007's "absent venv → hooks degrade" guarantee is unreachable: if the shell can't find the venv's `python` binary at all, the OS fails to spawn the process before any of our Python-level try/except (which is where the actual degradation logic lives) ever runs. Confirmed by executing the command string directly against a fake `$HOME` with no venv — resolves to `python3`, exits 0.
>
> **Also fixed:** `install-claude`/`install-gemini` previously ran `cp -r ./* ~/.claude/` unconditionally, which — now that this repo tracks a root-level `settings.json` — would have silently overwritten any pre-existing installed `settings.json` (a user's own hooks/permissions) before any merge logic ran. Both install targets now back up an existing destination `settings.json`, let the copy proceed, then restore the backup before `install_settings.py` merges into it (Gemini: restore only, no merge — see Task 3.4 gate).
>
> **Flag for Task 3.2:** `scripts/cleanup.sh` (which both install targets run at the end) deletes `Makefile` and `scripts/` from the installed `~/.claude`/`~/.gemini` tree as dev-only cruft. `make memory-setup`/`make memory-rebuild`/`make memory-bench` are Makefile targets — whoever implements Task 3.2/4.1 needs a plan for invoking them post-cleanup (e.g. run from the source checkout with `PB_MEMORY_ROOT` pointed at a project, not from the installed `~/.claude` tree).

### Task 3.2: Isolated venv setup
> Links to: REQ-007, REQ-008

**Acceptance Criteria:**
- [x] `make memory-setup` creates `~/.claude/venv` and `~/.gemini/venv` and installs `requirements.txt` into each; not into global Python
- [x] `memory-setup` finishes by running the cold-start micro-benchmark and recording `meta.embed_load_ms`; standalone re-runnable as `make memory-bench` (REQ-008)
- [x] Idempotent: re-running does not error or rebuild from scratch unnecessarily
- [x] Verified: a `make install` after `memory-setup` leaves the venv intact (venv path is outside the `rm -rf` list and `cleanup.sh` DEV_ITEMS)

> Makefile targets (`memory-setup`, `memory-bench`) and `tools/memory_bench.py` are implemented and syntax/logic-verified (`make -n`, plus `memory_bench.bench()` tested against a stubbed `fastembed` module — this sandbox has no real `fastembed`/`onnxruntime`, see `TestAmbientEnvIsMissingDependency`). **`make memory-setup` was deliberately never run for real against this machine** — per user decision, no real `pip install` of the heavy deps was performed. The venv-survives-`rm -rf`/`cleanup.sh` claim is verified by inspection (neither list references `venv`), not by an end-to-end run.
>
> **Design gap found and fixed:** `meta.embed_load_ms` lives in each *project's* `.ai-memory/memory.db`, but `memory-setup`/`memory-bench` run once, globally, from wherever the framework checkout happens to be — there's no clean way for that one-time step to know which project(s) to calibrate, and `cleanup.sh` strips the `Makefile` from the installed tree anyway (see Task 3.1's note), so `make memory-bench` isn't even reachable from inside a typical user project post-install. Fixed by having `memory_engine.upsert()` **auto-record `embed_load_ms`** into the current project's DB the first time it actually loads the real model — this happens naturally on that project's first `PreCompact` run (PreCompact is explicitly allowed to pay the cold-load cost). `make memory-bench`/`memory_bench.py` still exist for explicit manual (re)calibration, but auto-calibration via `PreCompact` is what makes REQ-008 work in practice for real projects. 9 tests in `tools/tests/test_memory_bench.py`.

### Task 3.3: Dependencies & ignore rules
> Links to: REQ-001, REQ-005

**Acceptance Criteria:**
- [x] `requirements.txt` created with `fastembed` and `sqlite-vec` (pinned)
- [x] `.gitignore` gains `.ai-memory/`
- [ ] Docs state the enable path is `make memory-setup` (venv), and that without it the framework runs normally in degraded mode

> `requirements.txt` and the `.gitignore` entry are done. Version pins (`fastembed==0.8.0`, `sqlite-vec==0.1.9`) were checked against the live PyPI JSON API, not guessed — an earlier draft of this file had fabricated, nonexistent version numbers, which would have made `make memory-setup` fail outright. The docs bullet is deferred to Task 4.2 (skill/rules updates), where it belongs alongside the rest of the user-facing documentation.

### Task 3.4: Gemini hook adapter verification (gate for Gemini registration)
> Links to: REQ-009

**Acceptance Criteria:**
- [ ] Capture a real hook stdin payload from the Gemini orchestrator (or document that it exposes no equivalent hook events)
- [ ] Extend the host adapter to map the captured schema to the normalized payload; add a fixture-based unit test per host
- [ ] Only after this lands: `install-gemini` registers the hooks via `scripts/install_settings.py` with destination `~/.gemini`
- [x] Until then: `specs.md`/README document that Gemini support = `make memory-rebuild` + degraded recall only

> **Genuinely blocked, not attempted.** Capturing a real Gemini orchestrator hook payload requires an actual Gemini CLI session, which isn't available in this environment — fabricating a guessed schema here would be worse than leaving this undone, since `memory_engine.normalize_payload()` would silently "succeed" against a made-up shape and mask real field names when someone finally does check. `install-gemini` already prints the pending-adapter notice (Task 3.1) and this remains the gate on Gemini hook registration. Whoever picks this up next needs one real captured payload (any event) from a live Gemini Code Assist / Gemini CLI hook invocation to extend `normalize_payload()` correctly.

## P1 — High (lifecycle & docs)

### Task 4.1: Makefile lifecycle targets
> Links to: REQ-005

**Acceptance Criteria:**
- [x] `make memory-init` creates an empty, schema-correct `.ai-memory/memory.db`
- [x] `make memory-rebuild` truncates + re-embeds all `docs/ai/adr/` + `docs/ai/archive/` markdown; idempotent (REQ-005)

> Implemented as `tools/memory_init.py` and `tools/memory_rebuild.py` (wired into the Makefile as `memory-init`/`memory-rebuild`). 7 tests in `tools/tests/test_memory_lifecycle.py`, covering fresh-clone rebuild, idempotency, deleted-markdown row pruning, and edited-markdown re-embedding. `memory_rebuild.py` hashes each markdown file's full on-disk content for `content_sha` (not the same "stable body" hash `memory_compact.py` uses pre-render) — the two hash spaces don't need to match since rebuild always truncates first; the only cross-run guarantee that matters (REQ-005) is rebuild-vs-rebuild idempotency, which is tested directly.

### Task 4.2: Update memory skills & rules
> Links to: REQ-M02

**Acceptance Criteria:**
- [x] `project-memory/SKILL.md` documents the automated tier, `.ai-memory/` + `docs/ai/adr/` layout, and shows the literal `<adr title><decision><rationale></adr>` tag the agent must emit for capture
- [x] `context-management/SKILL.md` and `core/memory_rules.md` note that pruning/recall is now hook-enforced, with the Slot discipline as documented fallback
- [x] `project-memory` YAML `description` updated if it should trigger on "long-term memory"/"ADR recall"

> Added a new "Section 0: Automated Long-Term Tier" to `project-memory/SKILL.md` (layout table, the literal `<adr>` tag, recall behavior, degradation note), plus a cross-reference row in its Integration table. `context-management/SKILL.md` and `core/memory_rules.md` both gained a short section stating the hooks are enforcement (run regardless of agent discipline) and that the existing Slot/MVC rules remain the complete fallback when hooks are absent. `project-memory`'s `description` and `triggers` (`long-term memory`, `adr`, `adr recall`) were updated accordingly, and `make registry` was re-run to pick up the change (verified via `registry.min.json`'s `project-memory` entry) — this is also half of Task 5.1's acceptance.

## P0 — Gating (do last)

### Task 5.1: Regenerate registry & redeploy
> Links to: all REQs

**Acceptance Criteria:**
- [x] `make registry` run; `registry.min.json` reflects any `project-memory` description change
- [ ] `make install-claude` / `make install-gemini` run; Claude hook presence in installed `settings.json` re-verified, Gemini skip-notice verified (REQ-M01)
- [x] End-to-end smoke: run `memory_compact.py` on a sample transcript **from a repo subdirectory**, then `memory_recall.py` with a related first prompt, and confirm the relevant memory pointer is surfaced from the root-level DB

> `make registry` run and verified (`project-memory`'s updated description is in `registry.min.json`). The end-to-end smoke test is formalized in `tools/tests/test_end_to_end_smoke.py`: launches `memory_compact.py` from `<repo>/server/pkg/llm/` with an ADR-tagged transcript, confirms `.ai-memory/`+`docs/ai/adr/` land at the repo root (not the subdirectory), then launches `memory_recall.py` from the same subdirectory with a related first prompt and confirms the ADR pointer is surfaced with its `docs/ai/adr/...` path.
>
> **`make install-claude`/`make install-gemini` deliberately NOT run for real** — this is the one step in the whole spec that mutates the user's actual `~/.claude`/`~/.gemini`, and every other acceptance criterion for it (merge correctness, idempotency, preservation of pre-existing hooks) is already verified in `tools/tests/test_install_settings.py` and the earlier fake-`$HOME` Makefile run — real execution here is a deploy step, not a correctness question, and should be an explicit user decision.
