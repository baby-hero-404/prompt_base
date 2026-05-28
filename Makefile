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

# Install/Update locally to ~/.gemini
install:
	@echo "Installing to ~/.gemini..."
	@mkdir -p ~/.gemini
	@cp -r ./* ~/.gemini/
	@bash ~/.gemini/scripts/cleanup.sh
	@echo "Install complete."
