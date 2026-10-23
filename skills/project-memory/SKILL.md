---
name: project-memory
description: "Use when loading or managing persistent project-level context from global memory, including automated long-term memory (ADR capture/recall) via the context memory engine. Triggers on memory, adr capture."
triggers:
  - session-start
  - "project"
  - "architecture"
  - "system overview"
  - "init-context"
  - "init-memory"
  - "project memory"
  - "context cache"
  - "long-term memory"
  - "adr"
  - "adr recall"
---
# Project Memory & Context Cache

> **Core Principle:** Transform "AI discovers the project" into "AI reads structured project memory."
> Every session should bootstrap from cached context files — never rescan the full codebase unless explicitly required.

---

## 0. Automated Long-Term Tier (Hook-Enforced)

### Memory layers (shared by every agent)

**Rule:** the source of truth is plain markdown in the project repo under `docs/ai/`, readable by any agent (Claude Code, Gemini/Antigravity, Codex, Cursor...). Hooks, databases and embeddings are per-agent accelerators and are always rebuildable from that markdown.

| Layer | Location | Holds | Written by | Agent-neutral? |
|-------|----------|-------|------------|----------------|
| Profile | `docs/ai/PROFILE.md` | Identity, stack, repo map | `/init-memory` | Yes (markdown) |
| Invariants | `docs/ai/DOMAIN.md` | Domain rules with source rule IDs + enforcement tags | `/init-memory` | Yes. Re-injected by `tools/memory_invariants.py` (Claude hook, or `--print` for any agent) |
| Freshness | `docs/ai/manifest.json` | `autoRefreshTriggers` + `checksums` | `tools/memory_stale.py --update` | Yes (any agent runs the script) |
| Decisions (why) | `docs/ai/adr/`, `docs/ai/archive/` | ADRs, session rollups | `PreCompact` hook from `<adr>` tags, or by hand | Source files yes; hook capture is Claude-only |
| Derived index | `~/.claude/prompt_base_memory/<name>-<hash>/` | FTS/vector index of the above | hooks, `make memory-rebuild` | No (disposable) |
| Preferences | Claude Code native auto-memory (`~/.claude/projects/.../memory/`) | User/feedback notes | Claude Code itself | No. Never use it as the shared store |
| Task progress | `docs/openspecs/<task>/tasks.md` | Checkbox state | the agent doing the task | Yes |

Opt-in: memory exists only in projects where the user ran `/init-memory`; elsewhere no files are created and the memory hooks do nothing (they need `docs/ai/` and a trusted project). `/init-context` is read-only.

Legacy: `~/.gemini/projects/<parent>-<leaf>/` held PROFILE/DOMAIN before `docs/ai/`. It is read as a fallback only; migrate by copying the files into `docs/ai/`.

Trust: hooks that act on repo content (invariant injection, Stop gate) run only for projects the user trusted with `python3 tools/pb_trust.py --add`; the list lives outside the repo.

Staleness: `python3 tools/memory_stale.py --root .` exits 1 when a file in `autoRefreshTriggers` changed since the last `--update`; refresh with `/init-memory`.

### Automated long-term tier (Claude hooks)

There is a separate, **automated long-term tier** for *why past decisions were made*, enforced by Claude Code hooks (not agent discipline):

| Layer | Location | Written by |
|-------|----------|------------|
| Decision records (source of truth, git-tracked) | `docs/ai/adr/YYYY-MM-DD-HHMMSS-<slug>.md` | `PreCompact` hook, from `<adr>` tags you emit |
| Session rollups (source of truth, git-tracked) | `docs/ai/archive/YYYY-MM-DD-HHMMSS-<slug>.md` | `PreCompact` hook, heuristic, every compaction |
| Derived index (disposable, stored globally) | `~/.claude/prompt_base_memory/{project_name}-{hash}/` (or `.ai-memory/` if `PB_LOCAL_MEMORY=1`) | Both hooks; rebuild anytime with `make memory-rebuild` |

