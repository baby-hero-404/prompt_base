# Report: Token Reduction Opportunities for Prompt Base

> Revised 2026-07-13. The original draft of this report borrowed ideas from the
> "Awesome LLM Token Reduction" list without checking them against this
> project's architecture; several of its premises were wrong. This revision
> keeps only what applies to `prompt_base` as it actually exists, and records
> why the rejected ideas were rejected so future sessions don't re-propose them.

## 1. Overview and Current State

`prompt_base` is a **configuration framework** — rules (`CLAUDE.md`/`GEMINI.md`),
skills, a registry, and hook scripts — installed into `~/.claude` / `~/.gemini`.
It is *not* a runtime: the tools the agent calls (`Read`, `Grep`, Bash, etc.)
belong to the host harness, and their outputs enter context directly. Nothing
in this repo sits between the model and its tools.

The **Automated Context Memory Engine**
(`docs/openspecs/context-memory-engine-2026/`) already handles the macro
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

### P1 — Eliminate the `CLAUDE.md` double-load (high impact, trivial effort)

When working inside this repo, **two identical copies** of the framework rules
are loaded into context every request: the installed `~/.claude/CLAUDE.md` and
the repo's own checked-in `CLAUDE.md`. That is the single largest recurring
token cost the project controls, and no micro-optimization can offset paying
it twice.

**Action:** replace the repo's `CLAUDE.md` with a thin pointer (a few lines:
"this repo is the source of the framework; the active rules are the installed
`~/.claude/CLAUDE.md`"). The full content remains authored here and shipped by
`make install-claude`.

### P2 — Replace mandatory session-start full reads with lazy loading

`CLAUDE.md` TIER 0 currently mandates: *"Read `ARCHITECTURE.md` and
`registry.min.json` at session start"* — a large fixed cost paid even for
trivial questions. It also directly contradicts `core/memory_rules.md` rule 5,
which forbids reading the full registry and prescribes `grep` lookups instead.
The costlier rule wins because it sits at TIER 0.

**Action:** rewrite the TIER 0 rule to the lazy form (grep the registry by
trigger keyword when selecting a skill; read `ARCHITECTURE.md` by section when
needed). This applies the framework's own Progressive Disclosure principle to
the framework itself.

### P3 — Enforce a SKILL.md size budget via `checklist.py` (enforced, not advisory)

Skills load whole on trigger; some have grown large (`project-memory` is
~380 lines). The project already has an enforcement mechanism — `make audit` /
`scripts/checklist.py` — so a size check fits the established pattern:
warn when a `SKILL.md` exceeds a threshold (e.g. 150 lines) and recommend
moving detail into a `references/` subdirectory read on demand.

### P4 — Terse mode for autonomous loops (low effort, modest impact)

Add a terse/minimal-output mode to `behavioral-modes/SKILL.md` for sub-agent
loops with no user interaction: no conversational filler, single-sentence
status only. Note `core/memory_rules.md` rule 7 ("No Meta-Chat") already
covers half of this — this is an incremental extension, not a new pillar.
Impact is bounded because output style is also governed by the host harness.

## 5. Conclusion

The original draft looked for savings at a layer this project cannot touch
(harness tool traffic) while missing the waste in the layer it fully controls
(its own always-on context). The memory engine already solved the macro
problem; the remaining wins are P1 and P2 — both are single-file markdown
edits, measurable by counting tokens before and after, with zero runtime risk.
