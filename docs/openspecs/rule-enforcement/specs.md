# Specification: Rule Enforcement Architecture

## 1. Rule Format
```
<ID> <SEVERITY> [<enforcement>] - <one checkable sentence>
```
- `<ID>`: Stable identifier (e.g., `R1`, `6.1`).
- `<SEVERITY>`: `MUST`, `MUST NOT`, `SHOULD`.
- `[<enforcement>]`:
  - `[hook]`: Blocks completion mechanically via Stop hook running `make verify`.
  - `[lint]`: Static analyzer or grep rule in `make verify`.
  - `[test]`: Unit or architecture test in `make verify`.
  - `[review]`: Human or `/review` only.

## 2. Stop Hook Contract (`tools/verify_gate.py`)
- Reads JSON payload from stdin.
- Loop guard: If `stop_hook_active` is true -> exit 0.
- Root check: If no `Makefile` with a `verify:` target -> exit 0 silently.
- Trust check: If the project is not in the user's trust file (`tools/pb_trust.py`, outside the repo) -> exit 0 silently without running make. A Makefile is repo-controlled code.
- Run `make verify` with timeout (default 300s).
- On failure: print tail of stdout/stderr and exit 2 (blocks stop).
- On success: exit 0.

## 3. Skill `rule-enforcement`
- Converts project rules into language-native architecture tests (`test/architecture/`).
- Wires tests into project `make verify`.
