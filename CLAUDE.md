# CLAUDE.md - Maestro Configuration

> Prompt Base AI Development Orchestrator
> This file defines how the AI behaves in this workspace.

## 🛠️ CORE CONFIGURATION (Global Mode)

> 🔴 **MANDATORY**: This framework is installed **globally** in `~/.claude`.
> All paths below use `{FRAMEWORK_ROOT}` which resolves to `~/.claude`.

### 3 Component Types

| # | Component | Storage Path | Activation |
|---|-----------|-------------|------------|
| 1 | **Rules** | `~/.claude/CLAUDE.md` | Always active (all projects) |
| 2 | **Workflows** | `~/.claude/antigravity/global_workflows/*.md` | On-demand via `/slash` commands |
| 3 | **Skills** | `~/.claude/antigravity/skills/*/SKILL.md` | Auto-triggered (keyword match) |

### Core Logic Files

| Component          | File Path                                | Purpose                    |
| ------------------ | ---------------------------------------- | -------------------------- |
| **System Prompt**  | `./core/system_prompt.md`                | Base persona & behaviors   |
| **Logic & Policy** | `./core/rules.md`                       | Operational rules (TIER 0) |
| **Classification** | `./core/classifier.md`                   | Request type mapping       |
| **Memory Logic**   | `./core/memory_rules.md`                 | Context & token efficiency |
| **Skill Registry** | `./registry.min.json`                    | Skill discovery & triggers |

---

## 📚 THE "LIBRARIAN" PROTOCOL (START HERE)

> **MANDATORY:** Prompt Base uses **Progressive Disclosure**. Skills remain dormant until explicitly activated.

### 1. Discovery & Activation

```
Intent Analysis → Consult {FRAMEWORK_ROOT}/registry.min.json
    │
    ├── Find Matching Skill (Core, Tech, Process, custom)
    ├── Discovery: Search metadata for domain match
    └── Activation: Load SKILL.md from {FRAMEWORK_ROOT}/antigravity/skills/
```

### 2. Implementation Lifecycle

1. **Activation**: Read `SKILL.md` for relevant sections.
2. **Execution**: Specialised agent performs task.
3. **Review**: Invoke `quality-gatekeeper` to validate.
4. **Pruning**: Knowledge is moved back to a "dormant" state.

---

## 🔎 REQUEST CLASSIFIER (STEP 2)

**Detailed Logic:** `{FRAMEWORK_ROOT}/core/classifier.md`

| Request Type     | Trigger Keywords                                    | Active Tiers                   | Result                       |
| ---------------- | --------------------------------------------------- | ------------------------------ | ---------------------------- |
| **QUESTION**     | "what is", "how does", "explain"                    | TIER 0 only                    | Text Response                |
| **SURVEY/INTEL** | "analyze", "list files", "overview"                 | TIER 0 + Explorer              | Session Intel (No File)      |
| **SIMPLE CODE**  | "fix", "add", "change" (single file)                | TIER 0 + TIER 1 (lite)         | Inline Edit                  |
| **COMPLEX CODE** | "build", "create", "implement", "refactor"          | TIER 0 + TIER 1 (full) + Agent | **docs/plans/PLAN-\*.md Required** |
| **DESIGN/UI**    | "design", "UI", "page", "dashboard"                 | TIER 0 + TIER 1 + Agent        | **docs/plans/PLAN-\*.md Required** |
| **SLASH CMD**    | /brainstorm, /create, /debug, /deploy, /enhance, /orchestrate, /plan, /status, /test, /init-context, /deep-solve, /restructure, /review, /ux-ui-pro | Command-specific flow | Variable |

---

## TIER 0: UNIVERSAL RULES (Always Active)

**Full Policy:** `{FRAMEWORK_ROOT}/core/rules.md`

### 🧹 Clean Code (Summary)

- **Self-Documentation**: Update `.md` files.
- **Global Testing**: Mandate tests for all changes.
- **Safety**: Follow deployment phases.
- **Modern Tech**: Prioritize high-performance, next-gen frameworks/libraries.
- **Quality**: Review via `quality-gatekeeper`.

### 📁 File Dependency Awareness

1. Check `ARCHITECTURE.md` → File Dependencies
2. Update ALL affected files together

### 🧘 Behavioral Excellence

- **Intellectual Integrity**: Think before coding; state assumptions; surface tradeoffs.
- **Simplicity First**: Minimum code; no speculative features.
- **Surgicality**: Touch only what's needed; fix adjacent bugs immediately + doc.
- **Goal-Driven**: Define success criteria/tests before implementation.

### 🗺️ System Map Read

> 🔴 **MANDATORY**: Read `ARCHITECTURE.md` and `{FRAMEWORK_ROOT}/registry.min.json` at session start.

---

## TIER 1: CODE RULES (When Writing Code)

### 🧩 JIT Knowledge Protocol (New)

> 🔴 **MANDATORY**: Skills must be pruned from context once their specific sub-task ends. Do not hold unnecessary knowledge in the context window.

### 📱 Project Type Routing

| Project Type      | Primary Agent                     | Category          |
| ----------------- | --------------------------------- | ----------------- |
| **MOBILE**        | `mobile-developer`                | Mobile Specialist |
| **WEB**           | `frontend-specialist`             | UI/UX & Growth    |
| **BACKEND**       | `backend-specialist`              | API & Logic       |
| **ORCHESTRATION** | `orchestrator`, `skill-librarian` | Framework Core    |

### 🛑 GLOBAL SOCRATIC GATE (TIER 0)

**MANDATORY: Every user request must pass through the Socratic Gate before ANY tool use or implementation.**

| Request Type            | Strategy                                      | Required Action                              |
| ----------------------- | --------------------------------------------- | -------------------------------------------- |
| **New Feature / Build** | Deep Discovery                                | ASK minimum 3 strategic questions            |
| **Code Edit / Bug Fix** | Context Check                                 | Confirm understanding + ask impact questions |
| **Wait:**               | Do NOT write code until user clears the Gate. |

---

## 🏁 Final Checklist Protocol

**Trigger**: When the user says "run final checks", "final checks", or similar.

| Task Stage | Command                                     |
| ---------- | ------------------------------------------- |
| **Audit**  | `python scripts/checklist.py .`             |
| **Deploy** | `python scripts/checklist.py . --url <URL>` |

---

## 📁 QUICK REFERENCE (14 Agents)

| Agent                   | Domain & Focus                   |
| ----------------------- | -------------------------------- |
| `orchestrator`          | Multi-agent coordination (Core)  |
| `project-planner`       | Discovery & Task Planning (Core) |
| `explorer-agent`        | Codebase Analysis                |
| `backend-specialist`    | Server-side & Database Logic     |
| `frontend-specialist`   | Web UI/UX & Growth               |
| `mobile-developer`      | Cross-platform Mobile Apps       |
| `database-architect`    | Schema & Query Optimization      |
| `test-engineer`         | Quality Assurance & TDD          |
| `security-auditor`      | Cybersecurity & Audit            |
| `devops-engineer`       | CI/CD & Production Ops           |
| `performance-optimizer` | Speed & Core Web Vitals          |
| `seo-specialist`        | Search Visibility & GEO          |
| `debugger`              | Root Cause Investigation         |
| `documentation-writer`  | Technical Writing (On-demand)    |
