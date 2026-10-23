# Proposal: Per-Project Rule Sync & Deterministic Enforcement

## 1. Context & Motivation
Agents drift from project rules in long conversations because:
1. Project rules are not reliably loaded into conversation context.
2. Rules are advisory prose with no mechanical check.
3. Rule files lacked stable numbering and clear enforcement tags.

## 2. Key Decisions
- **Enforcement Tags**: Every rule has an ID and tag: `[hook] [lint] [test] [review]`.
- **Mechanical Checks**: All checkable rules (`[test]`/`[lint]`) are implemented as automated tests or linter checks wired into the project's `verify` target.
- **Stop Hook Gate**: `tools/verify_gate.py` runs `make verify` on `Stop` event. If verification fails, it exits with code 2 and blocks completion, sending failures back to the agent.
- **Sole Plan Standard**: OpenSpec (`docs/openspecs/<task>/`) is the sole planning standard. Legacy `docs/plans/` is eliminated.
