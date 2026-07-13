"""Shared library for the automated context memory engine.

Schema, project-root resolution, embedding, and query logic used by the
PreCompact (memory_compact.py) and UserPromptSubmit (memory_recall.py) hooks.
Never raises on missing optional dependencies (sqlite-vec, fastembed) -
callers get a `degraded` flag and fall back to FTS5 keyword search instead.
"""

import hashlib
import json
import os
import re
import sqlite3
import struct
import time
from datetime import datetime, timezone
from pathlib import Path

EMBED_DIM = 384
DEFAULT_EMBED_MODEL = "bge-small-en-v1.5"
SCHEMA_VERSION = "1"

ROOT_MARKERS = ("CLAUDE.md", "GEMINI.md", "ARCHITECTURE.md")

# Claude Code hook_event_name values this engine knows how to normalize.
CLAUDE_EVENTS = ("PreCompact", "SessionStart", "UserPromptSubmit")

SECRET_PATTERNS = [
    re.compile(r"sk-[A-Za-z0-9]{20,}"),                     # OpenAI/Anthropic-style keys
    re.compile(r"AKIA[0-9A-Z]{16}"),                         # AWS access key id
    re.compile(r"gh[pousr]_[A-Za-z0-9]{20,}"),               # GitHub tokens
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),       # PEM private keys
    re.compile(r"(?i)\b(api[_-]?key|secret|token|password)\b\s*[:=]\s*['\"]?[A-Za-z0-9_\-/+=]{12,}"),
]

_VEC_AVAILABLE = None  # tri-state cache: None untested, True/False result
_EMBED_BACKEND = None  # cached fastembed model, or False if unavailable
_COLD_LOAD_MS = None  # wall-clock ms of the first fastembed import+construct in this process


# ---- secret scrubbing ----

def contains_secret(text: str) -> bool:
    return any(pattern.search(text) for pattern in SECRET_PATTERNS)


# ---- path resolution ----

def resolve_project_root(cwd: str) -> str:
    """PB_MEMORY_ROOT override -> upward walk for .git -> upward walk for a
    root marker file -> logged fallback to cwd."""
    override = os.environ.get("PB_MEMORY_ROOT")
    if override:
        return str(Path(override).resolve())

    current = Path(cwd).resolve()
    candidates = [current, *current.parents]

    for candidate in candidates:
        if (candidate / ".git").exists():
            return str(candidate)

    for candidate in candidates:
        if any((candidate / marker).exists() for marker in ROOT_MARKERS):
            return str(candidate)

    root = str(current)
    _log(root, f"resolve_project_root: no .git or root marker found above {cwd}, falling back to cwd")
    return root


def memory_db_path(root: str) -> str:
    return str(Path(root) / ".ai-memory" / "memory.db")


def adr_dir(root: str) -> str:
    return str(Path(root) / "docs" / "ai" / "adr")


def archive_dir(root: str) -> str:
    return str(Path(root) / "docs" / "ai" / "archive")


# ---- host adapter (REQ-009) ----

def _empty_payload():
    return {
        "host": "unknown",
        "event": None,
        "cwd": None,
        "session_id": None,
        "transcript_path": None,
        "prompt": None,
    }


def normalize_payload(raw: dict) -> dict:
    """Normalize host-specific hook stdin JSON into the internal payload
    {host, event, cwd, session_id, transcript_path, prompt}. Missing/unknown
    fields become None; never raises. Claude Code is the only verified host
    today - Gemini's schema is unverified (see design.md, Task 3.4), so any
    payload that doesn't match a known Claude Code event maps to host=unknown
    with event=None, which callers treat as a no-op."""
    if not isinstance(raw, dict):
        return _empty_payload()

    event = raw.get("hook_event_name")
    host = "claude" if event in CLAUDE_EVENTS else "unknown"
    if host != "claude":
        event = None

    return {
        "host": host,
        "event": event,
        "cwd": raw.get("cwd"),
        "session_id": raw.get("session_id"),
        "transcript_path": raw.get("transcript_path"),
        "prompt": raw.get("prompt"),
    }


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _log(root: str, message: str) -> None:
    try:
        mem_dir = Path(root) / ".ai-memory"
        mem_dir.mkdir(parents=True, exist_ok=True)
        with open(mem_dir / "engine.log", "a", encoding="utf-8") as f:
            f.write(f"{_now_iso()} {message}\n")
    except OSError:
        pass  # logging must never raise


