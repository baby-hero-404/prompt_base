#!/usr/bin/env python3
"""Re-inject a project's invariant rules so long conversations do not drop them.

Source of truth is agent-neutral markdown: <root>/docs/ai/DOMAIN.md, section
"## Invariant Rules" (legacy fallback: ~/.gemini/projects/<parent>-<leaf>/DOMAIN.md).

Two modes:
  --print [--root DIR]   print the invariants (any agent can call this)
  (default)              Claude Code UserPromptSubmit hook: JSON on stdin; emits on the
                         first prompt of a session and every PB_INVARIANT_EVERY-th (10),
                         only for projects trusted via tools/pb_trust.py
Never breaks a session: always exit 0, errors go to the engine log.
"""
import argparse
import json
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import memory_engine as me  # noqa: E402
import pb_trust  # noqa: E402

DEFAULT_EVERY = 10
MAX_CHARS = 1500
STATE_NAME = "invariants_state.json"
SECTION = re.compile(r"^## Invariant Rules[^\n]*\n(.*?)(?=^## |\Z)", re.MULTILINE | re.DOTALL)


def _domain_candidates(root: str):
    root_path = Path(root).resolve()
    yield root_path / "docs" / "ai" / "DOMAIN.md"
    project_subpath = f"{root_path.parent.name}-{root_path.name}/DOMAIN.md"
    legacy_env = os.environ.get("PB_LEGACY_PROJECTS_DIR")
    if legacy_env:
        yield Path(legacy_env).expanduser() / project_subpath
    else:
        yield Path("~/.gemini/projects").expanduser() / project_subpath
        yield Path("~/.claude/projects").expanduser() / project_subpath


def load_invariants(root: str) -> str:
    """Capped invariant text, or "" when missing, empty, or it looks like it holds a secret."""
    for path in _domain_candidates(root):
        try:
            text = path.read_text(encoding="utf-8")
        except OSError:
            continue
        match = SECTION.search(text)
        if not match:
            continue
        lines = [ln.rstrip() for ln in match.group(1).splitlines() if ln.strip() and not ln.lstrip().startswith("*(")]
        body = "\n".join(lines)
        if not body or me.contains_secret(body):
            return ""
        if len(body) > MAX_CHARS:
            body = body[:MAX_CHARS].rsplit("\n", 1)[0] + "\n..."
        return f"Project invariants (summary from {path.name}; verify against the project's rule files):\n{body}"
    return ""


def _every() -> int:
    try:
        return max(1, int(os.environ.get("PB_INVARIANT_EVERY", DEFAULT_EVERY)))
    except ValueError:
        return DEFAULT_EVERY


def _should_emit(root: str, session_id) -> bool:
    """Count prompts per session; emit on counts 0, N, 2N..."""
    if not session_id:
        return False
    state_path = me.get_memory_dir(root) / STATE_NAME
    count = 0
    try:
        state = json.loads(state_path.read_text(encoding="utf-8"))
        if state.get("session") == str(session_id):
            count = int(state.get("count", 0))
    except (OSError, ValueError, AttributeError):
        pass
    try:
        state_path.parent.mkdir(parents=True, exist_ok=True)
        state_path.write_text(json.dumps({"session": str(session_id), "count": count + 1}), encoding="utf-8")
    except OSError:
        pass
    return count % _every() == 0


def run_hook() -> tuple[str, str]:
    """Returns (output_text, host)"""
    try:
        raw = json.loads(sys.stdin.read() or "{}")
    except json.JSONDecodeError:
        return "", "unknown"
    if not isinstance(raw, dict):
        return "", "unknown"
    norm = me.normalize_payload(raw)
    host = norm.get("host") or "unknown"
    root = me.resolve_project_root(norm.get("cwd") or os.getcwd())
    try:
        # Hook mode injects repo-controlled text into context: trusted projects only.
        if not pb_trust.is_trusted(root):
            return "", host
        invariants = load_invariants(root)
        if not invariants or not _should_emit(root, norm.get("session_id")):
            return "", host
        return invariants, host
    except Exception as exc:  # a hook must never break the session
        me._log(root, f"memory_invariants: unhandled error: {exc}")
        return "", host


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--print", dest="print_mode", action="store_true")
    parser.add_argument("--root", default=".")
    args = parser.parse_args()

    if args.print_mode:
        output = load_invariants(me.resolve_project_root(args.root))
        if output:
            print(output)
    else:
        output, host = run_hook()
        if host == "gemini":
            if output:
                print(json.dumps({"injectSteps": [{"ephemeralMessage": output}]}))
            else:
                print(json.dumps({}))
        else:
            if output:
                print(output)
    return 0


if __name__ == "__main__":
    sys.exit(main())
