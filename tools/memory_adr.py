#!/usr/bin/env python3
"""Record one architecture decision (ADR) from any agent: `/record-decision`.

Hook-free counterpart of the <adr> capture in memory_compact.py, for agents
without a PreCompact hook (Gemini/Antigravity, Codex). Writes
docs/ai/adr/<timestamp>-<slug>.md and indexes it in the shared memory store, so
every agent recalls it. Works only in projects that opted in with /init-memory
(docs/ai exists and the project is trusted). Refuses text that looks like a secret.

  memory_adr.py --title T --decision D --rationale R [--root .]
  echo '{"title": "...", "decision": "...", "rationale": "..."}' | memory_adr.py --json
"""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import memory_compact as mc  # noqa: E402
import memory_engine as me  # noqa: E402
import pb_trust  # noqa: E402


def record(root: str, title: str, decision: str, rationale: str):
    """Returns (source_path, None) on success or (None, error message)."""
    title, decision, rationale = title.strip(), decision.strip(), rationale.strip()
    if not (title and decision and rationale):
        return None, "title, decision and rationale are all required"

    stable_body = f"{title}\n\n{decision}\n\n{rationale}"
    if me.contains_secret(stable_body):
        return None, "text looks like it contains a secret (key/token/password); not recorded"

    created_at = me._now_iso()
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d-%H%M%S")
    rendered = mc._render_adr(title, decision, rationale, created_at)
    conn = me.init_db(root)
    source_path = mc._capture(
        conn, root, me.adr_dir(root), timestamp, mc._slugify(title), title, "adr", stable_body, rendered
    )
    if source_path is None:
        return None, "could not record the decision (see engine.log)"
    return source_path, None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--root", default=".", help="Project directory (default: cwd)")
    parser.add_argument("--title")
    parser.add_argument("--decision")
    parser.add_argument("--rationale")
    parser.add_argument("--json", action="store_true", help="read title/decision/rationale as a JSON object from stdin")
    args = parser.parse_args()

    root = me.resolve_project_root(args.root)
    if not pb_trust.memory_enabled(root):
        print(
            f"memory_adr: memory is not enabled for {root}. Run /init-memory first "
            "(creates docs/ai and trusts the project).",
            file=sys.stderr,
        )
        return 1

    fields = {"title": args.title, "decision": args.decision, "rationale": args.rationale}
    if args.json:
        try:
            data = json.loads(sys.stdin.read())
            fields = {key: data.get(key) for key in fields}
        except (json.JSONDecodeError, AttributeError):
            print("memory_adr: --json expects a JSON object on stdin", file=sys.stderr)
            return 1
    fields = {key: (value or "") for key, value in fields.items()}

    try:
        path, error = record(root, **fields)
    except Exception as exc:  # never leave a traceback in the agent's context
        me._log(root, f"memory_adr: unhandled error: {exc}")
        path, error = None, f"unexpected error: {exc}"
    if error:
        print(f"memory_adr: {error}", file=sys.stderr)
        return 1
    print(f"memory_adr: recorded {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
