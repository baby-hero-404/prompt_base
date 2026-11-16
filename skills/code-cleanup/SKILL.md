---
name: code-cleanup
description: "Use when cleaning AI slop and leftovers from your change set after a task. Triggers on ai slop, deslop, clean up my changes, post-task cleanup, leftover code."
allowed-tools: Read, Write, Edit, Glob, Grep, Bash
---

# Code Cleanup (after every task)

> You wrote it, you clean it. A task is not done while its diff still carries drafts, noise, or work nobody asked for.

## When to use

- A feature or fix works and its tests pass, before you report it done.
- The user says the result feels bloated or machine-written.

**Not this skill:** logic that is too complicated belongs to `code-simplifier`; code that lost its last caller belongs to `dead-code-removal`; the whole repository belongs to `codebase-cleanup`.

## Scope: the change set

The **change set** is the only thing you may edit:

- lines this task added or modified,
- code those edits orphaned,
- new untracked files this task created.

Measure it against the commit the task started from. If you do not know that commit, use the working tree against the last commit. Do not assume a remote branch exists.

```bash
git status --short            # includes untracked files
git diff HEAD                 # uncommitted work
git diff <start-commit>..HEAD # committed work of this task
```

Outside the change set:

- Problems you did not create are **reported, not fixed**, under "Noticed, not changed".
- Uncommitted edits that are not from this task belong to the user. Never modify, revert, or stage them. If you cannot tell which edits are yours, ask.
- Generated, vendored, and third-party code is never cleaned.

## Checklist

Read every hunk of the change set and remove what matches.

| Leftover | Action |
|---|---|
| Comment that narrates the code or the edit ("increment counter", "now uses the new client", "fixed the bug") | Delete. Keep comments that explain *why*. |
| Comment, docstring, or nearby documentation that no longer matches the code you changed | Update it, or delete it if nothing is left to say |
| Docstring that restates the name; decorative file banner | Delete, unless it is public API documentation |
| Debug output, breakpoints, temporary logging | Delete. Logging through the project's logger that is meant to stay is fine. |
| Commented-out code, "removed" markers, unused variables renamed to hide a warning | Delete. Version control keeps history. |
| Draft files: scratch scripts, backups, parallel copies with suffixes such as old, new, v2 | Delete, after confirming this task created them |
| TODO or FIXME added by this task with no owner or condition | Do it now, or ask, or state the concrete condition |
| Defensive code for cases that cannot happen on trusted internal paths: redundant null checks, catch-all handlers that swallow errors, fallbacks for impossible states | Remove. Keep validation at system boundaries (user input, network, files, external services). |
| Type escape or lint suppression added only to silence a checker | Fix the type or the code |
| Compatibility shim nobody asked for: alias, re-export, deprecated wrapper | Remove |
| Edits outside the request: reformatted untouched lines, annotations or docstrings added to unchanged code, drive-by renames | Restore the original lines |
| Feature, option, or flag the request did not ask for | Remove, or ask whether it is wanted |
| Test-only code, fixtures, or hard-coded test values in production paths | Move to tests or remove |

## Do not remove

- Comments that explain a reason, a constraint, or a non-obvious choice.
- Licence headers and anything the project's conventions require.
- A marker that says a block is intentionally duplicated elsewhere.
- Checks at a real boundary, even if they look defensive.

## Stop and ask

- Removing the item would change observable behavior or a public contract.
- You cannot tell whether a leftover is intentional.
- The item is not yours.

## Verify and report

After cleaning, re-read the diff to confirm that only leftovers went away, then run the project's tests and linter. If a cleanup edit breaks something, undo that edit; never weaken a test to pass.

Report in a few lines. If the change set was already clean, say so in one line and make no edits.

```
Removed:              <item> — <why it was a leftover>
Left on purpose:      <item> — <reason>
Noticed, not changed: <item outside the change set>
Verification:         <command> → <result>
```
