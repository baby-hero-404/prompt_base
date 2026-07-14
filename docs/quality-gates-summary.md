# Prompt Base: Quality Gates & Testing Summary

This document summarizes all the testing mechanisms (Quality Gates) currently implemented in the framework to ensure skills remain high-quality, deterministic, and safe.

| Tier | Name | What it checks | Example Test Case / Data | How to run |
|---|---|---|---|---|
| **Tier 1** | **Linter** (`skill_lint.py`) | Validates YAML frontmatter, ensures `description` is not empty, and checks Markdown formatting. | *Checks if `SKILL.md` contains valid YAML and has `description: "..."`* | `make skill-check` |
| **Tier 2** | **Trigger Test** (`trigger_test.py`) | Tests if the LLM classifier correctly routes user intents to your skill (Precision & Recall). | **Input**: `"start tdd"`<br>**Expects**: `["tdd-workflow"]`<br>*(from `tests/skills/trigger_cases.json`)* | `make skill-check` |
| **Tier 0** | **Contract Check** (`skill_contract.py`) | Static analysis. Verifies that any file paths, CLIs, or other skills referenced in your prompt actually exist. | *Fails if your prompt says `Run python foo.py` but `foo.py` doesn't exist.* | `make skill-check` |
| **Tier 3** | **Golden Eval** (`golden_eval.py`) | LLM-as-a-Judge regression testing. Simulates an agent loop on real tasks to see if your code changes make the LLM output better or worse. | **Input**: `task1.yaml` (Ask agent to explore codebase).<br>**Judge**: Evaluates Constructiveness & Format. | `make skill-eval SKILL=<name>` |
| **System** | **Integration Test** (`test_integration.py`) | Ensures core system features (like Registry generation, Python scripts) work end-to-end. | *Creates a dummy skill, builds registry, and asserts output.* | `make test` |
| **System** | **Checklist** (`checklist.py`) | Audits the project structure to find orphaned skills or broken setups. | *Fails if a skill directory exists but is missing from registry.* | `make audit` |

## Where are the Test Cases stored?

1. **Trigger Cases (Tier 2)**: 
   Located in `tests/skills/trigger_cases.json`.
   ```json
   [
     {"prompt": "optimize seo", "expect": ["seo-fundamentals"]},
     {"prompt": "hello how are you", "expect": []}
   ]
   ```

2. **Golden Eval Tasks (Tier 3)**:
   Located in `evals/golden/<skill-name>/*.yaml`.
   ```yaml
   prompt: "Analyze this codebase and give me a summary."
   judge_model: "gemini-3.5-flash"
   rubric:
     Readability: "Is the output easy to read?"
     Completeness: "Did it cover all folders?"
   ```

3. **Feedback Journal (Tier 4)**:
   Located in `docs/reports/skill-feedback.md`. This is a human-in-the-loop journal where developers manually record why an evaluation failed and what rollback was applied.
