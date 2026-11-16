# Design: Evaluator & Architecture Hardening

## 1. Key Decisions

| Decision | Rationale |
|---|---|
| Fail-closed on missing judge scores | Without individual 0-100 scores, absolute quality $Q(\text{variant})$, $\Delta Q$, and ROI efficiency cannot be computed. Failing immediately prevents silent corruption of eval reports. |
| Two-tier pricing structure (`free` / `paid`) in `pricing.json` | Google AI Studio has two distinct billing realities: Free tier ($0) with rate limits and Paid tier ($0.25/$1.50). Users can switch tiers via `--tier paid` or `--tier free`. |
| 40,000-character & 10-file ceiling on `read_files` | Matches token limits (10K tokens) while allowing multi-file inspection; protects against massive accidental dumps. |
| Opt-in debug logs via `GOLDEN_EVAL_DEBUG=1` | Reconciles privacy claims with developer debugging needs: standard runs leave zero prompt files in `.tmp/`. |
| Selective sync for `make install` | `install_manifest.py` already copies files safely; removing pre-emptive `rm -rf` prevents clobbering user's non-prompt-base skills. |

---

## 2. Component Architecture

### 2.1 Judge Output Validation
`normalize_verdict` is enhanced to strictly validate the entire schema:
```python
def normalize_verdict(verdict):
    if not isinstance(verdict, dict) or verdict.get("status") not in VALID_STATUSES:
        return judge_error(f"Judge returned an invalid verdict: {verdict!r}")
    
    scores = verdict.get("scores")
    if not isinstance(scores, dict):
        return judge_error("Judge verdict missing 'scores' object")
    
    first = _valid_score(scores.get("first"))
    second = _valid_score(scores.get("second"))
    if first is None or second is None:
        return judge_error(f"Judge returned invalid scores: {scores!r} (must be 0-100)")
    
    return verdict
```

### 2.2 Tiered Pricing Schema (`evals/pricing.json`)
```json
{
  "version": "2026-11-16",
  "source": "https://ai.google.dev/pricing",
  "currency": "USD",
  "default_tier": "paid",
  "tiers": {
    "free": {
      "description": "Google AI Studio Free Tier (no cost)",
      "models": {
        "gemini-3.1-flash-lite": { "input_per_million": 0.0, "cached_input_per_million": 0.0, "output_per_million": 0.0 },
        "gemini-2.5-flash": { "input_per_million": 0.0, "cached_input_per_million": 0.0, "output_per_million": 0.0 },
        "gemini-2.5-pro": { "input_per_million": 0.0, "cached_input_per_million": 0.0, "output_per_million": 0.0 }
      }
    },
    "paid": {
      "description": "Google AI Studio Pay-as-you-go Tier",
      "models": {
        "gemini-3.1-flash-lite": { "input_per_million": 0.25, "cached_input_per_million": 0.025, "output_per_million": 1.50 },
        "gemini-2.5-flash": { "input_per_million": 0.30, "cached_input_per_million": 0.03, "output_per_million": 2.50 },
        "gemini-2.5-pro": { "input_per_million": 1.25, "cached_input_per_million": 0.125, "output_per_million": 10.00 }
      }
    }
  }
}
```
`load_pricing(path, tier="paid")` resolves models from the selected tier.

### 2.3 Safe Tool Execution (`read_files`)
```python
MAX_READ_FILES_COUNT = 10
MAX_READ_FILE_CHARS = 20000
MAX_READ_FILES_TOTAL_CHARS = 40000

if name == "read_files":
    paths = args.get("paths", [])
    if not isinstance(paths, list):
        return "ERROR: 'paths' must be a list of strings."
    
    header = ""
    if len(paths) > MAX_READ_FILES_COUNT:
        header = f"[Notice: read_files capped at {MAX_READ_FILES_COUNT} files; {len(paths) - MAX_READ_FILES_COUNT} omitted]\n"
        paths = paths[:MAX_READ_FILES_COUNT]
    
    results = []
    total_chars = 0
    for path in paths:
        try:
            p = _safe_path(workspace, path)
            if not p.is_file():
                entry = f"=== File: {path} ===\nERROR: file not found\n"
            else:
                raw = p.read_text(errors="replace")
                if len(raw) > MAX_READ_FILE_CHARS:
                    raw = raw[:MAX_READ_FILE_CHARS] + "\n[Truncated at 20000 characters; use read_file with start_line/end_line]"
                entry = f"=== File: {path} ===\n{raw}\n"
        except ValueError as e:
            entry = f"=== File: {path} ===\nERROR: {e}\n"
        
        results.append(entry)
        total_chars += len(entry)
        if total_chars > MAX_READ_FILES_TOTAL_CHARS:
            break

    joined = header + "\n".join(results)
    if len(joined) > MAX_READ_FILES_TOTAL_CHARS:
        joined = joined[:MAX_READ_FILES_TOTAL_CHARS] + f"\n[TRUNCATED: read_files exceeded maximum total characters ({MAX_READ_FILES_TOTAL_CHARS})]"
    return joined
```

### 2.4 Ephemeral Debugging
In `gemini_generate()`:
```python
debug_enabled = os.environ.get("GOLDEN_EVAL_DEBUG") == "1"
if debug_enabled:
    tmp_dir = root_dir / '.tmp'
    # write request.md and response.md
```
In `main()` `finally`:
```python
if os.environ.get("GOLDEN_EVAL_DEBUG_KEEP") != "1":
    shutil.rmtree(root_dir / '.tmp', ignore_errors=True)
```

### 2.5 Non-Destructive Installation
In `Makefile`:
Instead of:
```makefile
@rm -rf ~/.claude/skills ~/.claude/agents ~/.claude/global_workflows
```
We remove only the exact skill directories that Prompt Base publishes, e.g. using `python3 scripts/cleanup_managed.py ~/.claude` or letting `install_manifest.py` overwrite managed files without wiping the whole directory.

---

## 3. Security & Safety Boundaries
- **Prompt Isolation:** Telemetry continues to never log prompts, secret tokens, or file contents.
- **Privacy:** `.tmp/` is neither created by default nor left on disk after runs.
- **Quota Safeguard:** Multi-tiered truncation prevents runaway multi-file reads.
- **File Integrity:** User customizations in `~/.claude`, `~/.gemini`, `~/.codex` remain intact across `make install`.

