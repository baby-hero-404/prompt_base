# Async Logic & Type Systems In Python

## 1. Async vs Sync Decision

- **Async (`async def`)**: Best for **I/O-bound** operations (APIs, DB queries, HTTP calls).
- **Sync (`def`)**: Best for **CPU-bound** work or legacy libraries.

| Need | Async-Native Library |
|------|---------------------|
| **HTTP Client** | `httpx` |
| **PostgreSQL** | `asyncpg` |
| **Redis** | `redis-py` (async mode) |
| **File I/O** | `aiofiles` |
| **ORM** | `SQLAlchemy 2.0+` (async), `Tortoise` |

---

## 2. Type Hinting Strategy

### Mandatory Typing
- Function parameters and return values.
- Class attributes.
- Public API interfaces.

### Common Patterns
```python
from typing import Optional, Callable

# Optional (handles None)
def find_user(id: int) -> Optional[User]: ...

# Modern Union (Python 3.10+)
def process(data: str | dict) -> None: ...

# Callable
def apply(fn: Callable[[int], str]) -> str: ...
```

---

## 3. Data Validation (Pydantic v2)

Always use Pydantic for:
- API Request/Response models.
- Environment settings.
- Data serialization/deserialization.

**Rule:** Prefer `model_validate()` and `model_dump()` over old v1 methods.
