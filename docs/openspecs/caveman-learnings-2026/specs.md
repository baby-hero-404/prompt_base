# Specs: Caveman Learnings — Prompt & Delivery Refactor

## Added Requirements

### REQ-001: Tokenizer-Aware Output Rules
> ✅ Status: Complete

**Scenario:**
- WHEN an agent produces user-facing prose or documentation with TIER 0 rules active
- THEN it does not invent abbreviations (`cfg`, `impl`, `fn` for prose) or arrow-chain shorthand (`A → B → fails`)
- AND compression is achieved by dropping stylistic filler, never by shortening words or switching the user's language
- AND `core/rules.md` states the rationale (BPE tokenizers split invented words into multiple tokens)

### REQ-002: Auto-Clarity Escape Hatch
> ✅ Status: Complete

**Scenario:**
- WHEN any persona or brevity mode is active
- AND the agent must warn about a security issue, describe a destructive/irreversible action, or give a multi-step sequence where omitted words create ambiguity
- THEN the persona is automatically suspended for that passage and full, unambiguous language is used
- AND the rule exists in both `core/system_prompt.md` and `antigravity/skills/core/behavioral-modes/SKILL.md`

### REQ-003: Section-Level Skill Loading
> ✅ Status: Complete

**Scenario:**
- WHEN a skill is activated for a narrow sub-task (e.g., only "mocking strategy" from `testing-patterns`)
- THEN only the frontmatter, Core Principles, and heading-matched sections are loaded into context
- AND the `SKILL.md` file remains a single unsplit source of truth on disk
- AND the agent may escalate to a full-file read when sections cross-reference each other

### REQ-004: Manifest-Driven Installer with Excludes
> ✅ Status: Complete

**Scenario:**
- WHEN `make install` runs in a repo containing untracked junk (e.g., a cloned `caveman/` directory with read-only `.git` pack files)
- THEN the excluded paths are never copied to `~/.claude` or `~/.gemini`
- AND the install completes with exit code 0
- AND a post-install assertion verifies `registry.min.json`, `core/`, and `antigravity/skills/` exist in each target

### REQ-005: Broken Install State Repaired
> ✅ Status: Complete

**Scenario:**
- WHEN the migration lands
- THEN stray `caveman/` copies are removed from `~/.claude` and `~/.gemini`
- AND running `make install` twice in a row succeeds both times (idempotency)

## Modified Requirements

### REQ-M01: cleanup.sh Role Reduction
> ✅ Status: Complete

**Scenario:**
- WHEN `make install` completes
- THEN `scripts/cleanup.sh` (or its replacement step) only prunes `__pycache__`
- AND no copy-then-delete of `docs/`, `scripts/`, `Makefile`, `README.md` occurs (excludes prevent them from arriving)

## Removed Requirements
- None.
