# Memory & Context Slot System

## 🎯 Intent
Prevent "token bloat" and maintain reasoning precision by enforcing a strictly modular context window.

## 🤖 Automated Long-Term Tier (Hook-Enforced)
Long-term memory — architectural decisions and session rollups — is handled automatically by the context memory engine's `PreCompact`/`UserPromptSubmit` hooks when installed (`make memory-setup`; see `project-memory` skill, Section 0, and `docs/openspecs/context-memory-engine-2026/`). To get a decision captured, emit:

```
<adr title="Short decision title">
  <decision>What was decided.</decision>
  <rationale>Why, including rejected alternatives.</rationale>
</adr>
```

This is **enforcement, not advisory**: the hooks run whether or not the agent remembers to prune. Everything below — the Slot Protocol and General Memory Rules — governs in-session context hygiene at all times, and is also the **complete fallback** when hooks are disabled or not installed for a project: without hooks, long-term memory reverts to whatever the agent manually captures in `docs/ai/` via the discipline below.

## 📥 Slot Management (QUOTA: 1 per Slot)
To prevent rules from bleeding into each other, the AI MUST manage its memory using these "Slots":

| Slot Label | Domain Coverage |
|------------|-----------------|
| `SLOT_UX`  | Frontend, Mobile Design, UI, Styling, UX Psychology. |
| `SLOT_APP` | Business Logic, API, Backend, TypeScript Expert, Python Patterns. |
| `SLOT_OPS` | Docker, DevOps, CI/CD, Security, Cloud Infra. |
| `SLOT_QA`  | Unit Testing, E2E, Quality Gates, Debugging logs. |
| `SLOT_MAP` | Registry, Architecture, docs/plans/PLAN-*.md (Permanently Fixed). |

---

## 🏗️ The Slot Protocol (MANDATORY)

1. **Activation**: When loading a skill, assign it to a slot (e.g., "Loading `mobile-design` into `SLOT_UX`").
2. **Conflict Check**: If a slot is occupied, you MUST declare an `UNLOAD` before loading the new skill.
   - *Example*: "Unloading `frontend-design` from `SLOT_UX` to load `mobile-design`."
3. **Sub-task Pruning**: Once a specific sub-task (e.g., "Style the button") ends, immediately clear the reference materials from that slot.
4. **Context Summary**: Every 5 tool calls, verify if current loaded skills are still needed. If not, PRUNE.

---

## 🧹 General Memory Rules
1. **No Repeats**: Do not repeat full file contents. Use diffs and line-index references.
1. **Artifact Truth**: Rely on `docs/plans/PLAN-*.md` for state, not chat history.
3. **History Summarization**: If history > 15 turns, stop and provide a "Context Snapshot".
4. **JIT Reading**: Use `grep_search` or `view_file` with `StartLine/EndLine` to read only relevant snippets. Never read >500 lines unless creating a core index.
5. **Registry Lookup**: Do not read `registry.min.json` in full more than once per session. Use `grep_search` to find specific agent/skill paths by ID.
6. **Aggressive Pruning**: After EVERY major sub-task completion, execute an `UNLOAD` on all relevant slots.
7. **No "Meta-Chat"**: Avoid apologies, conversational filler, or repeating the user's request. Jump straight to the solution.
