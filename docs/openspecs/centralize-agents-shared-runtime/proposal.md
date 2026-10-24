# Proposal: Centralize Shared Runtime, Memory & Trust under `~/.agents`

## 1. Context & Motivation
Previously, Prompt Base managed tools, trust lists, and memory stores separately across individual agent directories (`~/.gemini/`, `~/.claude/`, and `~/.codex/`):
- Memory stores were split between `~/.gemini/prompt_base_memory` and `~/.claude/prompt_base_memory`.
- Trust files were maintained as `~/.gemini/prompt_base_trusted.txt` and `~/.claude/prompt_base_trusted.txt`.
- Tools and Python virtual environments were duplicated across `~/.gemini/` and `~/.claude/`.
- The `/init-memory` workflow required manual permission asking before adding a project to trust.

This caused fragmentations, duplication of heavy venv dependencies, and context drift across different AI assistants.

## 2. Key Decisions
1. **Centralized Runtime Directory (`~/.agents`)**:
   - `~/.agents/tools/`: Canonical home for all agent utilities (`pb_trust.py`, `verify_gate.py`, `memory_*.py`).
   - `~/.agents/prompt_base_trusted.txt`: Unified trust registry for all AI tools.
   - `~/.agents/prompt_base_memory/`: Canonical global memory store for all project ADRs/graphs. Old project memory directories are ignored and a clean start is established.
   - `~/.agents/venv/`: Single shared virtual environment for memory engine dependencies (`fastembed`, `sqlite-vec`).
2. **Backward-Compatible Symlinks**:
   - Symlink `~/.gemini/tools`, `~/.claude/tools`, and `~/.codex/tools` to `~/.agents/tools` to prevent breaking existing scripts or custom aliases.
3. **Auto-Trust in `/init-memory`**:
   - Streamline `global_workflows/init-memory.md` to automatically execute `python3 ~/.agents/tools/pb_trust.py --add .` when initializing memory, immediately enabling automated hooks and verify gates.
4. **Unified Hook Configurations**:
   - Update `settings.json` (Claude) and `hooks.gemini.json` (Gemini) to execute tools from `~/.agents/tools/` using `~/.agents/venv/`.
