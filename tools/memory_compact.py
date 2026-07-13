#!/usr/bin/env python3
"""PreCompact hook entry point.

Reads the host's hook stdin JSON, extracts any <adr> blocks the agent
flagged in the transcript, writes them (plus a heuristic session rollup) as
git-tracked markdown under docs/ai/, then embeds+upserts everything into
.ai-memory/memory.db. Source-of-truth markdown is always written before
anything is embedded. Never breaks the session: any internal error is
logged to .ai-memory/engine.log and the hook still exits 0 with empty
stdout (REQ-004).
"""

import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import memory_engine as me  # noqa: E402

ADR_PATTERN = re.compile(
    r'<adr\s+title="(?P<title>[^"]*)"\s*>\s*'
    r"<decision>(?P<decision>.*?)</decision>\s*"
    r"<rationale>(?P<rationale>.*?)</rationale>\s*"
    r"</adr>",
    re.DOTALL,
)


def _slugify(text: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return slug[:60] or "untitled"


def _render_adr(title: str, decision: str, rationale: str, created_at: str) -> str:
    return (
        f"# {title}\n\n"
        f"- Status: accepted\n"
        f"- Date: {created_at}\n\n"
        f"## Decision\n\n{decision.strip()}\n\n"
        f"## Rationale\n\n{rationale.strip()}\n"
    )


def _render_rollup(transcript_text: str, session_id, created_at: str) -> str:
    stripped = transcript_text.strip()
    preview = stripped[:2000]
    return (
        f"# Session rollup — {created_at}\n\n"
        f"- Session ID: {session_id or 'unknown'}\n"
        f"- Transcript length: {len(stripped)} chars\n\n"
        f"## Preview\n\n{preview}\n"
    )


def _write_markdown(out_dir: str, timestamp: str, slug: str, content: str) -> str:
    """Write content under out_dir/timestamp-slug.md. An existing file with
    identical content is reused (no-op write); an existing file with
    different content is disambiguated with an 8-char content_sha suffix -
    an existing file is never overwritten."""
    Path(out_dir).mkdir(parents=True, exist_ok=True)
    path = Path(out_dir) / f"{timestamp}-{slug}.md"
    if path.exists():
        if path.read_text(encoding="utf-8") == content:
            return str(path)
        sha8 = me.content_sha(content)[:8]
        path = Path(out_dir) / f"{timestamp}-{slug}-{sha8}.md"
        suffix = 2
        while path.exists() and path.read_text(encoding="utf-8") != content:
            path = Path(out_dir) / f"{timestamp}-{slug}-{sha8}-{suffix}.md"
            suffix += 1
    if not path.exists():
        path.write_text(content, encoding="utf-8")
    return str(path)


def _looks_like_json_line(line: str) -> bool:
    line = line.strip()
    return line.startswith("{") and line.endswith("}")


def _extract_strings(obj):
    if isinstance(obj, str):
        return [obj]
    if isinstance(obj, dict):
        out = []
        for value in obj.values():
            out.extend(_extract_strings(value))
        return out
    if isinstance(obj, list):
        out = []
        for value in obj:
            out.extend(_extract_strings(value))
        return out
    return []


def _read_transcript_text(transcript_path: str) -> str:
    try:
        raw = Path(transcript_path).read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""

    lines = raw.splitlines()
    non_empty = [line for line in lines if line.strip()]
    is_jsonl = bool(non_empty) and all(_looks_like_json_line(line) for line in non_empty)
    if not is_jsonl:
        return raw

    parts = []
    for line in non_empty:
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            continue
        parts.extend(_extract_strings(obj))
    return "\n".join(parts)


def _capture(conn, root: str, out_dir: str, timestamp: str, slug: str, title, kind: str, stable_body: str, rendered_content: str):
    """Write markdown + embed one chunk, deduped and secret-scrubbed.
    Returns the relative source_path, or None if skipped (secret match)."""
    if me.contains_secret(stable_body):
        me._log(root, f"memory_compact: skipped {kind} chunk matching secret pattern (title={title!r})")
        return None

    sha = me.content_sha(stable_body)
    existing = conn.execute("SELECT source_path FROM memory WHERE content_sha = ?", (sha,)).fetchone()
    if existing is not None:
        return existing["source_path"]

    path = _write_markdown(out_dir, timestamp, slug, rendered_content)
    source_path = os.path.relpath(path, root)
    me.upsert(conn, root, kind, title, stable_body, source_path)
    return source_path


def compact(root: str, payload: dict) -> None:
    transcript_path = payload.get("transcript_path")
    if not transcript_path:
        me._log(root, "memory_compact: no transcript_path in payload, skipping")
        return

    text = _read_transcript_text(transcript_path)
    session_id = payload.get("session_id")
    created_at = me._now_iso()
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d-%H%M%S")

    conn = me.init_db(root)

    for match in ADR_PATTERN.finditer(text):
        title = match.group("title").strip() or "untitled-decision"
        decision = match.group("decision").strip()
        rationale = match.group("rationale").strip()
        stable_body = f"{title}\n\n{decision}\n\n{rationale}"
        rendered = _render_adr(title, decision, rationale, created_at)
        _capture(conn, root, me.adr_dir(root), timestamp, _slugify(title), title, "adr", stable_body, rendered)

    rollup_title = f"Session rollup {created_at}"
    rollup_slug = _slugify(str(session_id) if session_id else "rollup")
    rendered_rollup = _render_rollup(text, session_id, created_at)
    _capture(conn, root, me.archive_dir(root), timestamp, rollup_slug, rollup_title, "summary", text.strip(), rendered_rollup)


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

    try:
        payload = me.normalize_payload(raw_payload)
        compact(root, payload)
    except Exception as exc:
        me._log(root, f"memory_compact: unhandled error: {exc}")

    sys.exit(0)


if __name__ == "__main__":
    main()
