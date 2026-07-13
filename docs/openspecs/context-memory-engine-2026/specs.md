# Specs: Automated Context Memory Engine

## Added Requirements

### REQ-001: Vector store engine with keyword fallback
> ❌ Status: Not Started

**Scenario:**
- WHEN `tools/memory_engine.py` is initialized against a project
- THEN it creates `.ai-memory/memory.db` with the `meta`, `memory`, `memory_vec` (sqlite-vec), and `memory_fts` (FTS5) objects
- AND WHEN `sqlite-vec` or the embedding model cannot be imported
- THEN queries transparently fall back to FTS5 keyword search and the engine reports `degraded=true` rather than raising

### REQ-002: PreCompact compression writes markdown, then embeds
> ❌ Status: Not Started

**Scenario:**
- WHEN the `PreCompact` hook fires and `memory_compact.py` receives a transcript path
- THEN every `<adr title="…"><decision>…</decision><rationale>…</rationale></adr>` block is extracted by regex (not heuristic guessing) and written as one markdown file under `docs/ai/adr/YYYY-MM-DD-HHMMSS-<slug>.md`, and a session rollup is written under `docs/ai/archive/`, BEFORE anything is embedded
- AND WHEN a target ADR filename already exists with different content (same second and slug)
- THEN an 8-char `content_sha` suffix is appended to the new file's name — an existing file is never overwritten
- AND a transcript containing no `<adr>` tag still produces a rollup and simply captures no ADR (no false positives)
- AND each resulting chunk is embedded and upserted into `.ai-memory/memory.db`, keyed by `content_sha` so re-running the same input inserts no duplicates
- AND chunks matching secret/credential patterns are skipped and never persisted

### REQ-003: First-prompt recall injects relevant memories
> ❌ Status: Not Started

