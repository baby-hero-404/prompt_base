# Orchestration Enforcement Protocols

## 1. Step 0: Pre-Flight Check (MANDATORY)

**Stop all work if these checkpoints fail!**

| Check | Tool / Verification | Action if Failed |
|-------|---------------------|------------------|
| **Plan artifact exists?** | `ls docs/openspecs/*/tasks.md docs/plans/PLAN-*.md` (OpenSpec set takes precedence) | Use `project-planner` first. |
| **Project Type?** | WEB / MOBILE / BACKEND | Determine via analyzer or ask. |
| **Agent Routing?** | Check matrix in `agent-registry.md` | Re-route to valid agents. |
| **Socratic Gate?** | 3 strategic questions answered | Ask questions before code. |

---

## 2. Agent Boundary Enforcement

**Each agent MUST stay within their domain. Cross-domain work is a violation.**

### Domain Boundaries
- `frontend-specialist`: UI/UX, styles, components. ❌ BLOCKED: Test files, backend logic.
- `backend-specialist`: API, DB queries, logic. ❌ BLOCKED: UI components, styles.
- `test-engineer`: **ONLY** files matching `**/*.test.*` or `**/__tests__/**`. ❌ BLOCKED: Production code.
- `database-architect`: Migrations, schema, queries. ❌ BLOCKED: API routing, UI.
- `security-auditor`: Audit, review, threat model. ❌ BLOCKED: Implementation code.

---

## 3. Conflict Resolution

### Disagreement Between Agents
1. Note both perspectives.
2. Explain trade-offs.
3. Recommend based on priority: **Security > Stability > Performance > Convenience**.

### Same File Edits
- Collect all suggestions → Present merged recommendation → User confirms.

---

## 4. Context Slot Enforcement
**Orchestrator must ensure agents don't flood the context window.**

- **Slot Quota**: Verify agents follow the `SLOT_UX`, `SLOT_APP`, `SLOT_OPS`, `SLOT_QA` quotas.
- **Unload Mandate**: If switching between heavy domains (e.g. Frontend to Backend), force an `UNLOAD` declaration.
- **Verification**: Check if skills not mentioned in the immediate `PLAN` step are still in context. Apply "JIT Pruning".
