# Prompt Base - Global Mode
# Supported: Antigravity

# Audit project structure
audit:
	@python3 scripts/checklist.py .

# Run integration tests
test:
	@python3 scripts/test_integration.py

# Regenerate registry.min.json from all SKILL.md files
registry:
	@python3 scripts/generate_registry.py

# Scaffold a new skill: make new-skill NAME=my-skill CATEGORY=tech DESCRIPTION="..."
CATEGORY ?= custom
new-skill:
	@python3 scripts/create_skill.py "$(NAME)" --category "$(CATEGORY)" --description "$(DESCRIPTION)"

# Install/Update locally to ~/.gemini
# NOTE: context-memory-engine hooks are intentionally NOT registered here.
# Gemini's hook stdin schema is unverified (see docs/openspecs/context-memory-engine-2026,
# Task 3.4) - registering blind would risk misparsing a payload we've never seen.
# A pre-existing ~/.gemini/settings.json is backed up/restored around the copy step
# so this install never clobbers a user's own settings.
install-gemini:
	@echo "Installing to ~/.gemini..."
	@mkdir -p ~/.gemini
	@rm -rf ~/.gemini/core ~/.gemini/tools ~/.gemini/antigravity/agents ~/.gemini/antigravity/skills ~/.gemini/antigravity/global_workflows
	@if [ -f ~/.gemini/settings.json ]; then cp ~/.gemini/settings.json ~/.gemini/.pb_settings_backup.json; fi
	@cp -r ./* ~/.gemini/
	@if [ -f ~/.gemini/.pb_settings_backup.json ]; then mv ~/.gemini/.pb_settings_backup.json ~/.gemini/settings.json; else rm -f ~/.gemini/settings.json; fi
	@rm -f ~/.gemini/CLAUDE.md
	@bash ~/.gemini/scripts/cleanup.sh ~/.gemini
	@echo "NOTE: context-memory-engine hooks are NOT registered for Gemini yet (adapter unverified, Task 3.4)."
	@echo "      Use 'make memory-rebuild' + degraded/FTS5 recall manually until that lands."
	@echo "Gemini Install complete."

# Install/Update locally to ~/.claude
# A pre-existing ~/.claude/settings.json is backed up before the blanket copy (which
# would otherwise overwrite it with this repo's tracked settings.json) and restored
# right after, so scripts/install_settings.py can safely MERGE our hook entries into
# the user's real prior settings instead of destroying them.
install-claude:
	@echo "Installing to ~/.claude..."
	@mkdir -p ~/.claude/skills ~/.claude/commands
	@rm -rf ~/.claude/core ~/.claude/tools ~/.claude/antigravity/agents ~/.claude/antigravity/skills ~/.claude/antigravity/global_workflows
	@if [ -f ~/.claude/settings.json ]; then cp ~/.claude/settings.json ~/.claude/.pb_settings_backup.json; fi
	@cp -r ./* ~/.claude/
	@if [ -f ~/.claude/.pb_settings_backup.json ]; then mv ~/.claude/.pb_settings_backup.json ~/.claude/settings.json; else rm -f ~/.claude/settings.json; fi
	@python3 scripts/install_settings.py --source settings.json --dest ~/.claude/settings.json
	@rm -f ~/.claude/GEMINI.md
	@find ~/.claude/skills -maxdepth 1 -type l ! -exec test -e {} \; -delete
	@find ~/.claude/commands -maxdepth 1 -type l ! -exec test -e {} \; -delete
	@find ~/.claude/antigravity/skills -mindepth 2 -maxdepth 2 -type d -exec ln -snf {} ~/.claude/skills/ \;
	@find ~/.claude/antigravity/global_workflows -maxdepth 1 -name "*.md" -exec ln -snf {} ~/.claude/commands/ \;
	@bash ~/.claude/scripts/cleanup.sh ~/.claude
	@echo "Claude Install complete."

# Install for both
install: install-gemini install-claude

# --- Context memory engine (opt-in; see docs/openspecs/context-memory-engine-2026) ---

# Build isolated venvs for the memory engine's heavy deps (fastembed/onnxruntime,
# sqlite-vec) - never installed into the user's global Python - then calibrate the
# recall latency budget against this checkout. A real project's own calibration
# normally happens automatically on that project's first PreCompact run instead;
# this is for setup/dev use. Idempotent: safe to re-run.
memory-setup:
	@[ -d ~/.claude/venv ] || python3 -m venv ~/.claude/venv
	@~/.claude/venv/bin/pip install --quiet --upgrade pip
	@~/.claude/venv/bin/pip install --quiet -r requirements.txt
	@[ -d ~/.gemini/venv ] || python3 -m venv ~/.gemini/venv
	@~/.gemini/venv/bin/pip install --quiet --upgrade pip
	@~/.gemini/venv/bin/pip install --quiet -r requirements.txt
	@$(MAKE) memory-bench
	@echo "memory-setup complete."

# Force a fresh cold-start latency measurement for the current project.
memory-bench:
	@if [ -x ~/.claude/venv/bin/python ]; then ~/.claude/venv/bin/python tools/memory_bench.py --root .; else python3 tools/memory_bench.py --root .; fi

# Create an empty, schema-correct .ai-memory/memory.db for the current project.
memory-init:
	@python3 tools/memory_init.py --root .

# Rebuild the derived index from docs/ai/adr/ + docs/ai/archive/ markdown.
memory-rebuild:
	@python3 tools/memory_rebuild.py --root .

clone-references: ## Clone external test/skill references
	@echo "==> Cloning external references..."
	bash scripts/clone_references.sh
