#!/usr/bin/env python3
"""UserPromptSubmit hook entry point (first prompt of session only).

Claude Code's SessionStart payload carries no goal/prompt, so recall
registers on UserPromptSubmit instead and self-gates to the first prompt of
each session via a sentinel file. Retrieves the top-k most relevant past
memories and prints them as title + one-line summary + source path pointers
only - never full bodies - under a hard character budget, so recall itself
can never re-introduce the token bloat this whole engine exists to prevent.
Never breaks the session: any internal error is logged to
.ai-memory/engine.log and the hook still exits 0 with empty stdout (REQ-004).
"""

import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import memory_engine as me  # noqa: E402

DEFAULT_K = 5
DEFAULT_MAX_CHARS = 2000
DEFAULT_BUDGET_MS = 2000
SENTINEL_NAME = "last_recall_session"


def _sentinel_path(root: str) -> Path:
    return Path(root) / ".ai-memory" / SENTINEL_NAME


def _already_served(root: str, session_id) -> bool:
    if not session_id:
        return False
    try:
        return _sentinel_path(root).read_text(encoding="utf-8").strip() == str(session_id)
    except OSError:
        return False


def _mark_served(root: str, session_id) -> None:
    if not session_id:
        return
    try:
        path = _sentinel_path(root)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(str(session_id), encoding="utf-8")
    except OSError:
        pass


def _filter_existing(conn, root: str, hits, k: int):
    """Existence-check each hit's source_path; a missing file means its
    markdown was deleted, so the row is pruned on the spot (REQ-011) and the
    next-best candidate backfills the slot. Rows with no source_path (raw
    transcript chunks) are exempt from the check."""
    kept = []
    for hit in hits:
        source_path = hit.get("source_path")
        if source_path and not (Path(root) / source_path).exists():
            me.drop_row(conn, root, hit["id"])
            continue
        kept.append(hit)
        if len(kept) >= k:
            break
    return kept


def _summary(body: str, limit: int = 120) -> str:
    text = " ".join((body or "").split())
    if len(text) <= limit:
        return text
    return text[: limit - 1].rstrip() + "…"


def _render_line(hit) -> str:
    title = hit.get("title") or hit.get("kind") or "memory"
    source = hit.get("source_path") or ""
    suffix = f"  ({source})" if source else ""
    return f"• {title} — {_summary(hit.get('body'))}{suffix}"


def _render_block(hits, max_chars: int) -> str:
    """Lines are already best-first; drop from the end (lowest-scoring)
    until the joined block fits the cap."""
    lines = [_render_line(hit) for hit in hits]
    while lines:
        block = "\n".join(lines)
        if len(block) <= max_chars:
            return block
        lines.pop()
    return ""


def recall(root: str, payload: dict) -> str:
    session_id = payload.get("session_id")
    prompt = payload.get("prompt")

    if _already_served(root, session_id):
        return ""

    # Mark served before doing any work: if recall itself fails below, every
    # later prompt in this same (broken) session still gets a clean no-op
    # instead of retrying and re-failing on every keystroke.
    _mark_served(root, session_id)

    if not prompt:
        return ""

    k = int(os.environ.get("PB_RECALL_K", DEFAULT_K))
    max_chars = int(os.environ.get("PB_RECALL_MAX_CHARS", DEFAULT_MAX_CHARS))
    budget_ms = int(os.environ.get("PB_RECALL_BUDGET_MS", DEFAULT_BUDGET_MS))

    conn = me.init_db(root)
    # Over-fetch so ghost rows pruned by _filter_existing still leave k hits.
    result = me.query(conn, root, prompt, k=max(k * 3, k + 5), budget_ms=budget_ms)
    hits = _filter_existing(conn, root, result["hits"], k)
    if not hits:
        return ""

    return _render_block(hits, max_chars)


def main() -> None:
    try:
        raw_text = sys.stdin.read()
    except Exception:
        raw_text = ""

    try:
        raw_payload = json.loads(raw_text) if raw_text.strip() else {}
    except json.JSONDecodeError:
        raw_payload = {}
    if not isinstance(raw_payload, dict):
        raw_payload = {}

    cwd = raw_payload.get("cwd") or os.getcwd()
    root = me.resolve_project_root(cwd)

    output = ""
    try:
        payload = me.normalize_payload(raw_payload)
        output = recall(root, payload)
    except Exception as exc:
        me._log(root, f"memory_recall: unhandled error: {exc}")
        output = ""

    if output:
        print(output)
    sys.exit(0)


if __name__ == "__main__":
    main()
