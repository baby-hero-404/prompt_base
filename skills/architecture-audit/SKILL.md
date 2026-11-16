---
name: architecture-audit
description: "Use when a change adds a module or cross-module dependency, moves files between modules, or the user asks whether the structure is still sound: boundaries, circular dependencies, layering, duplicated logic across modules. Diagnoses and proposes; does not rewrite. Triggers on architecture audit, circular dependency, module boundaries, layering violation."
allowed-tools: Read, Glob, Grep, Bash
---

# Architecture Audit

> Keep the shape of the system consistent a little at a time, so nobody has to pay for a rewrite later. This skill **diagnoses and proposes**; code moves only after the user approves.

## When to use

Run it when at least one is true; otherwise skip it and say so:

- The task added a module, package, or service.
- The task added an import or call from one module to another that did not exist before.
- Files moved between modules, or a large refactor happened.
- The user asks for a structural review (periodic, before a release).

**Not this skill:** choosing a design for something new is the `architecture` skill; complexity inside one function or class is `code-simplifier`.

## Scope

- **After a task:** only the dependency edges and modules the change added or moved. Find them from the import lines in the diff.
- **Periodic:** the area the user names, or the whole repository. Go breadth first, inspect the riskiest parts in depth, and list what was surveyed but not inspected. Never present a shallow pass as complete.

## Method

1. **Find the declared rules.** Read the project's architecture document, rule files, and lint or boundary configuration. The declared layering is the standard; do not impose your own.
2. **Map before judging.** Build the module graph for the scope: entry points, modules, who imports whom. Use the `code-graph-analysis` skill; use a graph tool only if the project already has one.
3. **Look for strain**, not style:

| Strain | Evidence to cite |
|---|---|
| Circular dependency | The import lines that close the cycle |
| Boundary leak: a module reaches into another's internals instead of its public surface | The import of an internal path |
| Layering violation: a lower layer imports an upper one, or domain code imports infrastructure | The import line and the declared rule it breaks |
| Hub module that everything imports and nobody can change safely | Count of incoming edges |
| Shallow module: wide public surface that only forwards calls | The forwarding functions |
| Same rule implemented in several modules, drifting apart | Both locations |
| Misplaced code: a new module where an existing one fits, or a file in the wrong layer | The existing home |
| New dependency direction with no stated reason | The first import that created it |

4. **Propose the smallest move** that relieves each strain: move one file, invert one dependency, expose one function on the public surface, merge one duplicate. Prefer a sequence of safe steps to one large cut.
5. **Rank** by pain relieved against effort and risk. Say which moves are safe now and which need tests in place first.
6. **Record large decisions** as a decision record through the `architecture` skill.

## Guardrails

- No move without a named strain. "Cleaner" is not a reason.
- No rewrite proposals. If the only fix is large, say so and split it into steps.
- Structural moves keep behavior fixed and land behind passing tests.
- Do not trade duplication for indirection unless the copies actually drift.
- Every finding cites the file and line of an import or call you read.

## Stop and ask

- The declared rules and the actual code disagree widely: ask which one is right before listing hundreds of violations.
- A fix would change a public contract or a deployment boundary.

## Report

```
Scope:    <edges added by this change | named area | whole repository>
Finding:  <strain> — <file:line evidence>
Move:     <smallest change> — risk <low | medium | high> — tests first: <yes | no>
Not inspected: <areas surveyed only>
```

If the structure is sound, say so in one line.
