---
name: code-simplifier
description: "Use when code is over-engineered or over-abstracted. Triggers on simplify code, over-engineering, over-engineered, unnecessary abstraction, reduce complexity."
allowed-tools: Read, Write, Edit, Glob, Grep, Bash
---

# Code Simplifier

> The codebase should grow in what it does, not in how hard it is to read. Every abstraction must pay for itself today.

## When to use

- After `code-cleanup`, on the code this task wrote or changed.
- The user says something is over-engineered or hard to follow.

**Not this skill:** leftovers such as comments and debug output belong to `code-cleanup`; unused code belongs to `dead-code-removal`; module-level structure belongs to `architecture-audit`.

## Scope

The change set, as defined in `code-cleanup`. Complexity that existed before the task is reported under "Noticed, not changed" unless the user asked for a wider pass.

## Does this abstraction earn its place?

Keep an interface, generic, wrapper, factory, layer, or option only if at least one is true **today**:

1. It has two or more real implementations or callers.
2. It is a module boundary or a public contract.
3. It is a test seam in use at a system edge (network, clock, storage, third-party service).
4. The framework or the project's written conventions require it.

"We might need it later" is not on the list. If none apply, inline it.

## Checklist

| Smell | Simplify to |
|---|---|
| Interface or abstract base with one implementation | The concrete type |
| Function or class that only forwards to another | Call the target directly |
| Factory, builder, strategy, or registry with one variant | Direct construction |
| Generic parameter only ever used with one type | The concrete type |
| Parameter, option, or flag that always gets the same value | A constant, or remove it |
| Helper extracted for one call site that reads no clearer than the code it replaced | Inline it |
| New layer or module that only passes calls through | Collapse it into its caller |
| Deep nesting | Guard clauses and early returns |
| Variable assigned once, used once, with a name that adds nothing | Inline the expression |
| Hand-written utility that the standard library or an existing project utility already provides | Use the existing one |

## Duplication

- Three similar lines are better than a premature abstraction.
- Extract when the copies are more than about three lines, or far apart, **and** must change together.
- Do not merge code that is similar by coincidence, or when the shared helper would need many parameters to cover both cases.
- If the copies already differ, find out which behavior is correct before merging; ask if unclear.
- When duplication is unavoidable (two languages, build time versus run time, two processes), put the same note on every copy naming the other locations, so a search for the note finds them all.

## Procedure

1. Pick one simplification.
2. Confirm a test covers the behavior. If none does, add a test that pins current behavior first, or report the item without changing it.
3. Make the change. Do not add features, widen the public surface, or change behavior.
4. Run the tests. On failure, undo that one change.
5. Repeat. Then hand orphaned code to `dead-code-removal`.

## Do not

- Shorten code at the cost of clarity. Dense one-liners and nested conditional expressions are not simpler.
- Remove an abstraction the framework needs.
- Rewrite stable code outside the change set for taste.
- Replace explicit code with a clever trick.

## Stop and ask

- The simplification would change behavior, an exported symbol, or stored data.
- The abstraction looks unused but may be a planned extension point the user mentioned.

## Report

```
Simplified:           <item> — <what it became and why>
Left on purpose:      <item> — <which of the four reasons applies>
Noticed, not changed: <item outside the change set>
Verification:         <command> → <result>
```
