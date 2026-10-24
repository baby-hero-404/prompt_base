# Proposal: Support Codex CLI in Prompt Base

## 1. Context & Motivation
Codex CLI is an AI coding assistant terminal tool that natively supports:
1. **Global Skills**: Scanned automatically from `~/.codex/skills/<skill-name>/SKILL.md` and callable via `$skill-name` or `/skills`.
2. **Global Rules / Instructions**: Loaded automatically from `~/.codex/AGENTS.md`.

Prompt Base already supports Gemini (`~/.gemini`) and Claude Code (`~/.claude`). Adding native Codex CLI support enables developers to use Prompt Base's 50+ curated skills, standardized rules (R1-R11), and agent workflows seamlessly inside Codex CLI sessions across all projects without per-project reinstallation.

## 2. Key Decisions
- **Standardized Rules File (`AGENTS.md`)**: Introduce `AGENTS.md` in the Prompt Base repository root. It defines the layout for `~/.codex` and maintains 100% synchronized `## Rules` (R1-R11) with `GEMINI.md` and `CLAUDE.md`.
- **Target in Manifest**: Add `~/.codex` to `install.manifest.json` targets.
- **Makefile Integration**: Add `install-codex` target and include it in `make install`.
- **Integration & Audit Gates**: Update `scripts/test_integration.py` to assert rule sync across `GEMINI.md`, `CLAUDE.md`, and `AGENTS.md`, and update `scripts/checklist.py` and `scripts/cleanup.sh`.
- **Documentation**: Document Codex CLI setup, skill invocation (`$skill-name`), and layout in `README.md` and `ARCHITECTURE.md`.
