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
install-gemini:
	@echo "Installing to ~/.gemini..."
	@mkdir -p ~/.gemini
	@rm -rf ~/.gemini/core ~/.gemini/tools ~/.gemini/antigravity/agents ~/.gemini/antigravity/skills ~/.gemini/antigravity/global_workflows
	@cp -r ./* ~/.gemini/
	@rm -f ~/.gemini/CLAUDE.md
	@bash ~/.gemini/scripts/cleanup.sh ~/.gemini
	@echo "Gemini Install complete."

# Install/Update locally to ~/.claude
install-claude:
	@echo "Installing to ~/.claude..."
	@mkdir -p ~/.claude/skills ~/.claude/commands
	@rm -rf ~/.claude/core ~/.claude/tools ~/.claude/antigravity/agents ~/.claude/antigravity/skills ~/.claude/antigravity/global_workflows
	@cp -r ./* ~/.claude/
	@rm -f ~/.claude/GEMINI.md
	@find ~/.claude/skills -maxdepth 1 -type l ! -exec test -e {} \; -delete
	@find ~/.claude/commands -maxdepth 1 -type l ! -exec test -e {} \; -delete
	@find ~/.claude/antigravity/skills -mindepth 2 -maxdepth 2 -type d -exec ln -snf {} ~/.claude/skills/ \;
	@find ~/.claude/antigravity/global_workflows -maxdepth 1 -name "*.md" -exec ln -snf {} ~/.claude/commands/ \;
	@bash ~/.claude/scripts/cleanup.sh ~/.claude
	@echo "Claude Install complete."

# Install for both
install: install-gemini install-claude
