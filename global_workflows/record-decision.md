---
description: Record an architecture decision (ADR) into the project's shared memory. Works in any agent, no hook needed.
---

# /record-decision - Record a Decision

$ARGUMENTS

Writes one decision to `docs/ai/adr/` and indexes it, so Claude, Gemini/Antigravity and Codex all recall it later. Only for projects that ran `/init-memory`.

1. Pick a decision worth keeping: a choice between alternatives that the code alone does not explain (a rejected option, a constraint, a trade-off). Skip routine edits.
2. Write three short parts: **title** (one line), **decision** (what was chosen), **rationale** (why, including rejected alternatives). Never include secrets, keys or tokens: the tool refuses them.
3. Record it. Use stdin JSON so quotes and newlines need no shell escaping:

   ```bash
   python3 ~/.agents/tools/memory_adr.py --root . --json <<'JSON'
   {"title": "...", "decision": "...", "rationale": "..."}
   JSON
   ```

   The script prints the file it wrote. Show that path to the user.
4. If it reports that memory is not enabled, tell the user to run `/init-memory` first. Do not create `docs/ai/` yourself.
5. The ADR is project data written for the user's repo: mention that `docs/ai/adr/` is meant to be committed.
