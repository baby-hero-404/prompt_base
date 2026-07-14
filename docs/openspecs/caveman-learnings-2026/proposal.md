# Proposal: Caveman Learnings — Prompt & Delivery Refactor

> Source analysis: [`docs/discovery/DISCOVERY-caveman.md`](../../discovery/DISCOVERY-caveman.md)

## Why
The Caveman discovery report identified four techniques that directly address weaknesses in Prompt Base:

1. Our prompts (core rules, skills) contain no **tokenizer-aware guidance** — agents freely invent abbreviations (`cfg`, `impl`) and arrow chains (`A → B`) that cost the same tokens as full words while hurting readability. Caveman proves compression should target stylistic filler, never word shape or language.
2. Our behavioral personas (`behavioral-modes`, terse output rules) have **no safety escape hatch** — a persona active during a destructive operation (e.g., `DROP TABLE`, `rm -rf`, force-push) can omit conjunctions/warnings and cause dangerous ambiguity. Caveman's "Auto-Clarity" rule solves this.
3. Skills are loaded **whole-file**, even when only one section is relevant. Caveman's runtime Markdown section filtering keeps one human-readable source of truth while feeding the LLM only the active subset — a direct upgrade to our JIT Knowledge Protocol.
4. Our installer (`Makefile` targets `install-claude` / `install-gemini`) uses a blind `cp -r ./*` with **hardcoded targets and no exclude list**. This is the exact "brittle integration logic" anti-pattern the report flags — and it already bit us: the untracked `caveman/` directory gets copied into `~/.claude`/`~/.gemini`, and its read-only `.git` pack files make every subsequent `make install` fail with `Permission denied`.

## What Changes

### Issue 1: Tokenizer-Aware Output Rules (TIER 0)
- Add a "Token-Efficient Output" subsection to `core/rules.md`: ban invented abbreviations and arrow-chain shorthand in user-facing prose; compress by dropping filler, not by mangling words; never compress across languages ("compress style, not language").
- Mirror the rule in `antigravity/skills/core/context-management/SKILL.md` (token efficiency is its domain) with the *why* (BPE tokenizers split invented words into multiple tokens).

### Issue 2: Auto-Clarity Escape Hatch
- Add an "Auto-Clarity Override" rule to `core/system_prompt.md` and `antigravity/skills/core/behavioral-modes/SKILL.md`: any active persona/brevity mode is automatically suspended for security warnings, destructive/irreversible actions, and multi-step sequences where omitted words create ambiguity.

### Issue 3: Section-Level Skill Filtering (JIT v2)
- Extend `antigravity/skills/core/skill-loading/SKILL.md` with a section-filtering protocol: when a skill is activated for a narrow sub-task, load only the matching `##` sections (by heading match against the task intent) instead of the full `SKILL.md`.
- Keep single-source-of-truth: no split files; filtering happens at read time.

### Issue 4: Config-Driven, Exclude-Aware Installer
- Replace the blind `cp -r ./*` in `Makefile` (`install-gemini` line 32, `install-claude` line 50) with an exclude-aware copy (rsync-style or a small Python helper) driven by an `install.manifest.json` listing include/exclude globs and target roots.
- Excludes at minimum: `caveman/`, `.git*`, `docs/`, `scripts/`, `__pycache__/`, `Makefile`, `README.md` (today `scripts/cleanup.sh` deletes some of these *after* copying — copy-then-delete is what breaks on read-only files).
- Fix the current breakage: remove the stray `caveman/` copies from `~/.claude` and `~/.gemini`.

## Capabilities

### New Capabilities
- TIER 0 tokenizer-aware output policy.
- Auto-Clarity safety override for all personas/modes.
- Section-level JIT skill loading.
- Manifest-driven installer with exclude support.

### Modified Capabilities
- `core/rules.md`, `core/system_prompt.md` — extended, no removals.
- `Makefile` install targets — same commands (`make install`), new mechanism.
- `scripts/cleanup.sh` post-install role shrinks (excludes replace copy-then-delete).

### Removed Capabilities
- None (behavior-preserving refactor; `make install` CLI unchanged).

## Impact

| Area | Files Affected |
|------|----------------|
| Core rules | `core/rules.md`, `core/system_prompt.md` |
| Skills | `antigravity/skills/core/context-management/SKILL.md`, `antigravity/skills/core/behavioral-modes/SKILL.md`, `antigravity/skills/core/skill-loading/SKILL.md` |
| Installer | `Makefile`, `scripts/install_manifest.py` (new), `install.manifest.json` (new), `scripts/cleanup.sh` |
| Registry | `registry.min.json` (regenerated if any skill `description` changes) |
| Docs | `ARCHITECTURE.md` (installer section), this spec set |
