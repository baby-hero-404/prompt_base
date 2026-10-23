# Project Rules Convention

Copy this folder's convention into the project repo (`AGENTS.md` or `.claude/rules/*.md`), not into `~/.gemini/projects/`. Rules that live with the code are loaded for every clone and reviewed like code.

## Rule format

```
<ID> <SEVERITY> [<enforcement>] - <one checkable sentence>
```

- **ID:** stable and numbered (`6.1`, `SEC-03`). Never renumber; retire an ID instead. `DOMAIN.md` → Invariant Rules cites these IDs.
- **SEVERITY:** `MUST`, `MUST NOT`, `SHOULD`.
- **Enforcement tag** says what stops a violation:
  - `[hook]` blocks the agent mechanically (Stop hook running `make verify`, PreToolUse).
  - `[lint]` static analyzer or grep check inside `make verify`.
  - `[test]` automated test inside `make verify`.
  - `[review]` human or `/review` only. Advisory: expect drift in long conversations.
- Write checkable sentences: "UI file <= 300 lines", not "keep files small".

## Example

```
1.2 MUST NOT [test] - `domain/` imports Flutter, drift, or dio.
6.1 MUST     [test] - UI files stay at or below 300 lines.
9.4 SHOULD   [review] - Prefer composition over inheritance for widgets.
```

## Layout

- Always-on file (`AGENTS.md` / `CLAUDE.md`): at most ~60 lines, only invariants. End it with the 3-5 most critical rules repeated.
- Longer, topic rules: `.claude/rules/<topic>.md`, with `paths:` frontmatter to load them only when matching files are touched.
- Every `[lint]`/`[test]` rule needs a check wired into the project's `verify` target. Use the `rule-enforcement` skill to generate it.
