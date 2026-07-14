---
name: explore-codebase
description: "Use when exploring or reverse-engineering an unfamiliar codebase to extract what is worth learning: architecture, design patterns, elegant techniques, hidden gems, reading order, anti-patterns, and a learning roadmap. Triggers on: explore codebase, discover project, learn from codebase, analyze repo for learning, what can I learn, reading guide, project discovery."
allowed-tools: Read, Write, Edit, Glob, Grep, Bash
---

# Project Discovery & Learning

> "Don't just understand what the code does — discover why it was designed that way, what trade-offs were made, and what a senior engineer would notice."

## When to Use
- The user provides a repository/path and wants to **learn from it**, not modify it.
- Requests like "what can I learn from this project", "analyze this repo for learning", "give me a reading guide", "discover this project".
- Onboarding onto an unfamiliar codebase where design decisions matter more than a feature summary.

## 1. Core Principles

| Principle | Why |
|-----------|-----|
| **Analyze like a Senior Architect** | The output is design decisions, trade-offs, and principles — never a plain feature summary. |
| **Evidence over impression** | Every claim cites a real `file:line` path discovered via Glob/Grep/Read. Never invent paths. |
| **Depth on the elegant 10%** | Skim broadly, then stop and dissect the few genuinely clever implementations in detail. |
| **Learning-oriented output** | Everything converges into ranked concepts, a reading order, and a roadmap the user can follow. |
| **Read-only mission** | Discovery never modifies the target project. The only artifact written is the report. |

## 2. The 10 Analysis Perspectives

Cover ALL of these — each grounded in concrete files:

1. **Architecture** — overall style, folder structure, layer separation, dependency direction, and *why this architecture was chosen*. Explicitly identify **"The Glue"**: how dependency injection, event buses, middleware, or plugin registries wire the isolated modules together — juniors understand components but miss the wiring.
2. **Design Patterns** — patterns used, why they fit here, pros/cons of each.
3. **Code Quality** — coding style, naming, readability, maintainability.
4. **Interesting Techniques** — elegant or uncommon implementations: what problem they solve, why the implementation is clever, possible alternatives.
5. **Engineering Practices** — testing, logging, configuration, dependency injection, error handling, validation, performance optimization, security.
6. **Hidden Gems** — specific files containing particularly valuable code, and why.
7. **What You Can Learn** — top 10 concepts ranked, each with: concept, file path, why useful, difficulty (⭐–⭐⭐⭐⭐⭐), suggested learning order.
8. **Reading Guide** — optimal file-reading order from beginner to advanced (Day 1 / Day 2 / Day 3 …).
9. **Anti-Patterns** — anything that could be improved, framed as lessons.
10. **Overall Evaluation** — score /10 on Architecture, Maintainability, Scalability, Clean Code, Learning Value — plus a final **Learning Roadmap**.

## 3. Workflow (Survey → Dissect → Teach)

### Phase 1: Survey (graph-first, not linear)
- Map the repo: `Glob` the tree, read manifests (`package.json`, `pyproject.toml`, `go.mod`, `Makefile`, CI config), find entry points.
- Trace imports/dependency direction from entry points (pair with `code-graph-analysis` for large repos).
- Identify central hubs (high fan-in/fan-out) — these are candidate hidden gems.
- **Large monorepos:** ask the user to specify a sub-package or core domain to focus on before deep-diving, to avoid context window exhaustion. Survey the top-level map first, then scope.

### Phase 2: Dissect (the senior lens)
Whenever you find a piece of code that is particularly elegant, **stop and explain**:
- Why it is elegant, and what problem it solves.
- What alternatives exist, and what would happen if another approach was chosen.
- What trade-offs the author accepted.
- Which engineering principles it demonstrates.
- What senior engineers usually notice here — and what juniors often miss.
- Which files deserve repeated reading.

**Historical context (optional):** when an implementation looks strange or unusually clever, use `git log --follow <file>` or `git blame` on it — the *why* behind a trade-off is often buried in commit messages rather than the code itself.

### Phase 3: Teach (produce the report)
- **Prefer the Artifacts system when available** — it renders rich markdown (Mermaid diagrams, tables) and keeps the target project untouched. Otherwise write to `docs/discovery/DISCOVERY-<project-name>.md`, or to the scratchpad / inline for small projects or when the target repo shouldn't gain files.
- Use the template below. For large projects, expand "Top 10" to "Top 20 Things Worth Learning".

## 4. Report Template

```markdown
# Project Discovery Report — <name>

## High Level
<what it is, stack, size, maturity — 5 lines max>

## Architecture
<style, layers, dependency direction, WHY it was chosen; mermaid diagram>

## Design Patterns & Code Quality
<patterns with file refs, pros/cons; style/naming/maintainability verdict>

## Interesting Techniques & Engineering Practices
<elegant implementations dissected per Phase 2; testing/logging/config/DI/errors/security findings>

## Most Valuable Files (Hidden Gems)
1. `src/core/...` — Why: ...

## Top 10 Things Worth Learning
| # | Concept | File | Why Useful | Difficulty | Order |
|---|---------|------|-----------|------------|-------|

## Reading Order
**Day 1:** ... **Day 2:** ... **Day 3:** ...

## Anti-Patterns / Improvements
<framed as lessons>

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
| Modify or "fix" the target project during discovery. | Stay read-only; improvements go in the Anti-Patterns section. |
| Skip scoring or the roadmap when the project is small. | Always deliver all 10 perspectives — scale depth, not coverage. |
