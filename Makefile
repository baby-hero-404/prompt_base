# Prompt Base - Global Mode
# Supported: Antigravity 2.x, Claude Code, Codex CLI

# Audit project structure
audit:
	@python3 scripts/checklist.py .

# Run integration tests
test:
	@python3 scripts/test_integration.py

# Full gate used by the Stop hook (R11): structure audit, tests, skill gates, memory freshness
verify: audit test skill-check memory-stale

# Regenerate registry.min.json from all SKILL.md files
registry:
	@python3 scripts/skill_lint.py --pre-gen
	@python3 scripts/generate_registry.py
	@python3 scripts/skill_lint.py

# Scaffold a new skill: make new-skill NAME=my-skill DESCRIPTION="..."
new-skill:
	@python3 scripts/create_skill.py "$(NAME)" --description "$(DESCRIPTION)"

# Run skill gates
skill-check:
	@if [ -z "$(SKILL)" ]; then \
		echo "Running Tier 1 (Lint) for all skills..."; \
		python3 scripts/skill_lint.py; \
		echo "Running Tier 2 (Trigger Test)..."; \
		python3 scripts/trigger_test.py; \
		echo "Running Tier 0 (Contract)..."; \
		python3 scripts/skill_contract.py; \
	else \
		echo "Running Tier 1 (Lint) for $(SKILL)..."; \
		python3 scripts/skill_lint.py; \
		echo "Running Tier 2 (Trigger Test)..."; \
		python3 scripts/trigger_test.py; \
		echo "Running Tier 0 (Contract)..."; \
		python3 scripts/skill_contract.py; \
		echo "Please run make skill-eval SKILL=$(SKILL) if eval: required."; \
	fi

skill-eval:
	@if [ -z "$(SKILL)" ]; then echo "SKILL required"; exit 1; fi
	@if [ -n "$(PROMPT)" ]; then \
		python3 scripts/golden_eval.py $(SKILL) --prompt "$(PROMPT)"; \
	else \
		python3 scripts/golden_eval.py $(SKILL); \
	fi

