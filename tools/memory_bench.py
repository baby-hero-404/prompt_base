#!/usr/bin/env python3
"""Manual/dev cold-start latency calibration (`make memory-bench`).

Forces a fresh measurement of the local embedding backend's import+load
time and records it as meta.embed_load_ms for a given project, so
memory_recall.py's latency budget check (REQ-008) has a real number to
compare against.

In normal use this isn't required: tools/memory_engine.py's upsert()
auto-records the same measurement the first time a project's PreCompact
hook actually loads the model (PreCompact is non-blocking, so it may always
pay that cost). This script exists for explicit re-calibration, CI, or
running against this repo's own checkout during development - not as the
primary way real projects get calibrated, since a project's PreCompact hook
already does it automatically without any manual step.
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import memory_engine as me  # noqa: E402


def bench(root: str):
    """Force a fresh cold-load measurement, ignoring any backend already
    cached in this process. Returns the measured ms, or None if no local
    embedding backend is available."""
    me._EMBED_BACKEND = None
    me._COLD_LOAD_MS = None
    vector, _model, _dim = me.embed("benchmark calibration probe", root=root)
    if vector is None:
        return None
    return me._COLD_LOAD_MS


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".", help="Project directory to calibrate (default: cwd)")
    args = parser.parse_args()

    root = me.resolve_project_root(args.root)
    load_ms = bench(root)
    if load_ms is None:
        print(
            "memory_bench: no local embedding backend available (fastembed not installed in this "
            "interpreter); nothing recorded. Run this with the venv's python after `make memory-setup`.",
            file=sys.stderr,
        )
        sys.exit(1)

    conn = me.init_db(root)
    me.set_embed_load_ms(conn, load_ms)
    print(f"memory_bench: recorded embed_load_ms={load_ms:.1f} for {root}")


if __name__ == "__main__":
    main()
