---
name: codebase-cleanup
description: Use when analyzing the codebase to perform a comprehensive cleanup, removing unused code, dead code, and duplicates without changing business logic.
---

# Codebase Cleanup & Refactoring

## Methodology

When invoked to perform a codebase cleanup or comprehensive refactor, follow these objectives and rules strictly to ensure safety, readability, and maintainability.

### 1. Detect and Remove
Analyze the project to detect and safely remove:
- Unused functions and dead code
- Unused variables and imports
- Unused classes, interfaces, or types
- Duplicate logic
- Obsolete helper utilities
- Legacy files that are no longer referenced
- Commented-out code that is no longer needed

### 2. Improve Readability
- Simplify complex functions
- Split large functions into smaller reusable functions
- Improve naming consistency
- Remove unnecessary nesting
- Reduce code duplication (DRY)
- Group related logic together

### 3. Improve Project Structure
- Reorganize folders if necessary
- Remove redundant files
- Consolidate duplicate utilities
- Ensure consistent architecture and conventions
- **File Responsibility Rule:** A file should answer the question: *"What is this file responsible for?"* If the answer takes more than one sentence, the file should be split.

### 4. Safety Requirements
- **Do NOT change business logic.**
- **Do NOT modify API contracts unless absolutely necessary.**
- **Do NOT remove code that is dynamically referenced without verifying usage.**
- If uncertain whether something is used, mark it as "potentially unused" instead of removing it.
- Explain why each file/function is removed in your reasoning.
- **Always adhere to the `coding-standards` skill during all refactoring and cleanup actions.**

### 5. Output Format
At the end of your process, provide a structured report containing:
- **Summary of issues found:** High-level overview of tech debt and unused code.
- **Files/Functions removed:** List of safely removed components.
- **Duplicate logic detected:** Where and how it was resolved.
- **Refactoring recommendations:** Any further architectural suggestions.
- **Final status:** Confirmation that all modifications preserve the existing behavior.

> **Note:** Assume this is a production codebase. Prioritize maintainability, readability, and long-term scalability. Apply SOLID, DRY, KISS principles where appropriate while preserving behavior.
