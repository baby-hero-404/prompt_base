---
description: Perform a pre-commit code review on staged changes using the verification-before-completion skill.
---

# /review - Pre-Commit Code Review

## Task

Analyze staged changes (`git diff --staged`) against coding standards, security best practices, and project patterns before committing.

## Usage

```bash
/review
```

## Workflow Steps

1.  **Check Staged Changes**
    - Run: `git diff --staged --name-only`
    - If output is empty -> **STOP**. Inform user "No staged changes found. Please `git add` files first."

2.  **Retrieve Diff**
    - Run: `git diff --staged`
    - Capture output.

3.  **Execute Review**
    - **Activate Skill**: `verification-before-completion` (skills/process/verification-before-completion)
    - **Input**: The captured diff content.
    - **Instruction**: "Perform a formal pre-commit review of these changes following the verification-before-completion pre-commit protocol."

4.  **Output Report**
    - Present findings in the standardized format defined by the skill.
    - Highlight "BLOCKING" issues vs "NITPICKS".

## Technical Implementation

```python
# Pseudo-code for agent execution
import subprocess

def run_workflow():
    # 1. Check
    files = subprocess.check_output(["git", "diff", "--staged", "--name-only"]).decode().strip()
    if not files:
        return "⚠️ No staged changes. Run `git add <file>` first."

    # 2. Get Diff
    diff_content = subprocess.check_output(["git", "diff", "--staged"]).decode()

    # 3. Review
    # Prompt the LLM with the diff and the skill context
    return llm.invoke(tool="verification-before-completion", input=diff_content)
```