**To get a decision captured**, emit this exact tag when you make (or the user confirms) an architecturally significant choice — the `PreCompact` hook extracts it by strict regex, not heuristic guessing, so the tag must match verbatim:

```
<adr title="Short decision title">
  <decision>What was decided, one or two sentences.</decision>
  <rationale>Why, including the alternative(s) rejected.</rationale>
</adr>
```

You do not need to do anything else — no manual file writing, no explicit "save this." The tag is enough; the hook handles extraction, dedup, secret-scrubbing, and embedding automatically at the next compaction.

**Recall is automatic too**: at the first prompt of a new session, a `UserPromptSubmit` hook injects the top-k most relevant past ADRs/rollups as `title — summary (path)` pointers (never full bodies, hard-capped in size). If a pointer looks relevant, read the file at that path — don't ask the user to repeat context that's already been surfaced.

If hooks are disabled or `sqlite-vec`/`fastembed` aren't installed, this tier degrades to keyword (FTS5) search automatically — recall still works, just without semantic ranking. Nothing about this tier changes the rest of this skill: the `docs/ai/` structure below remains the manually-maintained **current-state** memory.

---

## 1. Purpose

Eliminate redundant project scanning across AI sessions by maintaining a set of **structured context files** inside the repository. These files serve as the AI's persistent memory — a pre-compiled understanding of the project's architecture, patterns, file layout, and task progress.

### Why This Matters

| Without Project Memory | With Project Memory |
|------------------------|---------------------|
| AI scans entire codebase each session | AI reads 4–5 small files |
| High token consumption on discovery | Tokens spent on actual work |
| Slow session startup | Instant productive context |
| Inconsistent understanding | Stable, versioned knowledge |
| Repeated pattern violations | Enforced pattern adherence |

---

## 2. Context File Structure

All project memory lives in `docs/ai/`, separated from human-facing documentation:

```
docs/ai/
├── PROFILE.md        # identity, architecture, stack, repo map
├── DOMAIN.md         # concepts, "## Invariant Rules", quirks
├── manifest.json     # autoRefreshTriggers + checksums (staleness)
├── adr/              # decision records (hook- or hand-written)
├── archive/          # session rollups (hook-written)
└── progress/         # optional TASK_STATUS.md / PHASE_PLAN.md
```

Templates: `projects/_template/` (`PROFILE.md`, `DOMAIN.md`, `manifest.json`, `projects/_template/rules/README.md` for the rule ID + enforcement tag convention). `DOMAIN.md` Invariant Rules cite the project's own rule IDs, e.g. `1.2 [test] domain/ never imports Flutter`, capped at about 13 lines because they are re-injected into context.

The older `AI_PROJECT_CONTEXT.md` / `PROJECT_INDEX.md` / `CODING_PATTERNS.md` files are superseded by `PROFILE.md` + `DOMAIN.md`.

## Extended References
For less-frequently-needed detail, see [`references/extended-reference.md`](references/extended-reference.md):
- 2.2 `PROJECT_INDEX.md` — File Map (superseded by `PROFILE.md` Repository Map)
- 2.3 `CODING_PATTERNS.md` — Conventions & Patterns (superseded by `DOMAIN.md`)
- 2.4 `TASK_STATUS.md` — Progress Tracker
- 2.5 `PHASE_PLAN.md` — Roadmap (Optional)
- 3. Session Bootstrap Protocol
- 3.1 On Session Start
- 3.2 Bootstrap Prompt Template
- 3.3 Fallback: Missing Context Files
- 4. Context Update Protocol
- 4.1 After Every Task Completion
- 4.2 Update Rules
- 5. Memory Management
- 5.1 What Goes IN Project Memory
- 5.2 What Stays OUT of Project Memory
- 5.3 Staleness Prevention
- 6. Integration with Other Skills
- 7. Quick Reference
