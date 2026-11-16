# Prompt Base: Quality Gates & Testing Summary

This document summarizes all the testing mechanisms (Quality Gates) currently implemented in the framework to ensure skills remain high-quality, deterministic, and safe.

| Tier | Name | What it checks | Example Test Case / Data | How to run |
|---|---|---|---|---|
| **Tier 1** | **Linter** (`skill_lint.py`) | Validates YAML frontmatter, ensures `description` is not empty, and checks Markdown formatting. | *Checks if `SKILL.md` contains valid YAML and has `description: "..."`* | `make skill-check` |
| **Tier 2** | **Trigger Test** (`trigger_test.py`) | Deterministic keyword test, no LLM: matches each prompt against the `Triggers on` keywords (whole-word regex) and scores Precision & Recall per skill. A skill with zero cases only prints a WARN. | **Input**: `"start tdd"`<br>**Expects**: `["tdd-workflow"]`<br>*(from `tests/skills/trigger_cases.json`)* | `make skill-check` |
| **Tier 0** | **Contract Check** (`skill_contract.py`) | Static analysis. Verifies that any file paths, CLIs, or other skills referenced in your prompt actually exist. | *Fails if your prompt says `Run python foo.py` but `foo.py` doesn't exist.* | `make skill-check` |
| **Tier 3** | **Golden Eval** (`golden_eval.py`) | LLM-as-a-Judge regression testing. Simulates a read-only agent loop (read/list/grep, no edits, no test runs) on real tasks and compares New vs Old (`--baseline`, default `HEAD`) and New vs no skill. WORSE against either, or any judge error, fails the run. | **Input**: `task1.yaml` (Ask agent to explore codebase).<br>**Judge**: Evaluates Constructiveness & Format. | `make skill-eval SKILL=<name>`; `make eval-coverage` lists skills without golden tasks |
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

## Golden Eval behavior & Telemetry

| Situation | Result |
|---|---|
| New or Old vs New or Baseline is `WORSE` | Exit 1 |
| Judge call fails, returns no JSON, or an invalid `status` | `ERROR`, exit 1 (never counted as `SAME`) |
| Skill has no golden tasks, baseline ref unreadable, or `--fast` | `UNVERIFIED`, exit 0 with a clear message; exit 1 with `--strict` |
| `--runs N` | Each task repeats N times; the verdict is the strict majority, any `ERROR` fails |
| Judge presentation order | Randomized per comparison to cancel position bias |
| Old equals New (for example after committing with the default `HEAD`) | Warning; pass `--baseline HEAD~1` or a tag |

### Token Telemetry & Evaluator Enhancement
Each golden evaluation run automatically records runtime telemetry without altering agent loop behavior or exit codes:

1. **Per-Call JSONL Log** (`docs/reports/eval-telemetry-<run_id>.jsonl`):
   - Appended and flushed immediately on every Gemini API call (`gemini_generate`).
   - Fields: `run_id`, `timestamp`, `git_sha`, `baseline_ref`, `skill`, `skill_sha256`, `task_id`, `variant`, `run_no`, `turn_no`, `model`, `status`, `error`, `latency_ms`, `retries`, `tokens` (input, cached, output, thinking, breakdown), `cost_usd`, `tools_called`, `tool_output_chars`.
   - Durability & Privacy: Zero prompt text, completion text, or API secrets are logged; all token figures in reports are computed directly from this JSONL trace.

2. **Cost & Pricing** (`evals/pricing.json`):
   - User-maintained model pricing table mapping model IDs to input, cached input, and output rates per million tokens.
   - If a model is unpriced or prices are `null`, cost is reported as `UNPRICED` (never a guessed default) with a single console warning.

3. **Input Token Attribution & Tool Range Optimization**:
   - Exact breakdown of prompt input: `fixed` (system instruction, prompt, tools), `skill` (skill body delta), `model_replies` (re-sent assistant turns), and `tool_outputs` (re-sent tool results).
   - `read_file` supports optional `start_line` and `end_line` (1-indexed, inclusive) with header `[Lines a-b of <path> (<total> lines)]` and explicit truncation notices when exceeding 20,000 characters.

4. **Efficiency Metrics & Advisory Recommendation**:
   - Tracks $T(\text{variant})$ (mean tokens per sample), $\Delta T = T(\text{new}) - T(\text{baseline})$, $Q(\text{variant})$ (mean 0–100 quality), $\Delta Q = Q(\text{new}) - Q(\text{baseline})$, Quality / 1K Tokens efficiency, Success Rate, Cost per Success, and Judge Overhead.
   - Evaluates an advisory recommendation (`KEEP`, `OPTIMIZE`, `REVIEW`, `REGRESSION`, `INSUFFICIENT_DATA`). The recommendation is strictly informational and never alters the script's exit code.
