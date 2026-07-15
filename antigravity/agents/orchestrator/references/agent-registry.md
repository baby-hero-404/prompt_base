# Orchestrator Agent Registry

| Agent | Domain & Focus | Mandatory When? |
|-------|----------------|-----------------|
| `project-planner` | Plan artifacts, task breakdown (OpenSpec set `docs/openspecs/<task>/` preferred; fallback `docs/plans/PLAN-*.md`) | **Step 0** (No plan artifact = No work) |
| `security-auditor` | Security, Auth, OWASP, Vulnerabilities | Touching auth or sensitive data |
| `backend-specialist` | Node.js, API, Server logic, DB queries | Working on server-side |
| `frontend-specialist` | React, Next.js, UI, Styles, Components | Working on web UI |
| `mobile-developer` | RN, Flutter, Mobile UX | Working on mobile apps |
| `test-engineer` | Testing, Mocks, TDD, Coverage | **MANDATORY** for all code changes |
| `database-architect` | Schema, Migrations, Query optimization | Touching DB schema |
| `devops-engineer` | CI/CD, Deployment, Monitoring | Deployment tasks |
| `debugger` | Root cause, systematic investigation | Complex bugs |
| `explorer-agent` | Discovery, Mapping dependencies | Initial phase of complex tasks |
| `performance-optimizer` | Profiling, Caching, Speed | Optimization tasks |
| `seo-specialist` | SEO, Meta tags, Analytics | Marketing/SEO tasks |
| `documentation-writer` | Docs, README, JSDoc | **Optional**: User must request |

---

## Agent-Project Compatibility Matrix

| Project Type | Lead Agent | Banned Agents |
|--------------|------------|---------------|
| **MOBILE** | `mobile-developer` | ❌ frontend-specialist, backend-specialist |
| **WEB** | `frontend-specialist` | ❌ mobile-developer |
| **BACKEND** | `backend-specialist` | - |
