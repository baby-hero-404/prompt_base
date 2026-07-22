## Code Quality Reviewer Template

**Only dispatch after spec compliance review passes.**

```
Review the implementation for code quality:

## What Was Implemented
[From implementer's report]

## Review Focus
- Does each file have one clear responsibility?
- Are units decomposed so they can be tested independently?
- Is the implementation clean and maintainable?
- Names clear and accurate?
- Tests verify behavior (not just mock behavior)?
- No over-engineering (YAGNI)?

Report:
- Strengths
- Issues (Critical / Important / Minor)
- Assessment (Approved / Needs fixes)
```

## Red Flags

**Never:**
- Skip reviews (spec compliance OR code quality)
- Proceed with unfixed issues
- Dispatch multiple implementation subagents in parallel (conflicts)
- Make subagent read plan file (provide full text instead)
- Skip scene-setting context
- Ignore subagent questions
- Accept "close enough" on spec compliance
- Skip review loops (reviewer found issues = fix = review again)
- **Start code quality review before spec compliance is ✅**
- Move to next task while either review has open issues

**If subagent asks questions:** Answer clearly and completely.

**If reviewer finds issues:** Implementer fixes → reviewer reviews again → repeat until approved.

**If subagent fails task:** Dispatch fix subagent with specific instructions. Don't fix manually (context pollution).

## Integration

**Required workflow skills:**
- **plan-writing** — Creates the plan this skill executes
- **tdd-workflow** — Subagents follow TDD for each task
- **verification-before-completion** — Verify before claiming success
