# Prompt Base Architecture

## 📋 Overview

Prompt Base is a **global-only** modular framework installed in `~/.gemini`. It consists of **3 component types** and supporting infrastructure:

| Component | Count | Purpose |
|-----------|-------|---------|
| **Rules** | 1 file | Persistent behavior (`GEMINI.md`) |
| **Workflows** | 14 | On-demand slash command procedures |
| **Skills** | 40+ | Auto-triggered knowledge modules |
| **Agents** | 14 | Specialist AI personas |

---

## 🏗️ 3 Component Types

### 1. Rules (Always Active)

- **File**: `~/.gemini/GEMINI.md`
- **Purpose**: Define how the agent always behaves — coding style, safety constraints, architecture patterns.
- **Scope**: Applied to ALL projects automatically.

### 2. Workflows (On-Demand Modes)

- **Path**: `~/.gemini/antigravity/global_workflows/*.md`
- **Purpose**: Define how the agent behaves temporarily, triggered via slash commands.
- **Activation**: `/plan`, `/review`, `/create`, `/debug`, etc.
- **Scope**: Global — available in all workspaces.

### 3. Skills (Auto-Triggered)

- **Path**: `~/.gemini/antigravity/skills/*/SKILL.md`
- **Purpose**: Specialized knowledge modules automatically invoked when relevant.
- **Activation**: Keyword matching via `registry.min.json`.
- **Scope**: Global — available in all workspaces.

---

## 📁 Directory Structure

All documentation uses `{FRAMEWORK_ROOT}` as a placeholder that resolves to `~/.gemini`.

```
{FRAMEWORK_ROOT}/                          (~/.gemini)
├── GEMINI.md                              ← Rules (always active, all projects)
├── ARCHITECTURE.md                        ← This file
├── registry.min.json                      ← Unified metadata index
│
├── core/                                  ← Core logic
│   ├── system_prompt.md                   ← Base persona & behaviors
│   ├── rules.md                           ← Operational rules (TIER 0)
│   ├── classifier.md                      ← Request type mapping
│   └── memory_rules.md                    ← Context & token efficiency
│
├── antigravity/                           ← Antigravity platform integration
│   ├── agents/                            ← 14 Specialist Agent definitions
│   │   ├── orchestrator.md
│   │   ├── frontend-specialist.md
│   │   ├── backend-specialist.md
│   │   └── ...
│
│
    ├── global_workflows/                  ← Workflows (slash commands)
    │   ├── brainstorm.md
    │   ├── plan.md
    │   ├── create.md
    │   ├── debug.md
    │   ├── deploy.md
    │   ├── enhance.md
    │   ├── init-context.md
    │   ├── orchestrate.md
    │   ├── restructure.md
    │   ├── review.md
    │   ├── status.md
    │   ├── test.md
    │   ├── deep-solve.md
    │   └── ux-ui-pro.md
    │
    └── skills/                            ← Skills (auto-trigger)
        ├── core/                          ← Core skills (8)
        ├── tech/                          ← Technology skills (16)
        ├── process/                       ← Process skills (16+)
        └── custom/                        ← Custom/user skills
```

---

## 📚 The "Librarian" Pattern

Prompt Base uses **Progressive Disclosure** to manage complexity. Skills remain dormant until activated.

1. **Discovery**: Orchestrator consults `registry.min.json`.
2. **Activation**: The system loads the specific `SKILL.md` required for the task.
3. **Execution**: The specialized agent performs the task.
4. **Pruning**: Knowledge is cleared after task completion to maintain context window efficiency.

---

## 🤖 Agents (14)

| Category            | Agents                                                                                             |
| ------------------- | -------------------------------------------------------------------------------------------------- |
| **Core**            | `orchestrator`, `project-planner`, `explorer-agent`                                                |
| **Dev**             | `frontend-specialist`, `backend-specialist`, `mobile-developer`                                    |
| **Quality**         | `test-engineer`, `debugger`, `performance-optimizer`, `documentation-writer`                       |
| **Infra/Sec**       | `devops-engineer`, `security-auditor`, `database-architect`                                        |
| **Growth & Search** | `seo-specialist`                                                                                   |

