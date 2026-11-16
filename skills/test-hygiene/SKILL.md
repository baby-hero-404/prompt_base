---
name: test-hygiene
description: "Use when auditing test quality: redundant, flaky, or over-mocked tests. Triggers on test hygiene, flaky test, over-mocking, redundant tests, test quality."
allowed-tools: Read, Write, Edit, Glob, Grep, Bash
---

# Test Hygiene

> A test earns its place by answering two questions with yes: **if the behavior broke, would this test fail?** and **if this test fails, did the behavior break?**

## When to use

- After a task, on the tests it added, changed, or made obsolete.
- A test fails intermittently, or the suite is slow and nobody trusts it.
- The user asks whether the tests are meaningful.

**Not this skill:** how to structure and write new tests is `testing-patterns`; the red-green cycle is `tdd-workflow`.

## Scope

After a task: tests in the change set (as defined in `code-cleanup`) and tests whose subject the task removed or replaced. Weak tests you did not write are reported under "Noticed, not changed". For a wider review the user asked for, rank findings by what the test protects: data loss, security, and money first.

## Checklist

| Problem | Signs | Action |
|---|---|---|
| **No real assertion** | Only calls the code; asserts "no error" or "not empty"; asserts the value a mock was told to return; one snapshot of everything | Assert the specific outcome, or delete the test |
| **Over-mocking** | Mocks the unit under test or the project's own modules; verifies call order instead of results; setup longer than the test | Use the real object. Mock only system edges: network, clock, randomness, third-party services, storage when it must be isolated |
| **Redundant** | Another test at the same level already proves the same behavior through the same path; copies that differ by one value | Keep one; turn copies into a table of cases |
| **Flaky** | Depends on real time or sleeps, test order, shared state, network, randomness, time zone, or thread timing | Fix the cause: inject the clock, isolate state, fix the seed. Never fix with a retry, a longer sleep, or a skip |
| **Obsolete** | The behavior was removed or replaced; name or fixture no longer matches what is checked; disabled long ago with no condition | Delete, or rewrite for the current behavior, in the same change that made it obsolete |
| **Tied to implementation** | Asserts private details; breaks on a refactor that keeps behavior | Assert through the public behavior |
| **Misleading** | Name promises one thing, assertions check another; description only repeats the name | Rename or fix the assertions; drop the description |

Heavy mock setup is often a design signal: the module under test does too little itself. Report that; do not fix it by adding more mocks.

## Rules

- A failing test is information. Decide whether the code or the test is wrong before touching either. Never delete, skip, or loosen a test to get a passing run.
- Before deleting a test, name the behavior it covered and say where that behavior is covered now, or that the behavior no longer exists.
- A coverage percentage is not proof. Lines executed without assertions are not tested.
- Prefer the lowest test level that proves the behavior.
- Tests are not users: code referenced only by its tests goes to `dead-code-removal`.

## Verify

- Run the suite after every change to a test.
- For a strengthened assertion, break the behavior on purpose once, watch the test fail, then restore the code.
- For a flaky fix, run the test repeatedly with the runner's repeat option and with randomized order if available.

## Stop and ask

- A test fails and you cannot tell whether it or the code is right.
- Removing a test would leave important behavior with no coverage.
- The flakiness comes from shared infrastructure outside the repository.

## Report

```
Fixed:                <test> — <problem and what changed>
Removed:              <test> — <behavior it covered, and where that is covered now or why it is gone>
Noticed, not changed: <weak test outside the change set>
Verification:         <command> → <result>
```
