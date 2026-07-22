# Python Project Structure & Quality Control

## 1. Project Organization

| Scale | Recommended Layout |
|-------|--------------------|
| **Small / Script** | Flat: `main.py`, `utils.py`, `requirements.txt`. |
| **Medium API** | Layered: `app/main.py`, `models/`, `routes/`, `services/`, `schemas/`. |
| **Large App** | Domain/Feature: `src/myapp/core/`, `features/user/`, `features/product/`. |

---

## 2. Essential Tooling (2025)

| Tool | Purpose |
|------|---------|
| **Ruff** | Linter & Formatter (One tool to replace Black/Isort/Flake8). |
| **Pyright** | Fast, modern Static Type Checking (Preferred over MyPy). |
| **UV** | Extremely fast package manager. |
| **Pytest** | Standard testing engine. |

### Run Quality Audit
```bash
ruff check . --fix
pyright .
pytest
```

---

## 3. Testing Principles

- **Unit**: Test logic in isolation.
- **Integration**: Use `TestClient` (FastAPI) or `AsyncClient` (HTTPX) to test routes.
- **Async Tests**: Use `@pytest.mark.asyncio`.

---

## 4. Error Handling & Anti-Patterns

- **Custom Exceptions**: Define domain-specific exceptions.
- **Consistent Response**: Return programmatic error codes + human messages.
- **No Stack Traces**: Never leak traces to clients in production.

### Common Anti-Patterns (AVOID)
- ❌ Hardcoding secrets (use `.env`).
- ❌ Skipping type hints on public functions.
- ❌ Putting business logic directly in views/routes.
- ❌ Mixing sync/async without careful threadpool handling.
