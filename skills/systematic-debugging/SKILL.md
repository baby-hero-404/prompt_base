---
name: systematic-debugging
description: "Use when encountering any bug, test failure, or unexpected behavior, before proposing fixes."
allowed-tools: Read, Write, Edit, Glob, Grep, Bash
---

# Systematic Debugging

## Overview

Random fixes waste time and create new bugs. Quick patches mask underlying issues.

**Core principle:** ALWAYS find root cause before attempting fixes. Symptom fixes are failure.

**Violating the letter of this process is violating the spirit of debugging.**

## The Iron Law

```
NO FIXES WITHOUT ROOT CAUSE INVESTIGATION FIRST
```

If you haven't completed Phase 1, you cannot propose fixes.

## When to Use

Use for ANY technical issue:
- Test failures
- Bugs in production
- Unexpected behavior
- Performance problems
- Build failures
- Integration issues

**Use this ESPECIALLY when:**
- Under time pressure (emergencies make guessing tempting)
- "Just one quick fix" seems obvious
- You've already tried multiple fixes
- Previous fix didn't work

**Don't skip when:**
- Issue seems simple (simple bugs have root causes too)
- You're in a hurry (rushing guarantees rework)

## The Four Phases

You MUST complete each phase before proceeding to the next.

### Phase 1: Root Cause Investigation

**BEFORE attempting ANY fix:**

1. **Read Error Messages Carefully**
   - Don't skip past errors or warnings
   - Read stack traces completely
   - Note line numbers, file paths, error codes

2. **Reproduce Consistently**
   - Can you trigger it reliably?
   - What are the exact steps?
   - If not reproducible → gather more data, don't guess

3. **Check Recent Changes**
   - What changed that could cause this?
   - Git diff, recent commits
   - New dependencies, config changes

4. **Gather Evidence in Multi-Component Systems**

   **WHEN system has multiple components:**

   **BEFORE proposing fixes, add diagnostic instrumentation:**
   ```
   For EACH component boundary:
     - Log what data enters component
     - Log what data exits component
     - Verify environment/config propagation
     - Check state at each layer

   Run once to gather evidence showing WHERE it breaks
   THEN analyze evidence to identify failing component
   THEN investigate that specific component
   ```

5. **Trace Data Flow**
   - Where does bad value originate?
   - What called this with bad value?
   - Keep tracing up until you find the source
   - Fix at source, not at symptom

### Phase 2: Pattern Analysis

1. **Find Working Examples** — Locate similar working code in same codebase
2. **Compare Against References** — Read reference implementation COMPLETELY (don't skim)
3. **Identify Differences** — List every difference, however small
4. **Understand Dependencies** — What other components, config, environment does it need?

### Phase 3: Hypothesis and Testing

1. **Form Single Hypothesis** — "I think X is the root cause because Y"
2. **Test Minimally** — Smallest possible change, one variable at a time
3. **Verify** — Did it work? Yes → Phase 4. No → NEW hypothesis (don't stack fixes)

### Phase 4: Implementation

1. **Create Failing Test Case** — MUST have before fixing
2. **Implement Single Fix** — ONE change, address root cause only
3. **Verify Fix** — Test passes? No other tests broken?
4. **If Fix Doesn't Work** — Count attempts:
   - If < 3: Return to Phase 1
   - **If ≥ 3: STOP and question the architecture**
   - DON'T attempt Fix #4 without discussing fundamentals

5. **If 3+ Fixes Failed: Question Architecture**
   - Is this pattern fundamentally sound?
   - Are we "sticking with it through sheer inertia"?
   - Should we refactor architecture vs. continue fixing symptoms?
   - **Discuss with user before attempting more fixes**


## Extended References
For less-frequently-needed detail, see [`references/extended-reference.md`](references/extended-reference.md):
- Red Flags — STOP and Follow Process
- Common Rationalizations
- Quick Reference
- Real-World Impact
