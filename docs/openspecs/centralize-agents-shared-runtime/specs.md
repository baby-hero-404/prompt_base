# Specification: Centralized `~/.agents` Runtime & Memory Architecture

## 1. Directory Structure

```text
~/.agents/
├── tools/                      ← Canonical shared utilities
│   ├── pb_trust.py
│   ├── verify_gate.py
│   ├── memory_engine.py
│   ├── memory_compact.py
│   ├── memory_recall.py
│   ├── memory_invariants.py
│   ├── memory_status.py
│   └── ...
├── prompt_base_trusted.txt     ← Unified user-local trust list
├── prompt_base_memory/         ← Canonical multi-agent project memories
│   └── <project_name>-<hash>/
│       └── memory.db
└── venv/                       ← Unified virtualenv for memory dependencies
```

## 2. Component Contracts

### 2.1 Memory Engine (`tools/memory_engine.py`)
- `get_memory_dir(root: str) -> Path`:
  - Primary directory: `Path("~/.agents/prompt_base_memory").expanduser() / folder_name`
  - Ignores legacy project memory paths in `~/.claude/prompt_base_memory` and `~/.gemini/prompt_base_memory`.
  - Maintains `PB_LOCAL_MEMORY` and `PB_GLOBAL_MEMORY_DIR` environment overrides.

### 2.2 Trust Manager (`tools/pb_trust.py`)
- Primary trust file: `~/.agents/prompt_base_trusted.txt`
- Read fallback: checks `~/.agents/prompt_base_trusted.txt`, plus `~/.gemini/prompt_base_trusted.txt` / `~/.claude/prompt_base_trusted.txt` if they exist.
- Write target: always writes `--add` / `--remove` to `~/.agents/prompt_base_trusted.txt`.

### 2.3 Hooks (`settings.json` & `hooks.gemini.json`)
- Command pattern:
  `PY="$HOME/.agents/venv/bin/python"; [ -x "$PY" ] || PY=python3; "$PY" "$HOME/.agents/tools/<tool>.py"`

### 2.4 Workflow `/init-memory` (`global_workflows/init-memory.md`)
- Replaces manual permission prompt in Step 4 with direct auto-activation:
  `python3 ~/.agents/tools/pb_trust.py --add .`
- References all tools as `~/.agents/tools/<tool>.py`.

### 2.5 Makefile & Distribution
- New target `install-agents`: sets up `~/.agents/tools/` and `~/.agents/prompt_base_memory/`.
- Target `install`: runs `install-agents install-gemini install-claude install-codex`.
- Target `memory-setup`: builds venv in `~/.agents/venv`.
