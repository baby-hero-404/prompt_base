# Spec: Real ADR Population & Semantic/FTS5 Recall Evaluation

## 1. Goal
Populate `docs/ai/adr/` with real architectural decisions from Prompt Base and implement an evaluation script (`scripts/test_memory_eval.py`) to test and compare exact keyword matching (FTS5) against semantic vector recall (`sqlite-vec` + `fastembed`).

## 2. ADR Definitions
Create 3 authentic ADR documents in `docs/ai/adr/`:
1. `2026-10-23-001-isolated-venvs-for-heavy-dependencies.md`
   - Decision: Heavy machine learning / vector dependencies (`fastembed`, `sqlite-vec`) live only in per-agent isolated venvs (`~/.claude/venv`, `~/.gemini/venv`), never in the global Python environment.
2. `2026-10-23-002-dual-hybrid-search-recall.md`
   - Decision: Graceful degradation from `sqlite-vec` semantic similarity to SQLite FTS5 BM25 keyword matching when dependencies are missing or cold-start latency budget is exceeded.
3. `2026-10-23-003-git-tracked-markdown-memory-store.md`
   - Decision: Project memory canonical store is Git-tracked Markdown files under `docs/ai/` (`PROFILE.md`, `DOMAIN.md`, `manifest.json`, `adr/`, `archive/`). SQLite databases and vector indexes are disposable derived accelerators.

## 3. Evaluation Script (`scripts/test_memory_eval.py`)
- Rebuilds memory database with vector embeddings using the venv Python (`~/.claude/venv/bin/python`).
- Executes test queries across 4 categories:
  - Exact keyword query (BM25 FTS5).
  - Semantic concept query with non-overlapping terminology (Vector).
  - Cross-cutting architectural query.
  - Irrelevant/negative query (verify low similarity / no false positives).
- Outputs a formatted comparison table comparing FTS5 vs Vector results, distances/scores, and degradation behavior.