---

## 🧠 Skills (40+)

### Core (8)

| Skill                | Description               |
| -------------------- | ------------------------- |
| `coding-standards`         | Coding standards          |
| `brainstorming`      | Socratic discovery        |
| `plan-writing`       | Task breakdown            |
| `architecture`       | System design             |
| `skill-loading`      | JIT Knowledge discovery   |
| `context-management` | Context efficiency (MVC)  |
| `behavioral-modes`   | Operational personas      |
| `parallel-agents`    | Multi-perspective analysis|

### Technology (17)

| Category    | Skills                                                                              |
| ----------- | ----------------------------------------------------------------------------------- |
| **Web**     | `react-patterns`, `nextjs-best-practices`, `tailwind-patterns`, `typescript-expert` |
| **Backend** | `nodejs-best-practices`, `python-patterns`, `prisma-expert`, `nestjs-expert`, `golang-best-practices`, `api-patterns` |
| **Mobile**  | `mobile-design`                                                                     |
| **Other**   | `database-design`, `docker-expert`, `game-development`, `ux-ui-pro-max`, `mcp-builder`, `jupyter-notebooks` |

### Process (16+)

| Category    | Skills                                                                              |
| ----------- | ----------------------------------------------------------------------------------- |
| **Testing** | `testing-patterns`, `tdd-workflow`, `webapp-testing`, `lint-and-validate`           |
| **Security**| `vulnerability-scanner`, `red-team-tactics`, `red-teaming`                           |
| **Growth**  | `seo-fundamentals`, `geo-fundamentals`                                              |
| **Ops**     | `deployment-procedures`, `server-management`, `bash-linux`, `powershell-windows`    |
| **Meta**    | `code-review-checklist`, `documentation-templates`, `review-pre-commit-git`, `i18n-localization` |

---

## 🔄 Workflows (14)

| Command         | Description                   |
| --------------- | ----------------------------- |
| `/brainstorm`   | Socratic discovery            |
| `/create`       | Create new features           |
| `/debug`        | Debug issues                  |
| `/deploy`       | Deploy application            |
| `/enhance`      | Improve existing code         |
| `/orchestrate`  | Multi-agent coordination      |
| `/plan`         | Task breakdown                |
| `/status`       | Check project status          |
| `/test`         | Run tests                     |
| `/init-context` | Initialize MVC                |
| `/deep-solve`   | JIT Knowledge workflow        |
| `/restructure`  | Maintenance & registry update |
| `/review`       | Pre-commit audit              |
| `/ux-ui-pro`    | Design intelligence           |

---

## 📊 Statistics

| Metric              | Value |
| ------------------- | ----- |
| **Total Agents**    | 14    |
| **Total Skills**    | 41+   |
| **Total Workflows** | 14    |

---

## 🔗 Critical File Dependencies

| File | Depends On | Why? |
| ---- | ---------- | ---- |
| `{FRAMEWORK_ROOT}/registry.min.json` | All `.md` files in `{FRAMEWORK_ROOT}/antigravity/agents/` and `{FRAMEWORK_ROOT}/antigravity/skills/` | Source of truth for paths and descriptions. |
| `{FRAMEWORK_ROOT}/GEMINI.md` | `{FRAMEWORK_ROOT}/core/*.md` | Governance and rule enforcement. |
| `ARCHITECTURE.md` | `{FRAMEWORK_ROOT}/registry.min.json` | Statistics and module overview. |
| `README.md` | `ARCHITECTURE.md` | General project overview and setup. |

---

## 🔗 Quick Reference

| Need        | Agent                 | Category       |
| ----------- | --------------------- | -------------- |
| Web App     | `frontend-specialist` | UI/UX & Growth |
| API         | `backend-specialist`  | API & Logic    |
| Discovery   | `orchestrator`        | Orchestration  |
| Efficiency  | `orchestrator`        | Orchestration  |
| Quality     | `test-engineer`       | Quality        |
