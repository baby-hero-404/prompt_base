#!/usr/bin/env python3
"""Claude Code Stop hook: run the project's `make verify` before the agent may finish.

Exit 0 allows the stop. Exit 2 with stderr blocks it and feeds the failure back
to the agent. The gate is a silent no-op unless the working directory has a
Makefile with a `verify` target in a project listed in the user's trust file
(`tools/pb_trust.py`), so it is safe to register globally.

Speed: a project may define `verify-fast`, which the gate prefers over `verify`
(run the full `make verify` yourself before committing). After a passing run the
gate stores a fingerprint of the working tree and skips the next run while
nothing changed (chat-only turns). `PB_VERIFY_FORCE=1` disables the skip.
"""
import hashlib
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
VERIFY_FAST_TARGET = re.compile(r"^verify-fast\s*:(?!=)", re.MULTILINE)


def tree_fingerprint(cwd: Path):
    """Hash HEAD plus (path, mtime, size) of every tracked or unignored file.

    Returns None when the directory is not a usable git work tree, which makes
    the gate always run (never skip on an unknown state)."""
    try:
        head = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=cwd, capture_output=True, text=True, timeout=10
        ).stdout.strip()
        listing = subprocess.run(
            ["git", "ls-files", "-z", "-c", "-o", "--exclude-standard"],
            cwd=cwd, capture_output=True, timeout=30, check=True,
        ).stdout
    except (OSError, subprocess.SubprocessError):
        return None
    digest = hashlib.sha256(head.encode())
    for raw in sorted(set(listing.split(b"\0"))):
        if not raw:
            continue
        name = os.fsdecode(raw)
        try:
            st = (cwd / name).lstat()
            digest.update(f"{name}\0{st.st_mtime_ns}\0{st.st_size}\n".encode())
        except OSError:
            digest.update(f"{name}\0missing\n".encode())
    return digest.hexdigest()


def cache_file(cwd: Path) -> Path:
    base = os.environ.get("PB_VERIFY_CACHE_DIR") or str(Path.home() / ".agents" / "verify_cache")
    return Path(base) / (hashlib.sha256(str(cwd.resolve()).encode()).hexdigest()[:16] + ".json")


def unchanged_since_last_pass(cwd: Path, target: str):
    """Return (skip, fingerprint) where skip is True if this tree already passed `target`."""
    if os.environ.get("PB_VERIFY_FORCE") == "1":
        return False, None
    fingerprint = tree_fingerprint(cwd)
    if fingerprint is None:
        return False, None
    try:
        saved = json.loads(cache_file(cwd).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return False, fingerprint
    return saved.get("target") == target and saved.get("fingerprint") == fingerprint, fingerprint


def remember_pass(cwd: Path, target: str) -> None:
    # Re-fingerprint after the run: verify may regenerate files, and those must count as "seen".
    fingerprint = tree_fingerprint(cwd)
    if fingerprint is None or os.environ.get("PB_VERIFY_FORCE") == "1":
        return
    try:
        path = cache_file(cwd)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps({"target": target, "fingerprint": fingerprint}), encoding="utf-8")
    except OSError:
        pass


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
        makefile_text = makefile.read_text(encoding="utf-8")
    except OSError:
        return allow()
    if not VERIFY_TARGET.search(makefile_text):
        return allow()
    target = "verify-fast" if VERIFY_FAST_TARGET.search(makefile_text) else "verify"

    # A Makefile is repo-controlled code: only run it for projects the user trusted
    # (python3 tools/pb_trust.py --add), never automatically in a freshly cloned repo.
    if not pb_trust.is_trusted(cwd):
        return allow()

    skip, _ = unchanged_since_last_pass(cwd, target)
    if skip:
        return allow()

    try:
        timeout = int(os.environ.get("PB_VERIFY_TIMEOUT", DEFAULT_TIMEOUT_SECONDS))
    except ValueError:
        timeout = DEFAULT_TIMEOUT_SECONDS

    try:
        result = subprocess.run(
            ["make", target], cwd=cwd, capture_output=True, text=True, timeout=timeout
        )
    except subprocess.TimeoutExpired:
        print(f"verify_gate: `make {target}` timed out after {timeout}s; not blocking.", file=sys.stderr)
        return allow()
    except OSError as exc:
        print(f"verify_gate: could not run make ({exc}); not blocking.", file=sys.stderr)
        return allow()

    if result.returncode == 0:
        remember_pass(cwd, target)
        return allow()

    output = (result.stdout + result.stderr).strip()
    if len(output) > MAX_OUTPUT_CHARS:
        output = "...(truncated)...\n" + output[-MAX_OUTPUT_CHARS:]

    if is_gemini:
        reason = f"`make {target}` failed (exit {result.returncode}). Fix these before finishing:\n{output}"
        print(json.dumps({"decision": "continue", "reason": reason}))
        return 0
    else:
        print(
            f"`make {target}` failed (exit {result.returncode}). Fix these before finishing:\n{output}",
            file=sys.stderr,
        )
        return 2


if __name__ == "__main__":
    sys.exit(main())