eval-all:
	@echo "Running evaluation for all skills in evals/golden/..."
	@for skill_dir in evals/golden/*/; do \
		skill_name=$$(basename "$$skill_dir"); \
		if [ "$$skill_name" != "fixtures" ]; then \
			echo "======================================"; \
			echo "Evaluating $$skill_name"; \
			echo "======================================"; \
			python3 scripts/golden_eval.py "$$skill_name" || exit 1; \
		fi \
	done

# Install/Update shared runtime locally to ~/.agents
# Canonical home for shared tools, trust list, and memory store across all agents.
install-agents:
	@echo "Installing shared runtime to ~/.agents..."
	@mkdir -p ~/.agents/tools ~/.agents/prompt_base_memory
	@cp -f tools/*.py ~/.agents/tools/
	@echo "Shared ~/.agents runtime complete."

# Install/Update locally to ~/.gemini
# NOTE: context-memory-engine hooks are intentionally NOT registered here.
# Gemini's hook stdin schema is unverified
# (adapter unverified, Task 3.4) - registering blind would risk misparsing a payload we've never seen.
# A pre-existing ~/.gemini/settings.json is backed up/restored around the copy step
# so this install never clobbers a user's own settings.
install-gemini: install-agents
	@echo "Installing to ~/.gemini..."
	@mkdir -p ~/.gemini/config
	@rm -rf ~/.gemini/tools ~/.gemini/agents ~/.gemini/skills ~/.gemini/global_workflows ~/.gemini/config/skills ~/.gemini/config/global_workflows
	@if [ -f ~/.gemini/settings.json ]; then cp ~/.gemini/settings.json ~/.gemini/.pb_settings_backup.json; fi
	@python3 scripts/install_manifest.py ~/.gemini
	@mv ~/.gemini/skills ~/.gemini/config/skills
	@mv ~/.gemini/global_workflows ~/.gemini/config/global_workflows
	@if [ -f ~/.gemini/.pb_settings_backup.json ]; then mv ~/.gemini/.pb_settings_backup.json ~/.gemini/settings.json; else rm -f ~/.gemini/settings.json; fi
	@rm -f ~/.gemini/CLAUDE.md ~/.gemini/AGENTS.md
	@rm -rf ~/.gemini/tools
	@ln -sfn ~/.agents/tools ~/.gemini/tools
	@bash scripts/cleanup.sh ~/.gemini
	@python3 scripts/install_gemini_hooks.py --source hooks.gemini.json --dest ~/.gemini/config/hooks.json
	@echo "Gemini Install complete."

# Install/Update locally to ~/.claude
# A pre-existing ~/.claude/settings.json is backed up before the blanket copy (which
# would otherwise overwrite it with this repo's tracked settings.json) and restored
# right after, so scripts/install_settings.py can safely MERGE our hook entries into
# the user's real prior settings instead of destroying them.
install-claude: install-agents
	@echo "Installing to ~/.claude..."
	@mkdir -p ~/.claude/skills ~/.claude/commands
	@rm -rf ~/.claude/tools ~/.claude/agents ~/.claude/skills ~/.claude/global_workflows
	@if [ -f ~/.claude/settings.json ]; then cp ~/.claude/settings.json ~/.claude/.pb_settings_backup.json; fi
	@python3 scripts/install_manifest.py ~/.claude
	@if [ -f ~/.claude/.pb_settings_backup.json ]; then mv ~/.claude/.pb_settings_backup.json ~/.claude/settings.json; else rm -f ~/.claude/settings.json; fi
	@python3 scripts/install_settings.py --source settings.json --dest ~/.claude/settings.json
	@rm -f ~/.claude/GEMINI.md ~/.claude/AGENTS.md
	@rm -rf ~/.claude/tools
	@ln -sfn ~/.agents/tools ~/.claude/tools
	@find ~/.claude/commands -maxdepth 1 -type l ! -exec test -e {} \; -delete
	@find ~/.claude/global_workflows -maxdepth 1 -name "*.md" -exec ln -snf {} ~/.claude/commands/ \;
	@bash scripts/cleanup.sh ~/.claude
	@echo "Claude Install complete."

# Install/Update locally to ~/.codex
# Global Skills will be available at ~/.codex/skills/ and callable via $skill-name or /skills.
# Global rules are placed at ~/.codex/AGENTS.md.
install-codex: install-agents
	@echo "Installing to ~/.codex..."
	@mkdir -p ~/.codex/skills
	@rm -rf ~/.codex/tools ~/.codex/agents ~/.codex/skills ~/.codex/global_workflows
	@python3 scripts/install_manifest.py ~/.codex
	@rm -f ~/.codex/GEMINI.md ~/.codex/CLAUDE.md
	@rm -rf ~/.codex/tools
	@ln -sfn ~/.agents/tools ~/.codex/tools
	@bash scripts/cleanup.sh ~/.codex
	@echo "Codex Install complete."

# Install for all supported assistants
install: install-agents install-gemini install-claude install-codex

# --- Context memory engine (opt-in) ---

# Build isolated venvs for the memory engine's heavy deps (fastembed/onnxruntime,
# sqlite-vec) - never installed into the user's global Python - then calibrate the
# recall latency budget against this checkout. A real project's own calibration
# normally happens automatically on that project's first PreCompact run instead;
# this is for setup/dev use. Idempotent: safe to re-run.
memory-setup:
	@[ -d ~/.agents/venv ] || python3 -m venv ~/.agents/venv
	@~/.agents/venv/bin/pip install --quiet --upgrade pip
	@~/.agents/venv/bin/pip install --quiet -r requirements.txt
	@$(MAKE) memory-bench
	@echo "memory-setup complete."

# Agent-neutral Python runner: prefers ~/.agents/venv, then legacy venvs, fallback to python3
PY_VENV := $(shell if [ -x ~/.agents/venv/bin/python ]; then echo ~/.agents/venv/bin/python; elif [ -x ~/.gemini/venv/bin/python ]; then echo ~/.gemini/venv/bin/python; elif [ -x ~/.claude/venv/bin/python ]; then echo ~/.claude/venv/bin/python; elif [ -x ~/.codex/venv/bin/python ]; then echo ~/.codex/venv/bin/python; else echo python3; fi)

# Force a fresh cold-start latency measurement for the current project.
memory-bench:
	@$(PY_VENV) tools/memory_bench.py --root .

# Create an empty, schema-correct .ai-memory/memory.db for the current project.
memory-init:
	@python3 tools/memory_init.py --root .

# Read-only report: docs/ai state, this agent's derived index, leftover index dirs.
memory-status:
	@$(PY_VENV) tools/memory_status.py --root .

# Is docs/ai project memory stale? (exit 1 when an autoRefreshTriggers file changed)
memory-stale:
	@python3 tools/memory_stale.py --root .

# Rebuild the derived index from docs/ai/adr/ + docs/ai/archive/ markdown.
memory-rebuild:
	@$(PY_VENV) tools/memory_rebuild.py --root .

# Trust current project for automated hooks (verify gate, memory recall/invariants)
trust:
	@python3 tools/pb_trust.py --add .
	@echo "Project trusted for automated hooks."

# Remove current project from trust list
untrust:
	@python3 tools/pb_trust.py --remove .
	@echo "Project removed from trust list."

clone-references: ## Clone external test/skill references
	@echo "==> Cloning external references..."
	bash scripts/clone_references.sh

test-explore-codebase:
	@$(MAKE) skill-eval SKILL=explore-codebase
