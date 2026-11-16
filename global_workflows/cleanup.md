---
description: Post-task cleanup of your own change, or an on-request repository-wide sweep. Understand, implement, cleanup, simplify, verify.
---

# /cleanup - Own What You Changed

$ARGUMENTS

---

## Mode

- **No argument (default): per-task pass.** Works only on the change set: lines this task added or modified, code those edits orphaned, and new untracked files. Measured against the commit the task started from; if unknown, against `git diff HEAD`. Never assume `origin/main` exists. Uncommitted edits that are not from this task are not yours: do not touch them; ask if unsure.
- **`sweep [path]`: repository-wide pass.** Only when the user asks. Follow the `codebase-cleanup` skill: survey read-only, propose the list, wait for approval, apply in small groups.

## Behavior (per-task pass)

Run when the feature or fix works and its tests pass, before you report it done.

1. `code-cleanup`: comments, debug output, drafts, defensive boilerplate, stale docs in the change set.
2. `code-simplifier`: single-use abstractions, pass-through layers, needless options.
3. `dead-code-removal`: whatever steps 1 and 2 and the task itself orphaned. Evidence for every deletion; uncertain items are reported, not removed.
4. `test-hygiene`: tests the task added, changed, or made obsolete.
5. `code-review`: read the full diff, including untracked files, against the request.
6. `architecture-audit`, **only if** a module or package was added, a dependency between modules was added, or files moved between modules. Otherwise write "skipped: no structural change".
7. `verification-before-completion`: run tests, linter, and build; read the output.

If a cleanup edit breaks verification, undo that edit. Never weaken, skip, or delete a valid test to get green.

Behavior or a public contract would change: stop and ask.

## Report

```
Removed:              <item> — <evidence in one line>
Simplified:           <item> — <what and why>
Potentially unused:   <item> — <check that could not be completed>
Left on purpose:      <item> — <reason>
Noticed, not changed: <problem outside the change set>
Verification:         <command> → <result>
```

If a step found nothing, say so in one line for that step and make no edit. Do not invent work.
