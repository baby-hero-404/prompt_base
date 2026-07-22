---
description: Scaffold a new skill (folder, SKILL.md, frontmatter, registry sync, install) without manual boilerplate.
---

# /create-skill - Skill Scaffolder

$ARGUMENTS

---

## Task
Create a new skill from a name (and optional category/description) with zero manual boilerplate: folder, `SKILL.md` with valid frontmatter, a duplicate-safety check against both the live registry and the filesystem, then an automatic `make registry` + `make install`.

### Steps

1. **Parse arguments**
   - First token in `$ARGUMENTS` = skill name (required).
   - Look for `--category core|tech|process|custom` (default: `custom`).
   - Look for `--description "..."`. If omitted, ask the user for a one-line trigger description before scaffolding — this is what drives auto-discovery via `registry.min.json`, don't ship a `TODO` description.

2. **Run the scaffolder**
   ```bash
   python3 scripts/create_skill.py "<name>" --category <category> --description "<description>"
   ```
   This script owns the full sequence — duplicate check, directory creation, `SKILL.md` templating, `make registry`, `make install`. Do not hand-roll any of these steps yourself, and do not manually `mkdir`/`Write` a `SKILL.md` in parallel with it.

3. **If the script exits non-zero** (name collision, invalid category, `make install` failure): report the exact error to the user and stop. Do not silently pick a different name to work around a collision — that's the user's call.

4. **Flesh out the content**
   - The generated `SKILL.md` has `TODO` placeholders under "When to Use," "Core Principles," and "Anti-Patterns." Fill these in with real content — from the conversation context if `/create-skill` was invoked right after discussing a specific gap, or by asking the user.
   - If you change the `description` frontmatter after the initial scaffold, re-run `python3 scripts/generate_registry.py` — the scaffolder only synced the registry once, at creation time.

5. **Confirm**
   - Report the final path and confirm the skill now appears in `registry.min.json`.
   - It's live immediately: installed skills are symlinked from `~/.claude/skills/`, so no separate activation step is needed.

## Usage Examples

- `/create-skill rust-patterns --category tech --description "Use when writing or refactoring Rust code, ownership/borrowing, or Cargo workspace setup."`
- `/create-skill incident-postmortems` (category defaults to `custom`; you'll be asked for a description before scaffolding)
