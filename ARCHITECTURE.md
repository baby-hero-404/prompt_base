# Prompt Base Architecture

## 📋 Overview

Prompt Base is a **global-only** modular framework installed in `~/.gemini`. It consists of **3 component types** and supporting infrastructure:

| Component | Count | Purpose |
|-----------|-------|---------|
| **Rules** | 1 file | Persistent behavior (`GEMINI.md`) |
| **Workflows** | 14 | On-demand slash command procedures |
| **Skills** | 50+ | Auto-triggered knowledge modules |
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

## 📦 Installation & Distribution (Manifest Flow)

Prompt Base is installed globally to `~/.gemini` and `~/.claude` using a strict, manifest-driven flow to prevent workspace clutter:

1. **`install.manifest.json`**: Defines the targets, inclusion globs (`*`), and strict exclusions (`docs/`, `scripts/`, `.git*`, `Makefile`, etc.).
2. **`scripts/install_manifest.py`**: A zero-dependency Python script that reads the manifest and performs a filtered file copy. It safely overwrites read-only destinations and prunes excluded files during traversal.
3. **`make install`**: Triggers the python script for all targets and runs post-install assertions to guarantee `registry.min.json` and core directories were copied successfully.

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

### Process (27)

| Category    | Skills                                                                              |
| ----------- | ----------------------------------------------------------------------------------- |
| **Testing** | `testing-patterns`, `tdd-workflow`, `webapp-testing`, `lint-and-validate`, `verification-before-completion` |
| **Security**| `vulnerability-scanner`, `red-team-tactics`, `red-teaming`                           |
| **Growth**  | `seo-fundamentals`, `geo-fundamentals`                                              |
| **Ops**     | `deployment-procedures`, `server-management`, `bash-linux`, `powershell-windows`    |
| **Meta & Dev**| `code-review-checklist`, `documentation-templates`, `review-pre-commit-git`, `i18n-localization`, `openspec-authoring`, `subagent-driven-development`, `receiving-code-review`, `codebase-cleanup`, `readme-generator`, `code-graph-analysis`, `performance-profiling`, `frontend-design`, `systematic-debugging` |

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

## 🚦 Recommended Flows by Use Case

Choose the right command pipeline based on what you need to accomplish. Each flow is designed to keep context lean and results precise.

### Quick Fix (Low Complexity)

> **Use when:** Fixing a known bug, typo, or making a small isolated change.

```
Describe the fix → Edit directly → /test
```

No plan or spec needed. The agent applies the Socratic Gate lightly (confirms understanding), makes surgical edits, and runs tests.

### New Feature or Refactoring (Medium–High Complexity)

> **Use when:** Adding a new module, refactoring existing architecture, or implementing a multi-file change.

```
/plan → [openspec-authoring] → /create or /enhance → /review
```

1. `/plan` generates a high-level roadmap (`docs/plans/PLAN-YYYYMMDD-{slug}.md`) with phases and agent assignments.
2. The `openspec-authoring` skill decomposes the approved plan into 4 specification files (`docs/openspecs/{task}/`: proposal, specs, design, tasks).
3. `/create` or `/enhance` implements the tasks defined in the spec set.
4. `/review` performs a pre-commit quality check before merging.

### New Application (High Complexity)

> **Use when:** Building a project from scratch (e.g., SaaS dashboard, e-commerce app).

```
/brainstorm → /plan → /ux-ui-pro → [openspec-authoring] → /create
```

1. `/brainstorm` explores approaches, tech stack options, and trade-offs.
2. `/plan` maps out the architecture and milestones.
3. `/ux-ui-pro` generates a professional design system and UI foundation.
4. `openspec-authoring` writes the execution contract (the 4 spec files).
5. `/create` scaffolds and implements the full application with multi-agent coordination.

### Debugging & Troubleshooting (Variable Complexity)

> **Use when:** Investigating errors, crashes, or unexpected behavior.

```
/debug → /test → Fix → /review
```

1. `/debug` activates systematic investigation: gathers error context, forms hypotheses, tests each one.
2. `/test` creates a reproducing test case to confirm root cause.
3. The agent applies a surgical fix and explains the root cause.
4. `/review` validates the fix before commit.

### Pre-Commit Quality Gate

> **Use when:** About to commit or push changes. Works at any complexity level.

```
/review
```

Runs the `review-pre-commit-git` skill to audit staged changes against coding standards, test coverage, and security checklist.

### Extending Prompt Base Itself

> **Use when:** Adding new skills, agents, or workflows to this framework.

```
Create SKILL.md → Register in registry.min.json → make audit
```

1. Create the skill directory and `SKILL.md` following the [Skills Guide](docs/skills-guide.md).
2. Add the entry to `registry.min.json`.
3. Run `make audit` to validate structural consistency across the framework.

---

## 📊 Statistics

| Metric              | Value |
| ------------------- | ----- |
| **Total Agents**    | 14    |
| **Total Skills**    | 54    |
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

## Skill Quality Gates

Prompt Base implements a 5-Tier Verification Pipeline for skills:
1. **Tier 1 (Linter)**: Syntax and metadata validation (`scripts/skill_lint.py`)
2. **Tier 2 (Trigger)**: Precision/Recall testing for keyword triggers (`scripts/trigger_test.py`)
3. **Tier 0 (Contract)**: Static analysis for path/tool/skill references (`scripts/skill_contract.py`)
4. **Tier 3 (Golden Eval)**: LLM-as-judge regression testing (`scripts/golden_eval.py`)
5. **Tier 4 (Journal)**: Human-in-the-loop rollback tracking (`docs/reports/skill-feedback.md`)

Workflow: Edit -> `make skill-check` -> `make skill-eval` -> Merge -> Journal.
