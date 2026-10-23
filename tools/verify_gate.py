#!/usr/bin/env python3
"""Claude Code Stop hook: run the project's `make verify` before the agent may finish.

Exit 0 allows the stop. Exit 2 with stderr blocks it and feeds the failure back
to the agent. The gate is a silent no-op unless the working directory has a
Makefile with a `verify` target in a project listed in the user's trust file
(`tools/pb_trust.py`), so it is safe to register globally.
"""
import json
import os
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import pb_trust  # noqa: E402

DEFAULT_TIMEOUT_SECONDS = 300
MAX_OUTPUT_CHARS = 4000
VERIFY_TARGET = re.compile(r"^verify\s*:(?!=)", re.MULTILINE)


def main() -> int:
    try:
        payload = json.loads(sys.stdin.read())
        is_gemini = "workspacePaths" in payload or "executionNum" in payload or "terminationReason" in payload
        cwd_str = (payload.get("workspacePaths") or [None])[0] or payload.get("cwd") or os.getcwd()
        cwd = Path(cwd_str)
    except (json.JSONDecodeError, TypeError, AttributeError):
        return 0

    def allow():
        if is_gemini:
            print(json.dumps({"decision": "allow"}))
        return 0

    # A previous block already sent the agent back to fix things; never loop.
    if payload.get("stop_hook_active"):
        return allow()

    makefile = cwd / "Makefile"
    try:
        if not VERIFY_TARGET.search(makefile.read_text(encoding="utf-8")):
            return allow()
    except OSError:
        return allow()

    # A Makefile is repo-controlled code: only run it for projects the user trusted
    # (python3 tools/pb_trust.py --add), never automatically in a freshly cloned repo.
    if not pb_trust.is_trusted(cwd):
        return allow()

    try:
        timeout = int(os.environ.get("PB_VERIFY_TIMEOUT", DEFAULT_TIMEOUT_SECONDS))
    except ValueError:
        timeout = DEFAULT_TIMEOUT_SECONDS

    try:
        result = subprocess.run(
            ["make", "verify"], cwd=cwd, capture_output=True, text=True, timeout=timeout
        )
    except subprocess.TimeoutExpired:
        print(f"verify_gate: `make verify` timed out after {timeout}s; not blocking.", file=sys.stderr)
        return allow()
    except OSError as exc:
        print(f"verify_gate: could not run make ({exc}); not blocking.", file=sys.stderr)
        return allow()

    if result.returncode == 0:
        return allow()

    output = (result.stdout + result.stderr).strip()
    if len(output) > MAX_OUTPUT_CHARS:
        output = "...(truncated)...\n" + output[-MAX_OUTPUT_CHARS:]

    if is_gemini:
        reason = f"`make verify` failed (exit {result.returncode}). Fix these before finishing:\n{output}"
        print(json.dumps({"decision": "continue", "reason": reason}))
        return 0
    else:
        print(
            f"`make verify` failed (exit {result.returncode}). Fix these before finishing:\n{output}",
            file=sys.stderr,
        )
        return 2


if __name__ == "__main__":
    sys.exit(main())
