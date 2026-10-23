# Project Profile

## Identity
- **Project Name:** Prompt Base (`my_projects-prompt_base`)
- **Type:** Modular AI development framework & agentic infrastructure (Global-first architecture installed in `~/.gemini` and `~/.claude`; project memory is agent-neutral markdown in `docs/ai/`).
- **Primary Languages:** Python 3, Markdown, Shell/Bash, GNU Makefile.

## Architecture
**Key Components:**
- **Rules (`GEMINI.md` / `CLAUDE.md`):** Persistent, self-contained rule governance loaded into every session (Classifier, Socratic gate, Supply chain security, Code hygiene).
- **Workflows (`global_workflows/`):** 16 on-demand operational modes triggered via slash commands (`/plan`, `/review`, `/create`, `/create-skill`, `/debug`, `/init-context`, `/init-memory`, etc.).
- **Skills (`skills/`):** 58 auto-triggered domain knowledge modules categorized into Core, Tech, Process, and Custom, loaded via progressive disclosure.
- **Agents (`agents/`):** 14 specialist personas (e.g. `orchestrator`, `project-planner`, `frontend-specialist`, `backend-specialist`, `test-engineer`, `security-auditor`).
- **Registry (`registry.min.json`):** Unified, minified discovery index for zero-cost discovery.
- **5-Tier Quality Gate Pipeline:** Tier 1 Lint (`skill_lint.py`), Tier 2 Trigger test (`trigger_test.py`), Tier 0 Contract (`skill_contract.py`), Tier 3 Golden Eval (`golden_eval.py`), Tier 4 Journal (`skill-feedback.md`).
- **Context Memory Engine:** Opt-in long-term memory tier for ADR extraction via `PreCompact` hooks and semantic recall via `UserPromptSubmit` hooks (`tools/`, `scripts/`).
- **Manifest Installation System:** Manifest-driven installation (`install.manifest.json`, `scripts/install_manifest.py`, `scripts/install_settings.py`, `scripts/cleanup.sh`) ensuring non-destructive syncing to `~/.gemini` and `~/.claude`.

## Tech Stack
- Frontend: Markdown, JSON, YAML frontmatter
- Backend / Tooling: Python 3 (stdlib preferred for installers and linters), GNU Make, Bash
- Quality & Testing: Python `unittest`, custom lint and contract verification scripts, fastembed / sqlite-vec (for memory engine)
- Infra / Distribution: Git, Manifest-based file synchronization to `~/.gemini` and `~/.claude`

## Repository Map
- `GEMINI.md` / `CLAUDE.md`: Global rule definitions and security constraints
- `ARCHITECTURE.md`: Master architecture specification and file dependency matrix
- `registry.min.json`: Unified discovery index of all skills, agents, and workflows
- `agents/`: 14 Specialist agent definitions
- `global_workflows/`: On-demand slash command workflow procedures
- `skills/`: Auto-triggered knowledge modules
- `scripts/`: Automation scripts (linters, registry generator, installer, triggers)
- `tools/`: Context memory engine scripts (memory init, bench, rebuild)
- `docs/`: Documentation, skills guide, quality gates summary, evaluation reports
- `evals/`: Golden eval datasets and test fixtures
- `projects/`: Project profile templates and examples
- `Makefile`: Centralized automation targets (`install`, `install-gemini`, `install-claude`, `audit`, `test`, `registry`, `new-skill`, `skill-check`, `skill-eval`, `eval-all`, `memory-setup`, `memory-init`, `memory-rebuild`)