# ---- sqlite-vec extension loading ----

def _load_vec_extension(conn: sqlite3.Connection) -> bool:
    global _VEC_AVAILABLE
    if _VEC_AVAILABLE is False:
        return False
    try:
        import sqlite_vec  # type: ignore

        conn.enable_load_extension(True)
        sqlite_vec.load(conn)
        conn.enable_load_extension(False)
        _VEC_AVAILABLE = True
        return True
    except Exception:
        _VEC_AVAILABLE = False
        return False


def _serialize_vec(vector) -> bytes:
    try:
        import sqlite_vec  # type: ignore

        return sqlite_vec.serialize_float32(vector)
    except Exception:
        return struct.pack(f"{len(vector)}f", *vector)


# ---- schema ----

def connect(root: str) -> sqlite3.Connection:
    mem_dir = Path(root) / ".ai-memory"
    mem_dir.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(mem_dir / "memory.db"))
    conn.row_factory = sqlite3.Row
    _load_vec_extension(conn)
    return conn


def init_db(root: str) -> sqlite3.Connection:
    conn = connect(root)
    conn.execute("CREATE TABLE IF NOT EXISTS meta (key TEXT PRIMARY KEY, value TEXT)")
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS memory (
            id          INTEGER PRIMARY KEY,
            kind        TEXT NOT NULL,
            title       TEXT,
            body        TEXT NOT NULL,
            source_path TEXT,
            content_sha TEXT NOT NULL UNIQUE,
            created_at  TEXT NOT NULL
        )
        """
    )
    conn.execute(
        """
        CREATE VIRTUAL TABLE IF NOT EXISTS memory_fts USING fts5(
            body, content='memory', content_rowid='id'
        )
        """
    )
    if _load_vec_extension(conn):
        conn.execute(
            f"CREATE VIRTUAL TABLE IF NOT EXISTS memory_vec USING vec0(embedding FLOAT[{EMBED_DIM}])"
        )
    _set_meta_if_absent(conn, "schema", SCHEMA_VERSION)
    conn.commit()
    return conn


# ---- meta table helpers ----

def get_meta(conn: sqlite3.Connection, key: str, default=None):
    row = conn.execute("SELECT value FROM meta WHERE key = ?", (key,)).fetchone()
    return row["value"] if row is not None else default


def set_meta(conn: sqlite3.Connection, key: str, value) -> None:
    conn.execute(
        "INSERT INTO meta (key, value) VALUES (?, ?) "
        "ON CONFLICT(key) DO UPDATE SET value = excluded.value",
        (key, str(value)),
    )
    conn.commit()


def _set_meta_if_absent(conn: sqlite3.Connection, key: str, value) -> None:
    if get_meta(conn, key) is None:
        conn.execute("INSERT INTO meta (key, value) VALUES (?, ?)", (key, str(value)))


def get_embed_load_ms(conn: sqlite3.Connection):
    value = get_meta(conn, "embed_load_ms")
    return float(value) if value is not None else None


def set_embed_load_ms(conn: sqlite3.Connection, ms: float) -> None:
    set_meta(conn, "embed_load_ms", ms)


# ---- embedding ----

def _get_fastembed_model():
    """Construct (and cache) the local fastembed backend. Only the first
    call in a process pays the import+model-load cost, which is timed into
    _COLD_LOAD_MS so callers (upsert(), memory_bench.py) can persist it as
    meta.embed_load_ms for the recall latency budget (REQ-008)."""
    global _EMBED_BACKEND, _COLD_LOAD_MS
    if _EMBED_BACKEND is False:
        return None
    if _EMBED_BACKEND is not None:
        return _EMBED_BACKEND
    start = time.monotonic()
    try:
        from fastembed import TextEmbedding  # type: ignore

        _EMBED_BACKEND = TextEmbedding(model_name="BAAI/bge-small-en-v1.5")
        _COLD_LOAD_MS = (time.monotonic() - start) * 1000
        return _EMBED_BACKEND
    except Exception:
        _EMBED_BACKEND = False
        return None


def _embed_via_api(text: str, api: str, key: str, root: str):
    try:
        import urllib.request

        payload = json.dumps({"input": text}).encode("utf-8")
        req = urllib.request.Request(
            api,
            data=payload,
            headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        return [float(v) for v in data["embedding"]]
    except Exception as exc:
        _log(root, f"embed: API embedding failed: {exc}")
        return None


def embed(text: str, root: str = "."):
    """Return (vector, model_name, dim), or (None, None, None) if no
    embedding backend is available. Never raises."""
    api = os.environ.get("PB_EMBED_API")
    key = os.environ.get("PB_EMBED_KEY")
    if api and key:
        vector = _embed_via_api(text, api, key, root)
        if vector is not None:
            return vector, f"api:{api}", len(vector)
        return None, None, None

    model = _get_fastembed_model()
    if model is None:
        return None, None, None
    try:
        vector = [float(v) for v in next(iter(model.embed([text])))]
        return vector, DEFAULT_EMBED_MODEL, len(vector)
    except Exception as exc:
        _log(root, f"embed: fastembed inference failed: {exc}")
        return None, None, None


# ---- content hashing ----

def content_sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


# ---- upsert / drop ----

def upsert(conn: sqlite3.Connection, root: str, kind: str, title, body: str, source_path=None):
    """Insert (kind, title, body, source_path), deduped on content_sha.
    Returns the row id, or None if the chunk was skipped (secret match)."""
    if contains_secret(body):
        _log(root, f"upsert: skipped chunk matching secret pattern (kind={kind}, source={source_path})")
        return None

    sha = content_sha(body)
    existing = conn.execute("SELECT id FROM memory WHERE content_sha = ?", (sha,)).fetchone()
    if existing is not None:
        return existing["id"]

    vector, model, dim = embed(body, root=root)
    if vector is not None:
        # PreCompact (the only caller of upsert()) is non-blocking and may
        # always pay the cold-load cost - piggyback on that to calibrate
        # this project's recall latency budget (REQ-008), so a project
        # never needs a separate manual `make memory-bench` run before
        # recall's budget check has something real to compare against.
        if _COLD_LOAD_MS is not None and get_embed_load_ms(conn) is None:
            set_embed_load_ms(conn, _COLD_LOAD_MS)

        recorded_model = get_meta(conn, "embed_model")
        recorded_dim = get_meta(conn, "embed_dim")
        if recorded_model is None:
            set_meta(conn, "embed_model", model)
            set_meta(conn, "embed_dim", dim)
        elif recorded_model != model or int(recorded_dim) != dim:
            _log(
                root,
                f"upsert: embedding model drift ({recorded_model}/{recorded_dim} recorded vs "
                f"{model}/{dim} current); skipping vector index for this row, run `make memory-rebuild`",
            )
            vector = None

    cur = conn.execute(
        "INSERT INTO memory (kind, title, body, source_path, content_sha, created_at) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        (kind, title, body, source_path, sha, _now_iso()),
    )
    row_id = cur.lastrowid
    conn.execute("INSERT INTO memory_fts (rowid, body) VALUES (?, ?)", (row_id, body))
    if vector is not None and _load_vec_extension(conn):
        try:
            conn.execute(
                "INSERT INTO memory_vec (rowid, embedding) VALUES (?, ?)",
                (row_id, _serialize_vec(vector)),
            )
        except Exception as exc:
            _log(root, f"upsert: failed to write vector row {row_id}: {exc}")
    conn.commit()
    return row_id


def drop_row(conn: sqlite3.Connection, root: str, row_id: int) -> None:
    """Remove a row from memory, memory_vec, and memory_fts atomically."""
    try:
        conn.execute("DELETE FROM memory WHERE id = ?", (row_id,))
        conn.execute("DELETE FROM memory_fts WHERE rowid = ?", (row_id,))
        if _load_vec_extension(conn):
            conn.execute("DELETE FROM memory_vec WHERE rowid = ?", (row_id,))
        conn.commit()
    except Exception as exc:
        conn.rollback()
        _log(root, f"drop_row: failed to remove row {row_id}: {exc}")


# ---- query ----

def _fts_query(conn: sqlite3.Connection, text: str, k: int):
    terms = re.findall(r"[A-Za-z0-9_]+", text)
    if not terms:
        return []
    match_expr = " OR ".join(terms)
    rows = conn.execute(
        """
        SELECT m.id, m.kind, m.title, m.body, m.source_path, bm25(memory_fts) AS score
        FROM memory_fts
        JOIN memory m ON m.id = memory_fts.rowid
        WHERE memory_fts MATCH ?
        ORDER BY score
        LIMIT ?
        """,
        (match_expr, k),
    ).fetchall()
    return [dict(r) for r in rows]


def query(conn: sqlite3.Connection, root: str, text: str, k: int = 5, budget_ms=None):
    """Cosine top-k via sqlite-vec when the embedding backend + index are
    available and match the recorded meta; FTS5 keyword search otherwise.
    Returns {"degraded": bool, "reason": str | None, "hits": [...]}.

    When `budget_ms` is given, the recorded `meta.embed_load_ms` is checked
    FIRST: if it's missing or >= budget_ms, this goes straight to FTS5 and
    never calls embed() - so a caller on a latency budget (recall) never
    pays for a model import/load it isn't allowed to afford. Pass
    budget_ms=None (the default) for unrestricted callers like PreCompact."""
    degraded = True
    reason = None
    hits = []

    within_budget = True
    if budget_ms is not None:
        load_ms = get_embed_load_ms(conn)
        if load_ms is None:
            within_budget = False
            reason = "no embed_load_ms recorded; run `make memory-setup`/`make memory-bench`"
        elif load_ms >= budget_ms:
            within_budget = False
            reason = f"embed_load_ms {load_ms} >= budget {budget_ms}"

    if within_budget and _load_vec_extension(conn):
        recorded_model = get_meta(conn, "embed_model")
        recorded_dim = get_meta(conn, "embed_dim")
        vector, model, dim = embed(text, root=root)
        if vector is None:
            reason = "embedding backend unavailable"
        elif recorded_model and (recorded_model != model or int(recorded_dim) != dim):
            reason = (
                f"embedding model drift ({recorded_model}/{recorded_dim} recorded vs "
                f"{model}/{dim} current); run `make memory-rebuild`"
            )
            _log(root, f"query: refused vector search due to drift: {reason}")
        else:
            rows = conn.execute(
                """
                SELECT m.id, m.kind, m.title, m.body, m.source_path, v.distance
                FROM memory_vec v
                JOIN memory m ON m.id = v.rowid
                WHERE v.embedding MATCH ? AND k = ?
                ORDER BY v.distance
                """,
                (_serialize_vec(vector), k),
            ).fetchall()
            hits = [dict(r) for r in rows]
            degraded = False
    elif within_budget:
        reason = "sqlite-vec unavailable"

    if degraded:
        hits = _fts_query(conn, text, k)

    return {"degraded": degraded, "reason": reason, "hits": hits}
