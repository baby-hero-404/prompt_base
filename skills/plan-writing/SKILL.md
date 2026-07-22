---
name: plan-writing
description: "Use when you have a spec or requirements for a multi-step task, before touching code."
allowed-tools: Read, Write, Edit, Glob, Grep, Bash
---

# Writing Plans

## Overview

Write comprehensive implementation plans assuming the engineer has zero context and questionable taste. Document everything they need: which files to touch, code, testing, how to verify. Give them bite-sized tasks. DRY. YAGNI. TDD. Frequent commits.

**Output location (Plan Artifact Precedence):** If the spec is an OpenSpec set (`docs/openspecs/<task>/`), write the plan content INTO its `tasks.md` (structure below still applies) — do not create a separate `docs/plans/PLAN-*.md`. Only use `docs/plans/PLAN-YYYYMMDD-{slug}.md` when no OpenSpec set exists.

**Announce at start:** "I'm using the plan-writing skill to create the implementation plan."

## Scope Check

If the spec covers multiple independent subsystems, suggest breaking into separate plans — one per subsystem. Each plan should produce working, testable software on its own.

## File Structure

Before defining tasks, map out which files will be created or modified and what each one is responsible for.

- Design units with clear boundaries and well-defined interfaces
- Prefer smaller, focused files over large ones that do too much
- In existing codebases, follow established patterns

## Bite-Sized Task Granularity

**Each step is one action (2-5 minutes):**
- "Write the failing test" — step
- "Run it to make sure it fails" — step
- "Implement the minimal code to make the test pass" — step
- "Run the tests and make sure they pass" — step
- "Commit" — step

## Plan Document Header

**Every plan MUST start with this header:**

```markdown
# [Feature Name] Implementation Plan

> **For agentic workers:** Use subagent-driven-development or executing-plans
> to implement this plan task-by-task. Steps use checkbox syntax for tracking.

**Goal:** [One sentence describing what this builds]

**Architecture:** [2-3 sentences about approach]

**Tech Stack:** [Key technologies/libraries]

---
```

## Task Structure

````markdown
### Task N: [Component Name]

**Files:**
- Create: `exact/path/to/file.py`
- Modify: `exact/path/to/existing.py:123-145`
- Test: `tests/exact/path/to/test.py`

- [ ] **Step 1: Write the failing test**

```python
def test_specific_behavior():
    result = function(input)
    assert result == expected
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/path/test.py::test_name -v`
Expected: FAIL with "function not defined"

- [ ] **Step 3: Write minimal implementation**

```python
def function(input):
    return expected
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/path/test.py::test_name -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add tests/path/test.py src/path/file.py
git commit -m "feat: add specific feature"
```
````

## No Placeholders

Every step must contain the actual content an engineer needs. These are **plan failures** — never write them:
- "TBD", "TODO", "implement later", "fill in details"
- "Add appropriate error handling" / "add validation" / "handle edge cases"
- "Write tests for the above" (without actual test code)
- "Similar to Task N" (repeat the code — the engineer may be reading tasks out of order)
- Steps that describe what to do without showing how (code blocks required for code steps)
- References to types, functions, or methods not defined in any task

## Remember
- Exact file paths always
- Complete code in every step — if a step changes code, show the code
- Exact commands with expected output
- DRY, YAGNI, TDD, frequent commits

## Self-Review

After writing the complete plan, review it against the spec:

1. **Spec coverage:** Skim each requirement in the spec. Can you point to a task that implements it? List any gaps.
2. **Placeholder scan:** Search for red flags — any "TBD", "TODO", or patterns from the "No Placeholders" section. Fix them.
3. **Type consistency:** Do types, method signatures, and property names match across tasks?

If you find issues, fix them inline. If you find a spec requirement with no task, add the task.


## Extended References
For less-frequently-needed detail, see [`references/extended-reference.md`](references/extended-reference.md):
- Execution Handoff
- Red Flags
- Common Rationalizations