**Scenario:**
- WHEN the `UserPromptSubmit` hook fires with the **first** prompt of a session (Claude Code's `SessionStart` payload carries no goal, so recall registers on `UserPromptSubmit` and gates on a `.ai-memory/last_recall_session` sentinel)
- THEN it retrieves the top-k (default 5, `PB_RECALL_K`) most relevant memories — cosine similarity when within the latency budget (REQ-008), FTS5 over prompt terms otherwise
- AND prints them as **title + one-line (≤120-char) summary + source path pointers only** — never full ADR bodies
- AND the total injected text is hard-capped at `PB_RECALL_MAX_CHARS` (default 2000); if top-k exceeds it, lowest-scoring hits are dropped until it fits, so recall cannot itself cause token bloat
- AND WHEN a subsequent prompt fires in the same session, the hook is a no-op (one sentinel read, empty output, exit 0)
- AND WHEN the store is empty or degraded, it prints nothing and exits 0 (no error, no noise)

### REQ-004: Hooks never break a session
> ❌ Status: Not Started

**Scenario:**
- WHEN either hook script encounters any internal error (malformed stdin, missing dependency, locked/corrupt DB)
- THEN it catches the error, appends a diagnostic line to `.ai-memory/engine.log`, emits empty stdout, and exits with status 0

### REQ-005: Rebuildable index (DB is disposable)
> ❌ Status: Not Started

**Scenario:**
- WHEN `make memory-rebuild` is run in a repo that has `docs/ai/adr/` + `docs/ai/archive/` markdown but no `.ai-memory/memory.db` (e.g. a fresh clone)
- THEN the DB is recreated and every markdown source is re-embedded, restoring full recall
- AND running it twice produces an identical row set (idempotent via `content_sha`)

### REQ-006: Embedding-model drift is detected, not silently tolerated
> ❌ Status: Not Started

**Scenario:**
- WHEN the configured embedding model or vector dimension differs from what the `meta` table recorded
- THEN a recall query refuses to return possibly-corrupt similarity results and instructs the user to run `make memory-rebuild`

### REQ-007: Heavy deps isolated in a dedicated venv
> ❌ Status: Not Started

**Scenario:**
- WHEN `make memory-setup` is run
- THEN a venv is created at `~/.claude/venv` (and `~/.gemini/venv`) and `requirements.txt` is installed into it — nothing is installed into the user's global Python
- AND re-running `make install` (which `rm -rf`s framework dirs) does not delete the venv, and `make memory-setup` is idempotent
- AND WHEN the venv does not exist, both hooks detect its absence and degrade (no-op / FTS5) rather than crashing on a missing import

### REQ-008: Recall respects a cold-start latency budget
> ❌ Status: Not Started

**Scenario:**
- WHEN `make memory-setup` (or `make memory-bench`) runs
- THEN cold import+embed wall-clock time is measured and recorded as `meta.embed_load_ms`
- AND WHEN recall runs and `meta.embed_load_ms` is absent or ≥ `PB_RECALL_BUDGET_MS` (default 2000)
- THEN recall uses FTS5 keyword search over the prompt terms and never begins loading the ONNX model (the decision is made up front, not by aborting a load)
- AND `PreCompact` (non-user-blocking) may always load the model regardless of budget

### REQ-009: Uniform hook stdin contract across hosts
> ❌ Status: Not Started

**Scenario:**
- WHEN either hook receives stdin JSON from any host
- THEN it is normalized through a single adapter into the internal payload `{host, event, cwd, session_id, transcript_path, prompt}` defined in `design.md`, with missing/unknown fields becoming `null` (never an exception)
- AND WHEN the payload cannot be mapped to a known host/event (e.g. an unverified Gemini schema)
- THEN the hook no-ops with empty stdout and exit 0
- AND `install-gemini` does NOT register the hooks until the Gemini adapter is validated against a captured real payload (Task 3.4); this limitation is documented

### REQ-010: All engine paths bind to the resolved project root
> ❌ Status: Not Started

**Scenario:**
- WHEN a hook runs from a subdirectory of a repo (e.g. `server/pkg/llm/`)
- THEN it resolves the project root by: `PB_MEMORY_ROOT` if set → upward walk from the payload `cwd` to the first ancestor containing `.git` (dir or file), else `CLAUDE.md`/`GEMINI.md`/`ARCHITECTURE.md` → logged fallback to `cwd`
- AND `.ai-memory/`, `docs/ai/adr/`, and `docs/ai/archive/` are all created under that root — never under the launch subdirectory
- AND repeated launches from different subdirectories of the same repo use the same single `memory.db`

### REQ-011: Deleted markdown never serves ghost memories
> ❌ Status: Not Started

**Scenario:**
- WHEN recall produces a hit whose non-NULL `source_path` no longer exists on disk (its markdown was manually deleted)
- THEN that row and its `memory_vec`/`memory_fts` entries are deleted immediately, the hit is not rendered, and the next-best candidate backfills the result set
- AND rows with `source_path = NULL` (raw transcript chunks) are exempt from the check
- AND `make memory-rebuild` remains the full reconciliation path for edited (not just deleted) markdown

## Modified Requirements

### REQ-M01: Hooks are registered and survive install
> ❌ Status: Not Started

**Scenario:**
- WHEN `make install-claude` completes
- THEN the installed `~/.claude/settings.json` contains the `PreCompact` and `UserPromptSubmit` hook entries invoking `~/.claude/venv/bin/python tools/memory_compact.py` and `…memory_recall.py`
- AND the merge is performed by `scripts/install_settings.py` (not bash/jq), preserving any pre-existing user hooks
- AND running `make install-claude` twice yields exactly one copy of each hook entry (idempotent, no duplication)
- AND WHEN `make install-gemini` completes
- THEN no hook entries are registered for Gemini until REQ-009's adapter validation lands (Task 3.4), and the install output/docs state this

### REQ-M02: Memory skills/rules describe the automated tier
> ❌ Status: Not Started

**Scenario:**
- WHEN an agent reads `project-memory`, `context-management`, or `core/memory_rules.md`
- THEN each explains that long-term memory is now automated via hooks, where the archive lives (`.ai-memory/` + `docs/ai/adr/`), and shows the exact `<adr>…</adr>` tag the agent must emit for a decision to be captured by `PreCompact`
- AND the existing discipline-based Slot rules remain documented as the fallback when hooks are disabled

## Removed Requirements
- None
