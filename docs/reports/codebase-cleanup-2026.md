# Codebase Cleanup & Refactoring Report

## 1. Summary of Issues Found
The `prompt_base` framework is largely well-structured and relies on a clean markdown/JSON architecture. However, during the audit, several issues related to legacy developer scripts and obsolete documentation were identified:
- Presence of an outdated and duplicate registry generation script.
- Leftover planning documentation from previous feature implementations.
- Sub-agent reference folders (`antigravity/agents/*/references`) were audited and confirmed as correctly linked (not orphaned).
- Some Python utility scripts were verified against the skill definitions to ensure they are actively used by agents.

## 2. Files Removed
The following files were safely deleted as they constituted dead code or obsolete history:

- 🗑️ `scripts/minify_registry.py`
  - **Reason:** Duplicate logic. This file was an older, redundant version of `generate_registry.py` that used outdated keys (`i`, `d`, `p` instead of `id`, `description`, `path`) and targeted a legacy `.agents` directory. It was no longer referenced in the `Makefile`.
- 🗑️ `docs/PLAN-behavioral-rules.md`
  - **Reason:** Obsolete documentation. This was a temporary planning document used to track the integration of behavioral rules. Since the rules have successfully been merged into `core/rules.md` and `GEMINI.md`/`CLAUDE.md`, this file was simply cluttering the repository.

## 3. Duplicate Logic Detected & Resolved
- **Registry Generation:** The logic to generate a minified JSON registry was duplicated across `generate_registry.py` and `minify_registry.py`. By removing `minify_registry.py`, we enforce a Single Source of Truth in `generate_registry.py` (which correctly generates both the formatted and minified versions of `registry.min.json`).

## 4. Refactoring Recommendations
- **Python Utility Scripts (`code_graph.py`, `lint_runner.py`, `security_scan.py`, `ux_audit.py`):** These scripts are currently referenced by skills as placeholder execution commands for the LLM agents. As the framework evolves, consider moving these scripts into a dedicated `tools/` or `bin/` directory and ensuring they are copied over during `make install` if the agents are expected to execute them in the target environment (currently, `cleanup.sh` removes the `scripts` folder during installation).
- **Agent References:** Ensure that if new agents (like `test-engineer`) grow in complexity, their reference materials are also placed in structured `references/` directories (like `frontend-specialist`) and loaded via the `references:` YAML header to prevent token bloat in the main agent markdown file.

## 5. Final Status
✅ **Success.** The cleanup process preserved all business logic, API contracts, and framework behavior. The repository is now cleaner, DRYer, and free of legacy scripts.
