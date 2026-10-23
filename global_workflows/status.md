---
description: Project-wide health check and task tracking.
---

# /status - Project Status

$ARGUMENTS

---

## Behavior

1. Display active tasks and progress markers.
2. Check memory budget and active JIT skills.
3. Report current architectural health.
4. If `docs/ai/manifest.json` exists, run `python3 tools/memory_stale.py --root .` and report whether project memory is stale (refresh with `/init-memory`).
