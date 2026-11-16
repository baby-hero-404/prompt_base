---
name: dead-code-removal
description: "Use when finding or deleting code that is no longer used: functions, files, imports, types, dependencies, feature flags, obsolete tests. Requires evidence before every deletion and lists analysis tools per ecosystem. Triggers on dead code, unused code, unused imports, unused dependencies, obsolete code."
allowed-tools: Read, Write, Edit, Glob, Grep, Bash
references: [tools.md]
---

# Dead Code Removal

> Dead code is not harmless: readers and agents assume it matters and keep it "compatible". But a wrong deletion costs more than a leftover. **No deletion without evidence.**

## When to use

- A task replaced, renamed, or removed something: look for what it orphaned.
- After `code-simplifier` inlined an abstraction.
- The user asks for unused code, files, or dependencies to be found or removed.

## Scope

In a normal task: only what the task orphaned (the change set, as defined in `code-cleanup`). Older dead code goes under "Noticed, not changed". A wider search needs the user's request; then propose the full list first and delete in small groups, verifying after each.

Never touch generated, vendored, or third-party code.

## Step 1: Collect candidates

Functions, methods, classes, types, constants, imports, files, dependencies, configuration keys, environment variables, feature flags that are permanently on or off, unreachable branches, tests of removed behavior, orphaned fixtures, assets, and documentation.

Use an analysis tool if the project already has one; see `references/tools.md`. If none is installed, use text search and the compiler or linter already present, and mark results "lower confidence". Do not install a tool without asking.

Code referenced only by its own tests is still a candidate: tests are not users.

## Step 2: Verify each candidate

A candidate with no static reference is not yet proven. Check every item that applies:

- [ ] Search the whole repository for the name, including non-code files: configuration, templates, build files, scripts, continuous integration, documentation.
- [ ] Name built at run time: string lookup, reflection, dynamic import, attribute access by string.
- [ ] Framework registration: routes, dependency injection, plugins, decorators, signal or event handlers, serialization fields, migrations.
- [ ] Entry points: command-line scripts, package manifest fields, task runners.
- [ ] Exported or published API: a library's public symbols are used by code you cannot see.
- [ ] Other packages in the same monorepo; other languages calling across a boundary.
- [ ] For a dependency: plugins loaded by name, tools invoked only from scripts, type-only packages, peer requirements.

When a tool and the manual checks disagree, the manual evidence wins.

## Step 3: Decide

| Verdict | Meaning | Action |
|---|---|---|
| **Proven unused** | Every applicable check done, no use found | Delete |
| **Potentially unused** | Any check could not be completed, or a dynamic use is plausible | Report only |

Keep one evidence record per item:

```
Item:     <name or path> (<symbol | file | dependency | test | flag>)
Searched: <terms and where>
Dynamic:  <checks done and result>
Tool:     <tool and its output line, or "none">
Verdict:  proven unused | potentially unused
```

## Step 4: Delete completely

- Delete the item together with its tests, imports, documentation mentions, configuration, and manifest entry.
- Do not comment it out, leave a "removed" marker, or rename it to hide a warning. Version control keeps history.
- Deleting creates new orphans. Repeat steps 1 to 3 for whatever the deletion left without a user.

## Step 5: Verify

- A search for the removed name returns no hits.
- Build, tests, and linter pass. If something fails, restore the item and downgrade it to "potentially unused"; never delete or weaken a valid test to pass.

## Do not delete

- A placeholder for planned work that states its condition.
- Public API of a library, unless the user confirms the breaking change.
- Anything whose removal would change behavior, a contract, or stored data: stop and ask.
- Uncommitted work that is not from this task.

## Report

```
Removed:              <item> — <evidence in one line>
Potentially unused:   <item> — <which check could not be completed>
Noticed, not changed: <older dead code outside the change set>
Verification:         <command> → <result>
```
