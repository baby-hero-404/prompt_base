# Proposal: Memory Management Refresh

## Context & Motivation
Project memory spans overlapping layers, none of them agent-neutral:
1. `~/.gemini/projects/<name>/` profile (`PROFILE.md`, `DOMAIN.md`, `manifest.json`): Gemini-named, Claude never auto-loads it.
2. `docs/ai/` current-state memory (project-memory skill §2): a competing design, unused.
3. ADR engine DB under `~/.claude/prompt_base_memory/`: hooks are Claude-only, DBs for prompt_base have 0 rows, no venv (FTS-only).
4. Claude Code native auto-memory (`~/.claude/projects/.../memory/`): not mentioned by the framework; must not be used as the shared store.
`manifest.json` fields `checksums` / `autoRefreshTriggers` / `lastScanned` are read by no code.

## Requirement (user, 2026-10-23)
Memory is shared by many agents (Claude Code, Gemini/Antigravity, others), not Claude-only.

## Decisions (user, 2026-10-23)
- **Source of truth = markdown in the project repo under `docs/ai/`**: `PROFILE.md`, `DOMAIN.md`, `manifest.json`, `adr/`, `archive/`. Any agent can read it; it travels with the clone.
- Hooks, DBs and embeddings are optional per-agent accelerators, always rebuildable from that markdown.
- The legacy `~/.gemini/projects/<name>/` is read as a fallback only; `/init-context` writes `docs/ai/` and asks before writing into a project repo.
- Invariants are re-injected on the 1st prompt and every 10th prompt, for trusted projects only (`tools/pb_trust.py`; a repo cannot trust itself).
- Run `make memory-setup` (pinned `fastembed==0.8.0`, `sqlite-vec==0.1.9`, isolated venvs).
- Prune the duplicate prompt_base DB dir only after listing it and getting explicit confirmation.

- **Memory is opt-in per project (user, 2026-10-23):** new `/init-memory` workflow creates `docs/ai/` and trusts the project; `/init-context` is read-only; capture and recall hooks act only where `docs/ai/` exists and the project is trusted. Reason found in review: the global PreCompact hook was writing `docs/ai/archive/*.md` into every git repo.

## Scope (M1 - M5)
- **M1: Unified memory model** (docs): layers table with an "agent-neutral?" column; `docs/ai/` canonical.
- **M2: Staleness check**: `tools/memory_stale.py` over `docs/ai/manifest.json` `autoRefreshTriggers`.
- **M3: Invariant re-injection**: agent-neutral CLI `tools/memory_invariants.py`; Claude `UserPromptSubmit` hook adapter; rule line for agents without verified hooks (advisory `[review]`).
- **M5: Opt-in**: `global_workflows/init-memory.md`; `/init-context` read-only; `pb_trust.memory_enabled` gate in `memory_compact.py` / `memory_recall.py`; `pb_trust --remove`.
- **M4: Operations**: `tools/memory_status.py` + `make memory-status`, `make memory-setup`, confirmed prune.

## Non-goals
- Gemini hook adapter (payload schema unverified, see Makefile note).
- Changing the ADR engine storage default `~/.claude/prompt_base_memory/` (derived index only; override already exists via `PB_GLOBAL_MEMORY_DIR`).
