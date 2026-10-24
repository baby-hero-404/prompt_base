# Specification: Codex CLI Support in Prompt Base

## 1. Directory Layout & Paths
Target directory: `~/.codex`

```text
~/.codex/
├── AGENTS.md                  ← Rules & Persona (loaded on every session)
├── ARCHITECTURE.md            ← Architecture documentation
├── registry.min.json          ← Metadata index for skills & agents
├── agents/                    ← 14 Specialist agent references
├── skills/                    ← 50+ Global Skills
│   ├── api-patterns/
│   │   └── SKILL.md
│   ├── code-review/
│   │   └── SKILL.md
│   └── ...
└── global_workflows/          ← Workflow guides
```

## 2. Skill Contract Compatibility
- Each skill in `~/.codex/skills/<skill-name>/` contains `SKILL.md`.
- Frontmatter format:
  ```yaml
  ---
  name: <skill-name>
  description: <description>
  ---
  ```
- Interactive invocation in Codex CLI:
  - Select list: `/skills`
  - Direct call: `$skill-name <args>` (e.g. `$code-review Review my authentication module.`)

## 3. Rules & Instructions Compatibility
- File: `~/.codex/AGENTS.md`
- Header specifies layout and invocation conventions for Codex CLI.
- `## Rules` section (R1 - R11) must be strictly identical across `GEMINI.md`, `CLAUDE.md`, and `AGENTS.md`.

## 4. Automation & Manifest Contract
- `install.manifest.json`: Target includes `~/.codex`.
- `Makefile`:
  - `install-codex`: Copies files via `scripts/install_manifest.py ~/.codex`, cleans extraneous MDs (`GEMINI.md`, `CLAUDE.md`), and runs `cleanup.sh ~/.codex`.
  - `install`: Runs `install-gemini install-claude install-codex`.
- `scripts/test_integration.py`: Validates `AGENTS.md` existence and asserts rules synchronization between `CLAUDE.md`, `GEMINI.md`, and `AGENTS.md`.
