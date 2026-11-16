---
name: explore-codebase
description: "Use to reverse-engineer and learn patterns from an unfamiliar codebase. Triggers on: explore codebase, discover project, learn from codebase, reading guide."
allowed-tools: Read, Write, Edit, Glob, Grep, Bash
---

# Project Discovery & Learning

> "Don't just understand what the code does — discover why it was designed that way, what trade-offs were made, and what a senior engineer would notice."

## When to Use
- The user provides a repository/path and wants to **learn from it**, not modify it.
- Requests like "what can I learn from this project", "analyze this repo for learning", "give me a reading guide", "discover this project".
- **Primary use case:** Explore an external codebase to discover architectures, patterns, and implementation techniques that can be **adapted and applied to the user's current project**, with concrete recommendations rather than generic observations.
- Onboarding onto an unfamiliar codebase where design decisions matter more than a feature summary.

## 1. Core Principles

| Principle | Why |
|-----------|-----|
| **Analyze like a Senior Architect** | The output is design decisions, trade-offs, and principles — never a plain feature summary. |
| **Evidence over impression** | Every claim cites a real `file:line` path discovered via Glob/Grep/Read. Never invent paths. |
| **Calibrated confidence** | Label major findings **High / Medium / Low** confidence based on evidence strength; never overstate what a partial read supports. |
| **Depth on the elegant 10%** | Skim broadly, then stop and dissect the few genuinely clever implementations in detail. |
| **Learning-oriented output** | Everything converges into ranked concepts, a reading order, and a roadmap the user can follow. |
| **Transfer-oriented output** | The most valuable deliverable is the **Applied Takeaways** section: each idea mapped onto the user's current project with a concrete implementation sketch (which table, which module, which library) — not generic advice. |
| **Read-only mission** | Discovery never modifies the target project. The only artifact written is the report. |
| **Progressive disclosure** | Always explain a concept in plain, non-technical language first — what it is and why it matters — before naming files, functions, or implementation details. A reader unfamiliar with the project must be able to follow the report's opening before hitting any jargon. |

## 2. The 9 Analysis Perspectives

Cover all of these in full-report mode — each grounded in concrete files:

1. **Architecture** — *scope: system structure only — layers, folder structure, dependency direction* — and *why it was chosen*. Explicitly identify **"The Glue"**: how dependency injection, event buses, middleware, or plugin registries wire the isolated modules together — juniors understand components but miss the wiring. Reconstruct the **implicit ADRs** (Decision / Evidence / Benefits / Trade-offs) and, when git history helps, the **architecture evolution**: original approach → significant refactors → current approach, with likely reasons.
2. **Patterns & Engineering Gems** — reusable design patterns (why they fit, pros/cons), elegant or uncommon techniques dissected per Phase 2 (problem → why common implementations are weaker → why this one is elegant → trade-offs → reusable lesson), and specific files containing particularly valuable code, with file refs and supporting files.
3. **Code Quality** — coding style, naming, readability, maintainability.
4. **Engineering Practices** — *scope: the delivery machinery* — testing, CI/CD, logging, observability, configuration, error handling, validation, security, deployment.
5. **What You Can Learn** — top 10 concepts ranked, each with: concept, file path, why useful, difficulty (⭐–⭐⭐⭐⭐⭐), suggested learning order.
6. **Reading Guide** — a level-based path, not a calendar: **L0** Build & Run → **L1** Entry Points → **L2** Core Abstractions → **L3** Architecture Glue → **L4** Engineering Gems → **L5** Reimplement a Key Component.
7. **Anti-Patterns & What NOT to Copy** — flaws framed as lessons, *plus* sound decisions that are context-bound (legacy constraints, unusual scale, compatibility) — state when each should **not** be adopted elsewhere.
8. **Overall Evaluation** — score /10 on Architecture, Maintainability, Scalability, Clean Code, Learning Value — plus **Questions Worth Asking** (open architectural questions the code raises, e.g. *why Redis instead of PostgreSQL? why events instead of polling?*) and a final **Learning Roadmap**.
9. **Applied Takeaways** — the transfer step. For each promising idea: *(a)* what the mechanism is, *(b)* **how to apply it to the user's current project**, named explicitly and mapped to its real stack (e.g. "add an `agent_procedural_memory` table in the existing PostgreSQL schema; combine full-text search with `pgvector` via RRF"), *(c)* **impact, implementation effort, risk, and estimated dev time** — then **rank the list by adoption priority** so the user knows what to adopt first. If the current/destination project is unknown, **ask the user which project the learnings should be applied to** before writing this section.

## 3. Workflow (Survey → Dissect → Teach)

### Phase 1: Survey (graph-first, not linear)
- Map the repo: `Glob` the tree, read manifests (`package.json`, `pyproject.toml`, `go.mod`, `Makefile`, CI config), find entry points.
- Trace imports/dependency direction from entry points (pair with `code-graph-analysis` for large repos).
- **Rank before deep-diving:** score components by fan-in/fan-out, complexity, abstraction level, and business criticality; spend most analysis time on the top 10–20% — never treat all modules equally. High-scoring hubs are the candidate engineering gems.
- **Large monorepos:** ask the user to specify a sub-package or core domain to focus on before deep-diving, to avoid context window exhaustion. Survey the top-level map first, then scope.
- **Destination context:** identify the user's **current project** (stack, database, architecture) — usually the working directory the skill was invoked from — so Applied Takeaways can name real tables/modules/libraries instead of generic advice. A quick manifest + `ARCHITECTURE.md` read is enough; do not deep-dive the destination.

