---
name: subagent-driven-development
description: "Use when executing implementation plans with independent tasks in the current session."
allowed-tools: Read, Write, Edit, Glob, Grep, Bash
---

# Subagent-Driven Development

Execute plan by dispatching a fresh subagent per task, and enforcing the two-stage review using the `verification-before-completion` skill.

**Why subagents:** Delegate tasks to specialized agents with isolated context. By precisely crafting their instructions and context, you ensure they stay focused. They should never inherit your session's context — you construct exactly what they need.

**Core principle:** Fresh subagent per task + `verification-before-completion` = high quality, fast iteration

## When to Use

- Have an implementation plan with independent tasks
- Tasks are mostly independent (not tightly coupled)
- Want to stay in the current session

**vs. Inline Execution:**
- Fresh subagent per task (no context pollution)
- Two-stage review after each task
- Faster iteration (no human-in-loop between tasks)

## The Process

```
1. Read plan, extract all tasks with full text, create task list
2. FOR EACH TASK:
   a. Dispatch implementer subagent (with full task text + context)
   b. Handle implementer status (DONE / BLOCKED / NEEDS_CONTEXT)
   c. Trigger `verification-before-completion` (two-stage spec/quality review)
   d. If verification fails → implementer fixes → re-verify
   e. Mark task complete
3. After all tasks → final code review of entire implementation
4. Finish development branch
```

## Handling Implementer Status

**DONE:** Proceed to spec compliance review.

**DONE_WITH_CONCERNS:** Read concerns before proceeding. If about correctness/scope, address first. If observations, note and proceed.

**NEEDS_CONTEXT:** Provide missing context and re-dispatch.

**BLOCKED:** Assess the blocker:
1. Context problem → provide more context, re-dispatch
2. Needs more reasoning → re-dispatch with more capable model
3. Task too large → break into smaller pieces
4. Plan itself wrong → escalate to user

**Never** ignore an escalation or force retry without changes.

## Implementer Prompt Template

```
You are implementing Task N: [task name]

## Task Description
[FULL TEXT of task from plan - paste it, don't make subagent read file]

## Context
[Scene-setting: where this fits, dependencies, architectural context]

## Before You Begin
If you have questions about requirements, approach, dependencies, or anything
unclear — ask them now. Raise any concerns before starting work.

## Your Job
1. Implement exactly what the task specifies
2. Write tests (following TDD if task says to)
3. Verify implementation works
4. Commit your work
5. Self-review (completeness, quality, discipline, testing)
6. Report back

## When You're in Over Your Head
It is always OK to stop and say "this is too hard for me."
Bad work is worse than no work.

## Report Format
- **Status:** DONE | DONE_WITH_CONCERNS | BLOCKED | NEEDS_CONTEXT
- What you implemented
- What you tested and test results
- Files changed
- Self-review findings
- Any issues or concerns
```

## Spec Reviewer Prompt Template

```
You are reviewing whether an implementation matches its specification.

## What Was Requested
[FULL TEXT of task requirements]

## What Implementer Claims They Built
[From implementer's report]

## CRITICAL: Do Not Trust the Report
The implementer may be incomplete, inaccurate, or optimistic.
You MUST verify everything independently.

**DO NOT:** Take their word, trust claims, accept their interpretation
**DO:** Read actual code, compare to requirements line by line

Report:
- ✅ Spec compliant (if everything matches after code inspection)
- ❌ Issues found: [list what's missing or extra, with file:line references]
```


## Extended References
For less-frequently-needed detail, see [`references/extended-reference.md`](references/extended-reference.md):
- Code Quality Reviewer Template
- Red Flags
- Integration
