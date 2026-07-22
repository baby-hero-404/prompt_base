# Report: Token Reduction Opportunities for Prompt Base

> Revised 2026-07-14. The original draft of this report borrowed ideas from the
> "Awesome LLM Token Reduction" list without checking them against this
> project's architecture; several of its premises were wrong. The 2026-07-13
> revision fixed that, but two of its own recommendations (P2, P3) turned out
> to already be implemented by the *same commit* (`b58e467`) that introduced
> this report — the report's action items just weren't updated to reflect it.
> This revision corrects that: verified-open items and already-done items are
> now separated, and the stale claims are marked so they aren't re-proposed.

## 1. Overview and Current State

`prompt_base` is a **configuration framework** — rules (`CLAUDE.md`/`GEMINI.md`),
skills, a registry, and hook scripts — installed into `~/.claude` / `~/.gemini`.
It is *not* a runtime: the tools the agent calls (`Read`, `Grep`, Bash, etc.)
belong to the host harness, and their outputs enter context directly. Nothing
in this repo sits between the model and its tools.

The **Automated Context Memory Engine** already handles the macro
problem — long-term memory and session-boundary compression — via two hooks:

- `PreCompact` → `tools/memory_compact.py`: extracts `<adr>`-tagged decisions
  by strict regex (no chunking of code files), writes git-tracked markdown,
  embeds into `.ai-memory/memory.db`.
- `UserPromptSubmit` (first prompt of session) → `tools/memory_recall.py`:
  injects top-k memories as **pointers only** (title + ≤120-char summary +
  path), hard-capped at `PB_RECALL_MAX_CHARS` (default 2000).

Recall is therefore already bloat-proof by design. The remaining token waste
is elsewhere: in the **fixed context the framework itself imposes on every
session** — which this repo controls 100%.

## 2. What Prompt Base Can and Cannot Control

| Layer | Controlled by | Can we optimize it here? |
|-------|---------------|--------------------------|
| Rules loaded every session (`CLAUDE.md`) | This repo | **Yes — highest leverage** |
| Session-start mandatory reads (`ARCHITECTURE.md`, `registry.min.json`) | This repo (TIER 0 rule) | **Yes** |
| Skill docs loaded on trigger (`SKILL.md`) | This repo | **Yes** (size budgets) |
| Agent output verbosity | Partially (rules/skills) | Somewhat (advisory) |
| Tool output format (`Read`, `Grep`, …) | Host harness | **No** — no interception point |
| Harness context compaction | Host harness | No (PreCompact hook only *adds* archival) |

## 3. Evaluated and Rejected (do not re-propose without new evidence)

| Idea | Why rejected |
|------|--------------|
| **TOON / reformatting tool outputs** | No interception point exists: hooks can block tools or add context, but cannot rewrite a tool's output before the model sees it. Premise was also wrong — harness tool outputs are mostly plain text, not JSON arrays. |
| **LLMLingua-2 compression of archives** | Violates the engine's core design decision that the source of truth is *human-readable, PR-reviewable markdown* (see `proposal.md`, "philosophy bridge"). Also drags torch/transformers into a venv that is deliberately minimal. The claimed benefit ("pack more ADRs into the recall budget") misreads the design — recall injects pointers, never bodies. |
| **AST-aware `Read` replacement** | The built-in `Read` tool cannot be modified. An opt-in `tools/ast_skeleton.py` (next to the existing `tools/code_graph.py`) is feasible, but adoption would be discipline-based — the exact failure mode the memory engine was built to eliminate. Parked as low priority. |

## 4. Recommended Enhancements (prioritized by ROI)

### P1 — Eliminate the `CLAUDE.md` double-load (high impact, trivial effort) — OPEN

Verified 2026-07-14: `diff CLAUDE.md ~/.claude/CLAUDE.md` returns no
differences. When working inside this repo, **two identical copies** of the
framework rules are loaded into context every request: the installed
`~/.claude/CLAUDE.md` and the repo's own checked-in `CLAUDE.md`. That is the
single largest recurring token cost the project controls, and no
micro-optimization can offset paying it twice.

**Action:** replace the repo's `CLAUDE.md` with a thin pointer (a few lines:
"this repo is the source of the framework; the active rules are the installed
`~/.claude/CLAUDE.md`"). The full content remains authored here and shipped by
`make install-claude`.

### P2 — Replace mandatory session-start full reads with lazy loading — ALREADY IMPLEMENTED

**Correction:** this was already done, in the same commit (`b58e467`) that
introduced this report. `core/rules.md:46` and `CLAUDE.md`'s "System Map Read"
section both read: *"Grep `registry.min.json` by trigger keyword when
selecting a skill. Read `ARCHITECTURE.md` by section only when needed for the
task. Do not read the entire files upfront."* This is the lazy form and no
longer contradicts `core/memory_rules.md` rule 5. No further action needed —
kept here only so it isn't re-proposed.

### P3 — Enforce a SKILL.md size budget via `checklist.py` — ALREADY IMPLEMENTED

**Correction:** also already done in commit `b58e467`. `scripts/checklist.py`
lines 112-114 already warn when a `SKILL.md` exceeds 175 lines, recommending
the move to a `references/` subdirectory — the enforcement mechanism this
item asked for already exists.

The supporting claim was also wrong: `project-memory/SKILL.md` is **140
lines**, not "~380" — it doesn't even approach the existing 175-line
threshold. No further action needed — kept here only so it isn't re-proposed.

### P4 — Terse mode for autonomous loops (low effort, modest impact) — OPEN

Verified 2026-07-14: `behavioral-modes/SKILL.md` has no dedicated
terse/autonomous mode — only a mention of dropping "concise or terse persona
requirements" for safety overrides. Add a terse/minimal-output mode for
sub-agent loops with no user interaction: no conversational filler,
single-sentence status only. `core/memory_rules.md` rule 7 ("No Meta-Chat")
already covers half of this — this is an incremental extension, not a new
pillar. Impact is bounded because output style is also governed by the host
harness.

## 5. Conclusion

The original draft looked for savings at a layer this project cannot touch
(harness tool traffic) while missing the waste in the layer it fully controls
(its own always-on context). The memory engine already solved the macro
problem, and the 2026-07-13 revision already fixed the lazy-loading rule (P2)
and added the size-budget check (P3) in the same commit — both are done. The
one remaining high-ROI item is **P1** (drop the duplicate `CLAUDE.md`), plus
the low-effort **P4** (terse autonomous-loop mode). Both are single-file
markdown edits, measurable by counting tokens before and after, with zero
runtime risk.
