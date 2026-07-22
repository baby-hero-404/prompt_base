---
name: python-patterns
description: "Use when writing Python code, selecting Python frameworks, or implementing async patterns."
allowed-tools: Read, Write, Edit, Glob, Grep
references: [frameworks.md, async-and-types.md, structure-and-quality.md]
---

# Python Patterns

> **Learn to THINK, not memorize patterns.** Decision-making for YOUR specific context.

---

## 1. Context Analysis (ALWAYS FIRST)

- **Input Bound?** → Go Async (FastAPI).
- **Complexity Bound?** → Go Batteries-Included (Django).
- **Scale?** → Layered vs Feature-based structure.

---

## 2. Decision Support Modules

### Framework & Performance
Refer to **`references/frameworks.md`**.
- Selection tree for FastAPI, Django, Flask.
- Background task selection (Celery vs ARQ).

### Concurrency & Typing
Refer to **`references/async-and-types.md`**.
- Async library mapping (`httpx`, `asyncpg`).
- Strict type hint strategy and Pydantic validation.

### Structure & Quality
Refer to **`references/structure-and-quality.md`**.
- Project layout patterns.
- Modern tooling (`Ruff`, `Pyright`, `uv`).
- Testing strategies.

---

## 🛡️ CORE RULES

1. **NO MIXING**: Avoid mixing sync/async libraries unless using threadpools properly.
2. **TYPE EVERYTHING**: Mandatory type hints for all function parameters and returns.
3. **LOGIC SEPARATION**: Routes/Views should be thin; business logic stays in Services.
4. **SECURE SECRETS**: Never commit `.env` values or hardcode keys.

---

## ✅ VERIFICATION CHECKLIST

- [ ] Framework preference confirmed with user?
- [ ] Async/Sync choice justified?
- [ ] Pydantic schemas defined for all I/O?
- [ ] `Ruff` and `Pyright` audit passed?
- [ ] Unit/Integration tests planned?

---

> **Note:** Python development in 2025 favors speed (uv), correctness (Pyright), and async performance (FastAPI/Hono-Python). Apply these principles over legacy patterns.
