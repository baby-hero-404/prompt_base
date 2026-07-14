# Proposal: Automated Context Memory Engine

## Why
Today's "Minimal Viable Context" (MVC) is **discipline-based, not enforced**. It depends on the agent voluntarily doing the right thing:
- `core/memory_rules.md` asks the agent to self-manage context "Slots" and "PRUNE after EVERY major sub-task" — a rule the LLM must remember to apply mid-task.
- `context-management/SKILL.md` is four aspirational bullets ("Summarize older conversation history," "remove redundant skill documentation").
- `project-memory` persists structured markdown in `docs/ai/`, but a human/agent must remember to update it, and it only holds *current* state — there is no long-term, searchable record of *why* past decisions were made.

Two concrete failure modes result:
1. **Token bloat on long sessions.** Nothing actually compresses a growing transcript; the agent is simply told to be tidy. When it isn't, context fills and reasoning degrades.
2. **Lost architectural memory.** A decision made months ago (an ADR) lives only in git history or a human's head. The agent cannot answer "why did we choose X over Y back then?" without a full-repo/history spelunk — the exact rescanning `project-memory` was built to avoid.

This proposal upgrades `project-memory` from *passive markdown files* into an **automated, hook-driven memory engine**: transcript content and architectural decisions are compressed and embedded into a per-project vector store at session boundaries, then semantically recalled at the start of the next session. Automation is enforced by Claude Code hooks, not by agent goodwill.

## Design decisions (settled before authoring — see `design.md` for rationale)
- **Storage:** local vector DB via **`sqlite-vec`** (a single-file SQLite extension — no server, fits the per-project + hook model).
- **Embeddings:** **local ONNX model by default** (`fastembed`, offline, no API key) to preserve this framework's self-contained ethos; an external embedding API is an opt-in fallback via env var.
- **Trigger:** **Claude Code hooks** — `PreCompact` compresses+embeds before the harness compacts; `SessionStart` recalls relevant memories.
- **Location:** **global**, under `~/.claude/prompt_base_memory/{project_name}-{project_hash}/` (can be overridden to local `.ai-memory/` at the repo root by setting `PB_LOCAL_MEMORY=1`).

## The philosophy bridge (important)
The existing memory system deliberately chose **git-versioned, PR-reviewable markdown**. A binary vector DB would break that. This proposal keeps the property by splitting **source of truth** from **index**:
- **Source of truth = markdown**, git-tracked: ADRs in `docs/ai/adr/` and rollup summaries in `docs/ai/archive/`. Still human-readable and reviewable in PRs.
- **Index = `memory.db`** (stored globally, or local `.ai-memory/` if `PB_LOCAL_MEMORY=1`), fully rebuildable from that markdown via `make memory-rebuild`. It is a cache, never the only copy of anything.

## What Changes

### Issue 1: Automated compression (PreCompact)
- New hook script chunks the session transcript + any ADRs the agent emitted with a hard `<adr>` tag, embeds them, and upserts into the per-project vector store before the harness compacts context. ADR extraction is by strict tag/regex, not heuristic guessing.

### Issue 2: Automated recall (SessionStart)
- New hook script embeds the current session goal and injects the top-k most relevant past memories — as **title + one-line summary + file path**, under a hard character budget — so recall itself never re-introduces token bloat. The agent reads full ADR bodies on demand.

### Issue 3: Graceful degradation
- If `sqlite-vec` / `fastembed` are unavailable, the engine falls back to SQLite **FTS5 keyword search** and never hard-fails a session (hooks always exit 0).

### Issue 4: Skill & rules integration
- `project-memory`, `context-management`, and `core/memory_rules.md` are updated to describe the automated archive tier and the ADR-markdown convention, so the agent knows the engine exists and how to flag an ADR for capture.

### Issue 5: Install-pipeline, isolation & dependency plumbing
- Ship a tracked `settings.json` with the hook registration and extend `install-*` to actually merge it in via `scripts/install_settings.py` (`cp -r ./*` skips dotfiles, and a bash/jq merge is unsafe).
- Isolate the heavy native deps (`fastembed`/`onnxruntime`, `sqlite-vec`) in a dedicated **venv** at `~/.claude/venv` (and `~/.gemini/venv`), built by an opt-in `make memory-setup` — never installed into the user's global Python. Hooks invoke `venv/bin/python`.
- Add a `requirements.txt`; add `.ai-memory/` to `.gitignore`.

## Capabilities

### New Capabilities
- Automated, hook-enforced context compression at session boundaries.
- Semantic recall of past decisions/ADRs across sessions (long-term memory).
- `make memory-rebuild` / `make memory-init` lifecycle commands.

### Modified Capabilities
- `project-memory` gains an automated long-term tier (its markdown tier is unchanged).
- `context-management` / `memory_rules` describe enforced (not just advisory) pruning.

### Removed Capabilities
- None. The discipline-based rules remain as the fallback when hooks are disabled.

## Impact

| Area | Files Affected |
|------|----------------|
| Engine (shared lib) | `tools/memory_engine.py` (new) — schema, chunk, embed, upsert, query, degradation |
| Hook: compress | `tools/memory_compact.py` (new) — `PreCompact` entry point |
| Hook: recall | `tools/memory_recall.py` (new) — `SessionStart` entry point |
| Hook registration | `settings.json` (new, tracked) + `scripts/install_settings.py` (new, safe idempotent merge) wired into `install-*` |
| Runtime isolation | `Makefile` — `memory-setup` builds `~/.claude/venv` / `~/.gemini/venv` with pinned deps |
| Lifecycle commands | `Makefile` — `memory-init`, `memory-rebuild` targets |
| Dependencies | `requirements.txt` (new); `.gitignore` (add `.ai-memory/`, keep `venv/` out of installs' cleanup) |
| Skill docs | `antigravity/skills/core/project-memory/SKILL.md`, `antigravity/skills/core/context-management/SKILL.md` |
| Core rules | `core/memory_rules.md` |
| Registry | `registry.min.json` (regenerated if `project-memory` description changes) |
| ADR/archive source | `docs/ai/adr/`, `docs/ai/archive/` (markdown, created at runtime) |