### Phase 2: Dissect (the senior lens)
Whenever you find a piece of code that is particularly elegant, **stop and explain**:
- What problem it solves, and why it is elegant.
- What alternatives exist, why the common implementations are weaker, and what would happen if another approach was chosen.
- What trade-offs the author accepted.
- Which engineering principles it demonstrates — the **reusable lesson** to carry to other projects.
- What senior engineers usually notice here — and what juniors often miss.
- Which files deserve repeated reading.

**Architecture evolution (git):** when an implementation looks strange or unusually clever — or the architecture clearly shifted at some point — use `git log --follow <file>` / `git blame` to reconstruct: original approach → significant refactors → current approach, and the likely reasons. The *why* behind a trade-off is often buried in commit messages rather than the code itself.

### Phase 3: Teach (produce the report)
- **Prefer the Artifacts system when available** — it renders rich markdown (Mermaid diagrams, tables) and keeps the target project untouched. Otherwise write to `docs/discovery/DISCOVERY-<project-name>.md`, or to the scratchpad / inline for small projects or when the target repo shouldn't gain files.
- Use the template below. For large projects, expand "Top 10" to "Top 20 Things Worth Learning".
- **Default mode (digest):** Output five sections: **TL;DR → Best Features → Applied Takeaways for <current project> → Architecture & Key Paths → Main Flow (mermaid)**. Depth of evidence stays the same; only coverage is scoped.
- **Full report mode:** When the user asks for a "full report", "deep analysis", "in-depth", or "complete discovery", cover all 9 perspectives and use the full template below.

## 4. Report Template

```markdown
# Project Discovery Report — <name>

## TL;DR
<Plain, non-technical language. What problem does this project solve, and how, in 2-3 sentences? No jargon, no acronyms, no file paths — a newcomer should understand this before reading anything else.>

## Technical Overview
- **Stack:** <languages, frameworks, key infra>
- **Scale/Maturity:** <size, age, production status>

## Best Features
<3–5 standout capabilities with design analysis and any measured results; file refs>

## Applied Takeaways — for <current project> (ranked by adoption priority)
1. **<Idea>** — What: <mechanism, file ref>. Apply: <concrete change in the current project's real stack — table/module/library>. Impact: <H/M/L> · Effort: <H/M/L> · Risk: <H/M/L> · Est. time: <...>

## Architecture
<style, layers, dependency direction, WHY it was chosen; mermaid diagram; evolution per git history: original → refactors → current, with likely reasons; confidence label on major claims>

### Inferred ADRs
| Decision | Evidence | Benefits | Trade-offs | Confidence |
|---|---|---|---|---|

## Main Flow
<end-to-end runtime flow of the core scenario as a mermaid flowchart, from entry point to output>

## Patterns & Engineering Gems
<reusable patterns with file refs and pros/cons; elegant implementations dissected per Phase 2 (problem → why common is weaker → why this is elegant → trade-offs → reusable lesson); code quality verdict>

## Engineering Practices
<testing, CI/CD, logging, config, error handling, validation, security, deployment findings>

## Top 10 Things Worth Learning
| # | Concept | File | Why Useful | Difficulty | Order |
|---|---------|------|-----------|------------|-------|

## Reading Guide (by level)
**L0 Build & Run:** ... **L1 Entry Points:** ... **L2 Core Abstractions:** ... **L3 Architecture Glue:** ... **L4 Engineering Gems:** ... **L5 Reimplement a Key Component:** ...

## Anti-Patterns & What NOT to Copy
<flaws framed as lessons; context-bound decisions (legacy/scale/compatibility) and when NOT to adopt them>

## Questions Worth Asking
<open architectural questions the code raises, to push understanding deeper>

## Overall Evaluation
| Architecture | Maintainability | Scalability | Clean Code | Learning Value |
|---|---|---|---|---|
| x/10 | x/10 | x/10 | x/10 | x/10 |

## Learning Roadmap
<week-by-week path from reading to reimplementing the core ideas>
```

## 5. Anti-Patterns

| ❌ Don't | ✅ Do |
|----------|-------|
| Produce a feature summary of "what the code does". | Explain *why* it was designed this way and the trade-offs made. |
| Cite patterns or files from memory of similar projects. | Verify every path/claim with Glob/Grep/Read before citing it. |
| Read the whole repo linearly and dump everything. | Survey graph-first, deep-dive only the valuable 10%. |
| Give vague advice ("has good tests"). | Point to concrete files and the specific technique they teach. |
| State every finding with the same certainty. | Label major findings **High / Medium / Low** confidence per the evidence behind them. |
| Modify or "fix" the target project during discovery. | Stay read-only; improvements go in the Anti-Patterns section. |
| Give generic takeaways ("you could use RRF too"). | Map every takeaway onto the current project's real stack: name the table, module, or library to change. |
| Skip scoring or the roadmap when the project is small. | Deliver all 9 perspectives in full-report mode; digest mode is the default. |
| Open with dense jargon (attestation schemes, gate names, framework-specific terms) before the reader knows what the project is. | Lead every section with a plain-language TL;DR of the concept, then drop into file names and implementation detail. |
