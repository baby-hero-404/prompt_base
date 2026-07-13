# Design: Skill Consolidation 2026

## Architecture

```mermaid
flowchart TD
    subgraph Current
        A1[code-review-checklist]
        A2[review-pre-commit-git]
        A3[verification-before-completion]
    end
    
    subgraph Consolidated
        B1[verification-before-completion]
    end
    
    A1 --> B1
    A2 --> B1
    A3 --> B1
    
    C1[frontend-design] --> D1[ux-ui-pro-max]
    
    E1[red-team-tactics] --> F1[red-team-operations]
    E2[red-teaming] --> F1
    
    G1[tdd-workflow] -->|References| H1[testing-patterns]
```

## Security & Execution Boundaries

| Agent | Allowed Paths | Permissions |
|-------|---------------|-------------|
| Orchestrator | `antigravity/skills/` | Read, Write, Delete |
| Orchestrator | `docs/openspecs/` | Read |
| Orchestrator | `registry.min.json` | Write (via make) |

## Risk Mitigation

| Risk | Severity | Mitigation |
|------|----------|------------|
| Dangling References | HIGH | Ensure `grep` is run across `antigravity/agents/` and `antigravity/global_workflows/` to update any hardcoded references to deprecated skills. |
| Missing Information | MEDIUM | Before deleting a skill, manually verify its unique contents are migrated to the destination skill. |
