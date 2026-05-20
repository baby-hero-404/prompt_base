# Tier 0: Universal Rules (Always Active)

## Clean Code (Global Mandatory)

**ALL code MUST follow rules in `skills/core/clean-code/SKILL.md`. No exceptions.**

- **Simplicity First**: Write the minimum code that solves the problem. No speculative abstractions or features beyond what was asked.
- **Self-Documentation**: Every agent is responsible for documenting their own changes in relevant `.md` files.
- **Goal-Driven Execution**: Define success criteria/goals BEFORE coding. Add tests for invalid/valid inputs first, then make them pass. 
- **Infrastructure & Safety Mandate**: Follow the "5-Phase Deployment Process".
- **Modern Tech Mandate**: Always prioritize modern, high-performance libraries and stable, next-generation frameworks (e.g., Next.js 15, Tailwind v4, Biome, Shadcn). Reject legacy or deprecated patterns.
- **Quality Gate**: Every final output MUST be reviewed by the `quality-gatekeeper`.
- **Implementation Notes Mandate**: Implement <Spec> and while you do keep a running `implementation-notes.md` (or `.html`) file with decisions you had to make that weren't in the spec, things you had to change, tradeoffs you had to make or anything else I should know. Place this file into the `docs/implementation` folder of the current project.

## File Dependency Awareness

**Before modifying ANY file:**

1. Check `ARCHITECTURE.md` → File Dependencies
2. Identify dependent files
3. Update ALL affected files together

## 🧠 Intellectual Integrity (Think Before Coding)

- **State Assumptions**: Explicitly state assumptions before implementing.
- **Surface Tradeoffs**: If multiple interpretations or approaches exist, present them before picking.
- **Push Back**: Identify simpler approaches or warrant pushback on requested complexity.
- **Stop on Confusion**: If something is unclear, stop and ask immediately.

## ✂️ Surgical Changes & Adjacent Integrity

- **Minimum Touch**: Only touch what is necessary. Match existing style.
- **Orphans**: Remove imports/variables/functions that your changes made unused.
- **Adjacent Bugs**: If an adjacent bug or vulnerability is found, **FIX IT IMMEDIATELY** and document the change clearly.

## System Map Read

> 🔴 **MANDATORY**: Read `ARCHITECTURE.md` and `registry.min.json` at session start.

**Path Awareness:**

- Agents: `[ROOT]/antigravity/agents/`
- Skills: `[ROOT]/antigravity/skills/{core|tech|process|custom}/`
- Core Config: `[ROOT]/core/`
- Registry: `[ROOT]/registry.min.json`

## ⚡ Token Efficiency Protocol
- **Snippet-Only Reading**: Avoid reading full files if a summary or specific sub-item exists. Use `StartLine/EndLine`.
- **MVC (Minimal Viable Context)**: Unload skills immediately after use.
- **No Conversational Bloat**: Do not ask "The user wants X?" or apologize for errors. State the action and execute.
- **Diffs over Full Writes**: When editing, only output the necessary changes.
