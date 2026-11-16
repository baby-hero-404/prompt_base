---
description: Formal audit of changes before committing.
---

# /review - Code Review Procedure

$ARGUMENTS

---

## Behavior

1. Run quality gates and static checks.
2. Check for security vulnerabilities, hardcoded secrets, or anti-patterns.
3. Activate `verification-before-completion` skill to validate correctness.
4. Review the final diff with the `code-review` skill. If it finds leftovers, orphans, or needless complexity in your own change, run `/cleanup`.
