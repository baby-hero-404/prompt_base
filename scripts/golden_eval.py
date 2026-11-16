#!/usr/bin/env python3
import sys
import json
import re
import yaml
import tempfile
import shutil
import random
import hashlib
import secrets
import subprocess
from collections import Counter
from pathlib import Path
from datetime import datetime, timezone

import urllib.request
import urllib.error
import os
import time

DEFAULT_MODEL = os.environ.get("GEMINI_MODEL", "gemini-3.1-flash-lite")
MAX_TOOL_TURNS = 10

SCHEMA_VERSION = 1
EVALUATOR_VERSION = 2          # 2: the judge also returns an absolute 0-100 score per answer
DEFAULT_PASS_SCORE = 70        # a sample succeeds when its quality is at least this
MIN_PAIRED_SAMPLES = 3         # fewer samples than this gives no recommendation
GAIN_STRONG = 10               # quality points
TOKENS_CHEAP = 10_000          # extra tokens per sample versus no skill
TOKENS_ACCEPTABLE = 20_000
ERROR_TEXT_LIMIT = 300

# Global counter to track API calls
llm_call_count = 0

FUNCTION_DECLARATIONS = [
    {
        "name": "read_file",
        "description": "Read file contents in the workspace, optionally bounded by line numbers.",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Path relative to the workspace root."},
                "start_line": {"type": "integer", "description": "1-indexed starting line number (inclusive)."},
                "end_line": {"type": "integer", "description": "1-indexed ending line number (inclusive)."},
            },
            "required": ["path"],
        },
    },
    {
        "name": "read_files",
        "description": "Read the full contents of MULTIPLE files at once. Always prefer this over read_file when you need to examine more than one file to save tool turns.",
        "parameters": {
            "type": "object",
            "properties": {
                "paths": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of file paths relative to the workspace root."
                }
            },
            "required": ["paths"],
        },
    },
    {
        "name": "list_files",
        "description": "List files under a directory in the workspace, recursively.",
        "parameters": {
            "type": "object",
            "properties": {"path": {"type": "string", "description": "Directory relative to the workspace root. Use '.' for the root."}},
            "required": ["path"],
        },
    },
    {
        "name": "grep",
        "description": "Search all files in the workspace for a regex pattern; returns matching lines with file:line.",
        "parameters": {
            "type": "object",
            "properties": {"pattern": {"type": "string", "description": "Regex pattern to search for."}},
            "required": ["pattern"],
        },
    },
]


def load_env(root_dir):
    env_path = root_dir / '.env'
    if env_path.exists():
        with open(env_path, 'r') as f:
            for line in f:
                if '=' in line and not line.strip().startswith('#'):
                    k, v = line.strip().split('=', 1)
                    os.environ[k.strip()] = v.strip().strip("'").strip('"')


def format_request_md(data):
    md = ["# LLM API Request\n"]
    sys_inst = data.get("systemInstruction", {}).get("parts", [])
    if sys_inst:
        md.append("## System Instruction\n```markdown\n" + sys_inst[0].get("text", "") + "\n```\n")
        
    md.append("## Conversation History\n")
    for content in data.get("contents", []):
        role = content.get("role", "user")
        md.append(f"### Role: {role.upper()}\n")
        for part in content.get("parts", []):
            if "text" in part:
                md.append(part["text"] + "\n")
            elif "functionResponse" in part:
                name = part["functionResponse"].get("name", "unknown")
                res = part["functionResponse"].get("response", {}).get("result", "")
                md.append(f"**Tool Response ({name})**:\n```\n{res}\n```\n")
            elif "functionCall" in part:
                name = part["functionCall"].get("name", "unknown")
                args = part["functionCall"].get("args", {})
                md.append(f"**Assistant Tool Call ({name})**:\n```json\n{json.dumps(args, indent=2)}\n```\n")
    return "\n".join(md)


def format_response_md(res_json, error=None):
    md = ["# LLM API Response\n"]
    if error:
        md.append(f"## Error\n```\n{error}\n```\n")
        if res_json:
            md.append(f"## Raw Response\n```json\n{json.dumps(res_json, indent=2)}\n```\n")
        return "\n".join(md)
        
    usage = res_json.get("usageMetadata", {})
    md.append(f"**Tokens**: Input: {usage.get('promptTokenCount', 0)} | Output: {usage.get('candidatesTokenCount', 0)}\n")
    
    candidates = res_json.get("candidates", [])
    if not candidates:
        md.append("## No Candidates Returned\n")
        md.append(f"```json\n{json.dumps(res_json, indent=2)}\n```")
        return "\n".join(md)
        
    md.append("## Response Content\n")
    parts = candidates[0].get("content", {}).get("parts", [])
    for part in parts:
        if "text" in part:
            md.append(part["text"] + "\n")
        elif "functionCall" in part:
            fc = part["functionCall"]
            md.append(f"**Tool Call: {fc.get('name')}**\n```json\n{json.dumps(fc.get('args', {}), indent=2)}\n```\n")
            
    return "\n".join(md)


def gemini_generate(contents, root_dir, system_instruction=None, tools=None, temperature=0.0, model=DEFAULT_MODEL, prefix=""):
    global llm_call_count
    llm_call_count += 1
    print(f"    -> [API Call #{llm_call_count}] Sending request to {model}...", flush=True)
    
    tmp_dir = root_dir / '.tmp'
    call_dir = tmp_dir / f"{prefix}call_{llm_call_count:03d}_{datetime.now().strftime('%H%M%S')}"
    call_dir.mkdir(parents=True, exist_ok=True)
    
    req_file = call_dir / "request.md"
    res_file = call_dir / "response.md"
    
    # Sleep 5 seconds to strictly adhere to the 15 RPM free tier limit
    time.sleep(5)
    
    load_env(root_dir)
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return {"error": "GEMINI_API_KEY not found in .env or environment variables."}

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    data = {
        "contents": contents,
        "generationConfig": {"temperature": temperature},
    }
    if system_instruction:
        data["systemInstruction"] = {"parts": [{"text": system_instruction}]}
    if tools:
        data["tools"] = tools

    with open(req_file, "w", encoding="utf-8") as f:
        f.write(format_request_md(data))

    def _save_res(res_json, error=None):
        with open(res_file, "w", encoding="utf-8") as f:
            f.write(format_response_md(res_json, error))

    headers = {'Content-Type': 'application/json', 'x-goog-api-key': api_key}
    req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'), headers=headers)

    for attempt in range(6):
        try:
            t0 = time.perf_counter()
            with urllib.request.urlopen(req, timeout=120) as response:
                latency_ms = int((time.perf_counter() - t0) * 1000)
                res_json = json.loads(response.read().decode('utf-8'))
                _save_res(res_json)
                res_json["_meta"] = {"latency_ms": latency_ms, "retries": attempt, "model": model}
                return res_json
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt < 5:
                time.sleep(min(60, 5 * (attempt + 1)))  # 5,10,15,20,25s
                continue
            _save_res(None, f"HTTPError: {e}")
            return {"error": f"Gemini API call failed: {e}", "_meta": {"latency_ms": 0, "retries": attempt, "model": model}}
        except urllib.error.URLError as e:
            _save_res(None, f"URLError: {e}")
            return {"error": f"Gemini API call failed: {e}", "_meta": {"latency_ms": 0, "retries": attempt, "model": model}}
            
    _save_res(None, "Exhausted retries on 429")
    return {"error": "Gemini API call failed: exhausted retries on 429", "_meta": {"latency_ms": 0, "retries": 5, "model": model}}


def _safe_path(workspace, rel_path):
    base = Path(workspace).resolve()
    target = (base / (rel_path or ".")).resolve()
    if base not in target.parents and target != base:
        raise ValueError(f"path escapes workspace: {rel_path}")
    return target


def execute_tool(name, args, workspace):
    try:
        if name == "read_file":
            p = _safe_path(workspace, args.get("path", ""))
            if not p.is_file():
                return f"ERROR: file not found: {args.get('path')}"
            
            start = args.get("start_line")
            end = args.get("end_line")

            if start is not None and (isinstance(start, bool) or not isinstance(start, int)):
                return "ERROR: 'start_line' must be an integer"
            if end is not None and (isinstance(end, bool) or not isinstance(end, int)):
                return "ERROR: 'end_line' must be an integer"

            content = p.read_text(errors="replace")
            lines = content.splitlines(keepends=True)
            total = len(lines)

            if start is not None or end is not None:
                s = 1 if start is None else start
                e = total if end is None else end
                if s < 1:
                    s = 1
                if s > total:
                    return f"ERROR: start_line {s} is past the end ({total} lines)"
                if s > e:
                    return f"ERROR: start_line ({s}) > end_line ({e})"
                e = min(e, total)
                selected = "".join(lines[s - 1:e])
                header = f"[Lines {s}-{e} of {args.get('path')} ({total} lines)]\n"
                result = header + selected
            else:
                result = content

            if len(result) > 20000:
                return result[:20000] + "\n[Truncated at 20000 characters; use start_line/end_line]"
            return result

        if name == "read_files":
            paths = args.get("paths", [])
            if not isinstance(paths, list):
                return "ERROR: 'paths' must be a list of strings."
            results = []
            for path in paths:
                try:
                    p = _safe_path(workspace, path)
                    if not p.is_file():
                        results.append(f"=== File: {path} ===\nERROR: file not found\n")
                    else:
                        content = p.read_text(errors="replace")[:20000]
                        results.append(f"=== File: {path} ===\n{content}\n")
                except ValueError as e:
                    results.append(f"=== File: {path} ===\nERROR: {e}\n")
            return "\n".join(results)

        if name == "list_files":
            base = _safe_path(workspace, args.get("path", "."))
            if not base.exists():
                return f"ERROR: directory not found: {args.get('path')}"
            files = sorted(str(f.relative_to(workspace)) for f in base.rglob("*") if f.is_file())
            return "\n".join(files[:200]) if files else "(empty directory)"

        if name == "grep":
            pattern = args.get("pattern", "")
            matches = []
            for f in Path(workspace).rglob("*"):
                if not f.is_file():
                    continue
                try:
                    text = f.read_text(errors="ignore")
                except Exception:
                    continue
                for i, line in enumerate(text.splitlines(), 1):
                    if re.search(pattern, line):
                        matches.append(f"{f.relative_to(workspace)}:{i}:{line.strip()}")
                        if len(matches) >= 100:
                            break
                if len(matches) >= 100:
                    break
            return "\n".join(matches) if matches else "No matches"

        return f"ERROR: unknown tool '{name}'"
    except ValueError as e:
        return f"ERROR: {e}"


def run_agent(prompt, workspace, root_dir, skill_content, prefix="",
              telemetry=None, variant="new", task_id="inline_task", run_no=1,
              fixed_tokens=None, skill_sha256=None):
    """Runs the skill under test as a real tool-using agent, scoped to `workspace`."""
    
    global_instruction = "CRITICAL: Always use parallel tool calls when you need to read multiple files or fetch multiple resources at the same time to save API turns."
    final_instruction = f"{global_instruction}\n\n{skill_content}" if skill_content else global_instruction
    
    tools = [{"functionDeclarations": FUNCTION_DECLARATIONS}]
    contents = [{"role": "user", "parts": [{"text": prompt}]}]
    total_in_tokens = 0
    total_out_tokens = 0
    turns = []  # per-turn usage: {"turn", "in", "out", "tools"}
    prompt_tokens = []
    outputs = []

    for turn_no in range(1, MAX_TOOL_TURNS + 1):
        result = gemini_generate(contents, root_dir, system_instruction=final_instruction, tools=tools, prefix=prefix)
        if "error" in result:
            if telemetry:
                telemetry.record(
                    variant=variant,
                    task_id=task_id,
                    run_no=run_no,
                    turn_no=turn_no,
                    model=DEFAULT_MODEL,
                    response=result,
                    skill_sha256=skill_sha256,
                    tools_called=[],
                    tool_output_chars=0,
                    breakdown=None,
                    error=result.get("error"),
                )
            return f"ERROR: {result['error']}", total_in_tokens, total_out_tokens, turns, (prompt_tokens[0] if prompt_tokens else None)

        usage = result.get("usageMetadata", {})
        turn_in = usage.get("promptTokenCount", 0)
        turn_out = usage.get("candidatesTokenCount", 0)
        total_in_tokens += turn_in
        total_out_tokens += turn_out
        prompt_tokens.append(turn_in)
        outputs.append(turn_out)

        candidates = result.get("candidates")
        if not candidates:
            err_msg = f"ERROR: no candidates returned. Raw response: {json.dumps(result)}"
            if telemetry:
                telemetry.record(
                    variant=variant,
                    task_id=task_id,
                    run_no=run_no,
                    turn_no=turn_no,
                    model=DEFAULT_MODEL,
                    response=result,
                    skill_sha256=skill_sha256,
                    tools_called=[],
                    tool_output_chars=0,
                    breakdown=None,
                    error=err_msg,
                )
            return err_msg, total_in_tokens, total_out_tokens, turns, prompt_tokens[0]

        parts = candidates[0].get("content", {}).get("parts", [])
        contents.append({"role": "model", "parts": parts})

        function_calls = [p["functionCall"] for p in parts if "functionCall" in p]
        tool_names = [fc.get("name") for fc in function_calls]
        turns.append({"turn": turn_no, "in": turn_in, "out": turn_out,
                      "tools": tool_names})

        attr_rows = attribute(prompt_tokens, outputs, baseline_first=fixed_tokens, is_baseline=(variant == "baseline"))
        turn_breakdown = attr_rows[-1] if attr_rows else None

        response_parts = []
        tool_output_chars = 0
        if function_calls:
            for fc in function_calls:
                print(f"      * Tool call: {fc.get('name')}", flush=True)
                output = execute_tool(fc.get("name"), fc.get("args", {}) or {}, workspace)
                tool_output_chars += len(output)
                response_parts.append({
                    "functionResponse": {"name": fc.get("name"), "response": {"result": output}}
                })
            contents.append({"role": "user", "parts": response_parts})

        if telemetry:
            telemetry.record(
                variant=variant,
                task_id=task_id,
                run_no=run_no,
                turn_no=turn_no,
                model=DEFAULT_MODEL,
                response=result,
                skill_sha256=skill_sha256,
                tools_called=tool_names,
                tool_output_chars=tool_output_chars,
                breakdown=turn_breakdown,
            )

        if not function_calls:
            texts = [p.get("text", "") for p in parts if "text" in p]
            joined = "\n".join(t for t in texts if t)
            final_text = joined or f"ERROR: model returned no text and no tool calls. Raw candidate: {json.dumps(candidates[0])}"
            return final_text, total_in_tokens, total_out_tokens, turns, prompt_tokens[0]

    err_timeout = "ERROR: exceeded max tool turns without a final answer"
    if telemetry:
        telemetry.record(
            variant=variant,
            task_id=task_id,
            run_no=run_no,
            turn_no=MAX_TOOL_TURNS + 1,
            model=DEFAULT_MODEL,
            response=None,
            skill_sha256=skill_sha256,
            tools_called=[],
            tool_output_chars=0,
            breakdown=None,
            error=err_timeout,
        )
    return err_timeout, total_in_tokens, total_out_tokens, turns, (prompt_tokens[0] if prompt_tokens else None)


def judge_results(old_res, new_res, rubric, model, root_dir, prefix="",
                  telemetry=None, task_id="inline_task", run_no=1, variant="judge_old_new"):
    template_path = root_dir / 'evals' / 'golden' / 'judge_template.txt'
    with open(template_path, 'r', encoding='utf-8') as f:
        template = f.read()

    judge_prompt = template.replace(
        '{rubric}', yaml.dump(rubric)
    ).replace(
        '{old_res}', old_res
    ).replace(
        '{new_res}', new_res
    )
    result = gemini_generate(
        [{"role": "user", "parts": [{"text": judge_prompt}]}],
        root_dir, temperature=0.0, model=model, prefix=prefix
    )

    if telemetry:
        telemetry.record(
            variant=variant,
            task_id=task_id,
            run_no=run_no,
            turn_no=1,
            model=model,
            response=result,
            skill_sha256=None,
            tools_called=[],
            tool_output_chars=0,
            breakdown=None,
            error=result.get("error") if "error" in result else None,
        )

    if "error" in result:
        return judge_error(f"Judge call failed: {result['error']}")

    candidates = result.get("candidates") or []
    if not candidates:
        return judge_error("Judge returned no candidates")

    output = "".join(p.get("text", "") for p in candidates[0].get("content", {}).get("parts", [])).strip()
    if "{" in output and "}" in output:
        json_str = output[output.find("{"):output.rfind("}") + 1]
        try:
            return normalize_verdict(json.loads(json_str))
        except json.JSONDecodeError:
            pass

    return judge_error("Failed to parse judge output: " + output)


# ---------------------------------------------------------------------------
# Telemetry: usage, attribution, pricing, quality, metrics (pure functions)
# ---------------------------------------------------------------------------

def usage_of(response):
    """Token counts from a Gemini response. Missing usage is flagged, never estimated."""
    usage = (response or {}).get("usageMetadata") or {}
    has_input = "promptTokenCount" in usage
    return {
        "input": int(usage.get("promptTokenCount", 0) or 0),
        "cached": int(usage.get("cachedContentTokenCount", 0) or 0),
        "output": int(usage.get("candidatesTokenCount", 0) or 0),
        "thinking": int(usage.get("thoughtsTokenCount", 0) or 0),
        "usage_missing": not has_input,
    }


def attribute(prompt_tokens, outputs, baseline_first=None, is_baseline=False):
    """Split each turn's input tokens into fixed / skill / model_replies / tool_outputs.

    prompt_tokens[k] is the provider's input count at turn k, outputs[k] its output count.
    fixed and skill are differences of provider counts. model_replies and tool_outputs
    split the growth between turns and are derived: a re-sent model message is assumed to
    cost the previous turn's output tokens. Each row sums exactly to prompt_tokens[k].
    """
    if not prompt_tokens:
        return []
    first = prompt_tokens[0]
    if is_baseline:
        fixed, skill, skill_known = first, 0, True
    elif baseline_first is None:
        fixed, skill, skill_known = first, 0, False
    else:
        fixed = min(baseline_first, first)
        skill, skill_known = first - fixed, True

    replies = tools = 0
    rows = []
    for k, total in enumerate(prompt_tokens):
        clamped = False
        row_fixed, row_skill = fixed, skill
        if k > 0:
            growth = total - prompt_tokens[k - 1]
            if growth >= 0:
                reply = min(growth, outputs[k - 1])
                replies += reply
                tools += growth - reply
            else:
                clamped = True
                replies = 0
                tools = max(0, total - fixed - skill)
        if row_fixed + row_skill + replies + tools != total:
            # Provider counts moved in a way the model cannot explain: fall back to one bucket.
            clamped = True
            row_fixed, row_skill, replies, tools = total, 0, 0, 0
            fixed, skill = total, 0
        rows.append({"fixed": row_fixed, "skill": row_skill, "model_replies": replies,
                     "tool_outputs": tools, "skill_known": skill_known, "derived_clamped": clamped})
    return rows


def load_pricing(path):
    """Read evals/pricing.json. A missing or invalid file means no prices, not a crash."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, ValueError):
        return {"version": None, "models": {}}
    if not isinstance(data, dict) or not isinstance(data.get("models"), dict):
        return {"version": None, "models": {}}
    return data


_warned_unpriced = set()


def price(tokens, model, pricing):
    """Cost in USD for one call, or None when the model has no price or usage is missing."""
    if tokens.get("usage_missing"):
        return None
    models = (pricing or {}).get("models") or {}
    entry = models.get(model)
    rate_in = entry.get("input_per_million") if isinstance(entry, dict) else None
    rate_out = entry.get("output_per_million") if isinstance(entry, dict) else None
    if rate_in is None or rate_out is None:
        if model not in _warned_unpriced:
            _warned_unpriced.add(model)
            print(f"[WARN] No price for model {model} in evals/pricing.json; cost is UNPRICED.", file=sys.stderr)
        return None
    rate_cached = entry.get("cached_input_per_million")
    if rate_cached is None:
        rate_cached = rate_in
    cached = min(tokens.get("cached", 0), tokens.get("input", 0))
    cost = ((tokens.get("input", 0) - cached) * rate_in + cached * rate_cached
            + (tokens.get("output", 0) + tokens.get("thinking", 0)) * rate_out) / 1_000_000
    return round(cost, 8)


def _valid_score(value):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    return float(value) if 0 <= value <= 100 else None


def quality_from_verdict(verdict, swapped, ref_variant, cand_variant):
    """Map the judge's first/second scores back to the variants. None means not scored."""
    scores = verdict.get("scores") if isinstance(verdict, dict) else None
    scores = scores if isinstance(scores, dict) else {}
    first, second = _valid_score(scores.get("first")), _valid_score(scores.get("second"))
    ref, cand = (second, first) if swapped else (first, second)
    return {ref_variant: ref, cand_variant: cand}


def _mean(values):
    values = [v for v in values if v is not None]
    return sum(values) / len(values) if values else None


class Telemetry:
    """Manages append-only JSONL telemetry logging per eval run."""

    def __init__(self, path, context=None, pricing=None):
        self.path = Path(path)
        self.context = dict(context or {})
        self.pricing = pricing or {"models": {}}
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._f = open(self.path, "a", encoding="utf-8")

    def record(self, *, variant, task_id, run_no, turn_no, model,
               response, skill_sha256=None, tools_called=(), tool_output_chars=0,
               breakdown=None, error=None):
        tokens = usage_of(response)
        if breakdown is not None:
            tokens["breakdown"] = breakdown

        meta = (response or {}).pop("_meta", None) or {}
        latency_ms = meta.get("latency_ms", 0)
        retries = meta.get("retries", 0)
        actual_model = meta.get("model", model)

        err_text = None
        if error:
            err_text = str(error)[:ERROR_TEXT_LIMIT]
        elif response and "error" in response:
            err_text = str(response["error"])[:ERROR_TEXT_LIMIT]
        if err_text:
            err_text = re.sub(r'AIza[0-9A-Za-z-_]{35}', '[REDACTED]', err_text)
            err_text = re.sub(r'(?:api_key|key|token)=([^\s&]+)', r'key=[REDACTED]', err_text)

        cost = price(tokens, actual_model, self.pricing)

        rec = {
            "schema_version": SCHEMA_VERSION,
            "evaluator_version": str(EVALUATOR_VERSION),
            "run_id": self.context.get("run_id", ""),
            "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "git_sha": self.context.get("git_sha", ""),
            "baseline_ref": self.context.get("baseline_ref", ""),
            "skill": self.context.get("skill", ""),
            "skill_sha256": skill_sha256,
            "task_id": task_id,
            "variant": variant,
            "run_no": run_no,
            "turn_no": turn_no,
            "model": actual_model,
            "status": "ERROR" if err_text else "SUCCESS",
            "error": err_text,
            "latency_ms": latency_ms,
            "retries": retries,
            "tokens": tokens,
            "cost_usd": cost,
            "tools_called": list(tools_called or []),
            "tool_output_chars": int(tool_output_chars or 0),
        }

        line = json.dumps(rec, ensure_ascii=False)
        self._f.write(line + "\n")
        self._f.flush()
        return rec

    def close(self):
        if hasattr(self, "_f") and not self._f.closed:
            self._f.close()


def read_records(path):
    records = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records


AGENT_VARIANTS = ("baseline", "old", "new")


def summarize(records, quality, pass_scores):
    """Efficiency metrics from telemetry records and quality samples.

    quality: list of {"task_id", "run_no", "variant", "q"}; pass_scores: {task_id: threshold}.
    Judge calls are summed apart and never enter token or cost figures of a variant.
    """
    agent = [r for r in records if r["variant"] in AGENT_VARIANTS]
    judge = [r for r in records if r["variant"] not in AGENT_VARIANTS]

    q_by_sample = {}
    for item in quality:
        if item["q"] is not None:
            q_by_sample.setdefault((item["variant"], item["task_id"], item["run_no"]), []).append(item["q"])
    q_by_sample = {k: sum(v) / len(v) for k, v in q_by_sample.items()}

    variants = {}
    for variant in AGENT_VARIANTS:
        recs = [r for r in agent if r["variant"] == variant]
        samples = {}
        for r in recs:
            samples.setdefault((r["task_id"], r["run_no"]), []).append(r)
        if not samples:
            continue
        per_sample_tokens = [sum(x["tokens"]["input"] + x["tokens"]["output"] + x["tokens"]["thinking"] for x in rs)
                             for rs in samples.values()]
        breakdown = {k: 0 for k in ("fixed", "skill", "model_replies", "tool_outputs")}
        for r in recs:
            for k in breakdown:
                breakdown[k] += (r["tokens"].get("breakdown") or {}).get(k, 0)
        qs = {key: q for key, q in q_by_sample.items() if key[0] == variant}
        successes = sum(1 for (_, task_id, _), q in qs.items() if q >= pass_scores.get(task_id, DEFAULT_PASS_SCORE))
        costs = [r["cost_usd"] for r in recs]
        cost = None if any(c is None for c in costs) else sum(costs)
        variants[variant] = {
            "samples": len(samples),
            "tokens_per_sample": sum(per_sample_tokens) / len(per_sample_tokens),
            "input_breakdown_per_sample": {k: v / len(samples) for k, v in breakdown.items()},
            "quality": _mean(list(qs.values())),
            "scored_samples": len(qs),
            "success_rate": (successes / len(qs)) if qs else None,
            "cost": cost,
            "cost_per_success": (cost / successes) if (cost is not None and successes) else None,
            "usage_missing": sum(1 for r in recs if r["tokens"]["usage_missing"]),
            "errors": sum(1 for r in recs if r["status"] != "SUCCESS"),
        }

    delta_t = delta_q = efficiency = None
    saves_tokens = False
    paired = [(q_by_sample[("new", t, n)] - q_by_sample[("baseline", t, n)])
              for (v, t, n) in q_by_sample if v == "new" and ("baseline", t, n) in q_by_sample]
    if "new" in variants and "baseline" in variants:
        delta_t = variants["new"]["tokens_per_sample"] - variants["baseline"]["tokens_per_sample"]
    if paired:
        delta_q = sum(paired) / len(paired)
    if delta_q is not None and delta_t is not None:
        if delta_t > 0:
            efficiency = delta_q / delta_t * 1000
        elif delta_q >= 0:
            saves_tokens = True

    judge_costs = [r["cost_usd"] for r in judge]
    return {
        "variants": variants,
        "delta_tokens": delta_t,
        "delta_quality": delta_q,
        "efficiency": efficiency,
        "saves_tokens": saves_tokens,
        "paired_samples": len(paired),
        "judge_calls": len(judge),
        "judge_tokens": sum(r["tokens"]["input"] + r["tokens"]["output"] + r["tokens"]["thinking"] for r in judge),
        "judge_cost": None if (not judge or any(c is None for c in judge_costs)) else sum(judge_costs),
    }


def recommend(summary):
    """Advisory recommendation and the reason. Never changes the exit code."""
    dq, dt = summary["delta_quality"], summary["delta_tokens"]
    if summary["paired_samples"] < MIN_PAIRED_SAMPLES or dq is None or dt is None:
        return "INSUFFICIENT_DATA", f"needs at least {MIN_PAIRED_SAMPLES} samples scored for both no-skill and new (have {summary['paired_samples']})"
    if dq <= 0:
        return "REGRESSION", "no better than using no skill"
    if dq >= GAIN_STRONG and dt <= TOKENS_ACCEPTABLE:
        return "KEEP", "clear quality gain at acceptable token cost"
    if dq >= GAIN_STRONG:
        return "OPTIMIZE", "clear quality gain, but expensive in tokens"
    if dt <= TOKENS_CHEAP:
        return "KEEP", "small gain, cheap"
    return "REVIEW", "small gain, expensive in tokens"


VALID_STATUSES = ("WORSE", "SAME", "BETTER")


def judge_error(reason):
    """A judge that could not give a verdict is an ERROR, never a silent SAME."""
    return {"score": 0, "status": "ERROR", "reasoning": reason}


def normalize_verdict(verdict):
    """Accept only a dict whose status is WORSE, SAME or BETTER; anything else fails closed."""
    if not isinstance(verdict, dict) or verdict.get("status") not in VALID_STATUSES:
        return judge_error(f"Judge returned an invalid verdict: {verdict!r}")
    return verdict


def invert_verdict(verdict):
    """Flip a verdict when the two outputs were shown to the judge in swapped order."""
    flipped = {"WORSE": "BETTER", "BETTER": "WORSE"}.get(verdict.get("status"), verdict.get("status"))
    score = verdict.get("score", 0)
    return {**verdict, "status": flipped, "score": -score if isinstance(score, (int, float)) else score}


def compare(reference_res, candidate_res, rubric, model, root_dir, prefix, rng,
            telemetry=None, task_id="inline_task", run_no=1, variant="judge_old_new",
            ref_variant="old", cand_variant="new"):
    """Judge `candidate_res` relative to `reference_res`.

    The presentation order is randomized so a judge that favors the first or the
    second answer cannot bias every comparison the same way.
    """
    swapped = rng.random() < 0.5
    if swapped:
        raw_verdict = judge_results(candidate_res, reference_res, rubric, model, root_dir, prefix=prefix,
                                    telemetry=telemetry, task_id=task_id, run_no=run_no, variant=variant)
        verdict = invert_verdict(raw_verdict)
        verdict["reasoning"] = "(shown in swapped order) " + str(verdict.get("reasoning", ""))
    else:
        raw_verdict = judge_results(reference_res, candidate_res, rubric, model, root_dir, prefix=prefix,
                                    telemetry=telemetry, task_id=task_id, run_no=run_no, variant=variant)
        verdict = raw_verdict

    verdict["quality"] = quality_from_verdict(raw_verdict, swapped, ref_variant, cand_variant)
    return verdict


def aggregate_runs(statuses):
    """Combine the verdicts of repeated runs. Any ERROR fails closed; otherwise a strict majority decides."""
    if not statuses or "ERROR" in statuses:
        return "ERROR"
    counts = Counter(statuses)
    if counts["WORSE"] * 2 > len(statuses):
        return "WORSE"
    if counts["BETTER"] * 2 > len(statuses):
        return "BETTER"
    return "SAME"


def overall_status(verdicts):
    """Overall result from per-task verdicts; None means that comparison was not run.

    ERROR beats WORSE beats UNVERIFIED: a result that was not measured must never read as a pass.
    """
    flat = [v for v in verdicts if v is not None]
    if "ERROR" in flat:
        return "ERROR"
    if "WORSE" in flat:
        return "WORSE"
    if not flat:
        return "UNVERIFIED"
    return "BETTER" if "BETTER" in flat else "SAME"


def exit_code(status, strict=False):
    if status in ("ERROR", "WORSE"):
        return 1
    if status == "UNVERIFIED":
        return 1 if strict else 0
    return 0


def load_baseline(root_dir, rel_path, ref):
    """Return the text of `rel_path` at git `ref`, or raise RuntimeError."""
    if not ref or ref.startswith("-"):
        raise RuntimeError(f"invalid baseline ref: {ref!r}")
    res = subprocess.run(["git", "show", f"{ref}:{rel_path}"], cwd=root_dir, capture_output=True, text=True)
    if res.returncode != 0:
        raise RuntimeError(f"cannot read {rel_path} at {ref}: {res.stderr.strip()}")
    return res.stdout


def load_tasks(root_dir, skill_name):
    eval_dir = root_dir / 'evals' / 'golden' / skill_name
    tasks = []
    if eval_dir.is_dir():
        for task_file in sorted(eval_dir.glob("*.yaml")):
            with open(task_file, 'r') as f:
                task = yaml.safe_load(f)
                task['name'] = task_file.name
                tasks.append(task)
    return tasks


def coverage(root_dir):
    """Return (covered, missing) skill names, by presence of golden task files."""
    covered, missing = [], []
    for skill_md in sorted((root_dir / 'skills').glob('*/SKILL.md')):
        name = skill_md.parent.name
        has_tasks = any((root_dir / 'evals' / 'golden' / name).glob('*.yaml'))
        (covered if has_tasks else missing).append(name)
    return covered, missing


def format_telemetry_report(records, summary, rec_verdict, rec_reason, run_context):
    lines = []
    lines.append("## Telemetry & Efficiency Summary")
    lines.append(f"- **Run ID**: `{run_context.get('run_id')}`")
    lines.append(f"- **Git SHA**: `{run_context.get('git_sha')}`")
    lines.append(f"- **Baseline Ref**: `{run_context.get('baseline_ref')}`")
    lines.append(f"- **Evaluator Version**: {EVALUATOR_VERSION}")
    lines.append(f"- **Pricing Version**: {run_context.get('pricing_version') or 'None'}")
    lines.append(f"- **Trace Log**: [{run_context.get('telemetry_file')}]({run_context.get('telemetry_file')})")
    lines.append("")

    lines.append(f"### Advisory Recommendation: **{rec_verdict}**")
    lines.append(f"> {rec_reason}")
    lines.append("")

    lines.append("### Efficiency & ROI Metrics")
    lines.append("| Metric | Baseline (No skill) | Old Skill | New Skill | Delta (New vs Base) |")
    lines.append("|---|---|---|---|---|")
    v = summary.get("variants", {})
    b_tokens = f"{v['baseline']['tokens_per_sample']:.0f}" if 'baseline' in v else "-"
    o_tokens = f"{v['old']['tokens_per_sample']:.0f}" if 'old' in v else "-"
    n_tokens = f"{v['new']['tokens_per_sample']:.0f}" if 'new' in v else "-"
    dt = f"{summary['delta_tokens']:+.0f}" if summary.get("delta_tokens") is not None else "-"
    lines.append(f"| **Tokens / sample** | {b_tokens} | {o_tokens} | {n_tokens} | {dt} |")

    b_q = f"{v['baseline']['quality']:.1f}" if 'baseline' in v and v['baseline']['quality'] is not None else "-"
    o_q = f"{v['old']['quality']:.1f}" if 'old' in v and v['old']['quality'] is not None else "-"
    n_q = f"{v['new']['quality']:.1f}" if 'new' in v and v['new']['quality'] is not None else "-"
    dq = f"{summary['delta_quality']:+.1f}" if summary.get("delta_quality") is not None else "-"
    lines.append(f"| **Quality Score (0-100)** | {b_q} | {o_q} | {n_q} | {dq} |")

    b_sr = f"{v['baseline']['success_rate']*100:.0f}%" if 'baseline' in v and v['baseline']['success_rate'] is not None else "-"
    o_sr = f"{v['old']['success_rate']*100:.0f}%" if 'old' in v and v['old']['success_rate'] is not None else "-"
    n_sr = f"{v['new']['success_rate']*100:.0f}%" if 'new' in v and v['new']['success_rate'] is not None else "-"
    lines.append(f"| **Success Rate** | {b_sr} | {o_sr} | {n_sr} | - |")

    eff = f"{summary['efficiency']:.2f}" if summary.get("efficiency") is not None else ("saves tokens" if summary.get("saves_tokens") else "-")
    lines.append(f"| **Quality / 1K Tokens** | - | - | - | {eff} |")

    b_cps = f"${v['baseline']['cost_per_success']:.4f}" if 'baseline' in v and v['baseline']['cost_per_success'] is not None else ("UNPRICED" if 'baseline' in v and v['baseline']['cost'] is None else "-")
    o_cps = f"${v['old']['cost_per_success']:.4f}" if 'old' in v and v['old']['cost_per_success'] is not None else ("UNPRICED" if 'old' in v and v['old']['cost'] is None else "-")
    n_cps = f"${v['new']['cost_per_success']:.4f}" if 'new' in v and v['new']['cost_per_success'] is not None else ("UNPRICED" if 'new' in v and v['new']['cost'] is None else "-")
    lines.append(f"| **Cost / Success** | {b_cps} | {o_cps} | {n_cps} | - |")
    lines.append("")

    lines.append("### Input Token Attribution (Mean per sample)")
    lines.append("| Variant | Fixed Prompt | Skill Body | Model Replies | Tool Outputs | Total Input |")
    lines.append("|---|---|---|---|---|---|")
    for var in ("baseline", "old", "new"):
        if var in v:
            bd = v[var]["input_breakdown_per_sample"]
            tot = sum(bd.values())
            lines.append(f"| **{var}** | {bd.get('fixed', 0):.0f} | {bd.get('skill', 0):.0f} | {bd.get('model_replies', 0):.0f} | {bd.get('tool_outputs', 0):.0f} | {tot:.0f} |")
    lines.append("")

    lines.append("### Cost Summary (USD)")
    lines.append("| Category | Tokens | Cost (USD) |")
    lines.append("|---|---|---|")
    for var in ("baseline", "old", "new"):
        if var in v:
            c = f"${v[var]['cost']:.4f}" if v[var]['cost'] is not None else "UNPRICED"
            lines.append(f"| Agent: {var} | {v[var]['tokens_per_sample']*v[var]['samples']:.0f} | {c} |")
    jc = f"${summary['judge_cost']:.4f}" if summary.get("judge_cost") is not None else "UNPRICED"
    lines.append(f"| LLM Judge ({summary['judge_calls']} calls) | {summary['judge_tokens']} | {jc} |")
    lines.append("")

    return lines


def format_turns(label, turns):
    lines = [f"#### {label}: tokens per turn", "| Turn | In | Out | Tools |", "|---|---|---|---|"]
    for t in turns:
        lines.append(f"| {t['turn']} | {t['in']} | {t['out']} | {', '.join(t['tools']) or '-'} |")
    return lines


def find_skill_dir(root_dir, skill_name):
    p = root_dir / 'skills' / skill_name
    if p.exists():
        return p
    return None


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Run golden evaluation for a skill.")
    parser.add_argument("skill_name", nargs="?", help="Name of the skill to evaluate")
    parser.add_argument("--prompt", help="Inline prompt to test without needing a task.yaml", default=None)
    parser.add_argument("--fast", action="store_true", help="Run only the new version; nothing is compared, so the result is UNVERIFIED")
    parser.add_argument("--baseline", default="HEAD", help="Git ref holding the old skill version (default: HEAD; use HEAD~1 or a tag after committing)")
    parser.add_argument("--runs", type=int, default=1, help="Repeat each task N times; the verdict is the majority of the runs")
    parser.add_argument("--strict", action="store_true", help="Treat an unverified result (no golden tasks, --fast, missing baseline) as a failure")
    parser.add_argument("--coverage", action="store_true", help="List which skills have golden tasks and exit; with --strict, fail if any is missing")
    args = parser.parse_args()

    root_dir = Path(__file__).resolve().parent.parent

    if args.coverage:
        covered, missing = coverage(root_dir)
        print(f"Golden task coverage: {len(covered)}/{len(covered) + len(missing)} skills")
        print("Covered: " + (", ".join(covered) or "(none)"))
        print("Missing: " + (", ".join(missing) or "(none)"))
        sys.exit(1 if (args.strict and missing) else 0)

    if not args.skill_name:
        parser.error("skill_name is required unless --coverage is given")
    if args.runs < 1:
        parser.error("--runs must be at least 1")

    skill_name = args.skill_name
    skill_dir = find_skill_dir(root_dir, skill_name)

    if not skill_dir:
        print(f"Skill {skill_name} not found.")
        sys.exit(1)

    skill_md = skill_dir / 'SKILL.md'
    with open(skill_md, 'r') as f:
        new_content = f.read()

    if args.prompt:
        tasks = [{
            'name': 'inline_task',
            'prompt': args.prompt,
            'rubric': [
                {'name': 'Skill Adherence', 'weight': 2, 'description': 'Did the output strictly adhere to the system instructions and formatting rules of the skill?'},
                {'name': 'Task Completion', 'weight': 1, 'description': 'Did the output successfully complete the user prompt?'}
            ]
        }]
    else:
        tasks = load_tasks(root_dir, skill_name)
        if not tasks:
            print(f"NO COVERAGE: {skill_name} has no golden tasks in evals/golden/{skill_name}/. Nothing was evaluated.")
            sys.exit(exit_code("UNVERIFIED", args.strict))

    # Old version comes straight from git; the working-tree SKILL.md is never touched.
    old_content = None
    if not args.fast:
        try:
            old_content = load_baseline(root_dir, skill_md.relative_to(root_dir), args.baseline)
        except RuntimeError as e:
            print(f"UNVERIFIED: {e}. Nothing was evaluated.")
            sys.exit(exit_code("UNVERIFIED", args.strict))
        if old_content == new_content:
            print(f"WARNING: the skill at {args.baseline} is identical to the working copy, so Old vs New proves nothing. Pass --baseline <earlier ref>.", flush=True)

    pricing = load_pricing(root_dir / 'evals' / 'pricing.json')
    try:
        res = subprocess.run(["git", "rev-parse", "HEAD"], cwd=root_dir, capture_output=True, text=True)
        git_sha = res.stdout.strip() if res.returncode == 0 else "unknown"
    except Exception:
        git_sha = "unknown"

    run_id = f"{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S')}-{secrets.token_hex(2)}"
    telemetry_path = root_dir / 'docs' / 'reports' / f"eval-telemetry-{run_id}.jsonl"
    run_context = {
        "run_id": run_id,
        "git_sha": git_sha,
        "baseline_ref": args.baseline,
        "skill": skill_name,
        "pricing_version": pricing.get("version"),
        "telemetry_file": str(telemetry_path.relative_to(root_dir)),
    }
    try:
        telemetry = Telemetry(telemetry_path, context=run_context, pricing=pricing)
    except OSError as e:
        print(f"FATAL ERROR: cannot open telemetry file {telemetry_path}: {e}", file=sys.stderr)
        sys.exit(1)

    new_sha = hashlib.sha256(new_content.encode('utf-8')).hexdigest()
    old_sha = hashlib.sha256(old_content.encode('utf-8')).hexdigest() if old_content else None

    rng = random.Random()
    workspace = tempfile.mkdtemp(prefix="golden-eval-")
    fixtures_dir = root_dir / 'evals' / 'golden' / 'fixtures'
    verdicts = []
    quality_samples = []
    pass_scores = {}
    try:
        if fixtures_dir.exists():
            for item in fixtures_dir.iterdir():
                if item.is_dir():
                    shutil.copytree(item, Path(workspace) / item.name)
                else:
                    shutil.copy2(item, workspace)

        report_lines = [f"# Golden Eval Report: {skill_name}", f"Date: {datetime.now().isoformat()}",
                        f"Baseline ref: {args.baseline}", f"Runs per task: {args.runs}", ""]

        print(f"Starting golden evaluation for skill: {skill_name}...", flush=True)

        for task in tasks:
            task_id = task['name']
            pass_scores[task_id] = task.get('pass_score', DEFAULT_PASS_SCORE)
            print(f"\nEvaluating task: {task_id}...", flush=True)

            prompt = task['prompt']
            rubric = task['rubric']
            judge_model = task.get('judge_model') or DEFAULT_MODEL
            print(f"Using judge model: {judge_model}", flush=True)

            old_statuses, base_statuses = [], []
            old_notes, base_notes = [], []
            tokens = {"base": [0, 0], "old": [0, 0], "new": [0, 0]}
            new_turns = []

            for run_no in range(1, args.runs + 1):
                tag = f"r{run_no}_"
                fixed_tokens = None
                if not args.fast:
                    print(f"  - [run {run_no}/{args.runs}] BASELINE (no skill)...", flush=True)
                    baseline_res, b_in, b_out, _, fixed_tokens = run_agent(
                        prompt, workspace, root_dir, skill_content="", prefix=tag + "baseline_",
                        telemetry=telemetry, variant="baseline", task_id=task_id, run_no=run_no,
                        fixed_tokens=None, skill_sha256=None
                    )
                    if baseline_res.startswith("ERROR:"):
                        print(f"\n[FATAL ERROR] {baseline_res}\nEvaluation aborted to save quota.", flush=True)
                        sys.exit(1)

                    print(f"  - [run {run_no}/{args.runs}] OLD version (from {args.baseline})...", flush=True)
                    old_res, o_in, o_out, _, _ = run_agent(
                        prompt, workspace, root_dir, old_content, prefix=tag + "old_",
                        telemetry=telemetry, variant="old", task_id=task_id, run_no=run_no,
                        fixed_tokens=fixed_tokens, skill_sha256=old_sha
                    )
                    if old_res.startswith("ERROR:"):
                        print(f"\n[FATAL ERROR] {old_res}\nEvaluation aborted to save quota.", flush=True)
                        sys.exit(1)
                    tokens["base"][0] += b_in; tokens["base"][1] += b_out
                    tokens["old"][0] += o_in; tokens["old"][1] += o_out

                print(f"  - [run {run_no}/{args.runs}] NEW version (local changes)...", flush=True)
                new_res, n_in, n_out, turns, _ = run_agent(
                    prompt, workspace, root_dir, new_content, prefix=tag + "new_",
                    telemetry=telemetry, variant="new", task_id=task_id, run_no=run_no,
                    fixed_tokens=fixed_tokens if not args.fast else None, skill_sha256=new_sha
                )
                if new_res.startswith("ERROR:"):
                    print(f"\n[FATAL ERROR] {new_res}\nEvaluation aborted to save quota.", flush=True)
                    sys.exit(1)
                tokens["new"][0] += n_in; tokens["new"][1] += n_out
                if run_no == 1:
                    new_turns = turns

                if not args.fast:
                    print(f"  - [run {run_no}/{args.runs}] judging Old vs New...", flush=True)
                    judge = compare(
                        old_res, new_res, rubric, judge_model, root_dir, tag + "judge_old_new_", rng,
                        telemetry=telemetry, task_id=task_id, run_no=run_no, variant="judge_old_new",
                        ref_variant="old", cand_variant="new"
                    )
                    print(f"  - [run {run_no}/{args.runs}] judging Baseline vs New...", flush=True)
                    judge_base = compare(
                        baseline_res, new_res, rubric, judge_model, root_dir, tag + "judge_base_new_", rng,
                        telemetry=telemetry, task_id=task_id, run_no=run_no, variant="judge_base_new",
                        ref_variant="baseline", cand_variant="new"
                    )
                    for v in (judge, judge_base):
                        if v["status"] == "ERROR":
                            print(f"\n[FATAL ERROR] {v.get('reasoning')}\nEvaluation aborted to save quota.", flush=True)
                            sys.exit(1)
                    old_statuses.append(judge["status"]); old_notes.append(judge.get("reasoning", ""))
                    base_statuses.append(judge_base["status"]); base_notes.append(judge_base.get("reasoning", ""))

                    if "quality" in judge:
                        q_map = judge["quality"]
                        quality_samples.append({"task_id": task_id, "run_no": run_no, "variant": "old", "q": q_map.get("old")})
                        quality_samples.append({"task_id": task_id, "run_no": run_no, "variant": "new", "q": q_map.get("new")})
                    if "quality" in judge_base:
                        q_base_map = judge_base["quality"]
                        quality_samples.append({"task_id": task_id, "run_no": run_no, "variant": "baseline", "q": q_base_map.get("baseline")})
                        quality_samples.append({"task_id": task_id, "run_no": run_no, "variant": "new", "q": q_base_map.get("new")})

            old_verdict = aggregate_runs(old_statuses) if old_statuses else None
            base_verdict = aggregate_runs(base_statuses) if base_statuses else None
            verdicts.extend([old_verdict, base_verdict])

            report_lines.append(f"## Task: {task['name']}")
            if args.fast:
                report_lines.append("**Not evaluated**: --fast skips every comparison, so this task is UNVERIFIED.")
            else:
                report_lines.append(f"**Status (Old vs New)**: {old_verdict} (runs: {', '.join(old_statuses)})")
                report_lines.append(f"**Reasoning**: {old_notes[0]}")
                report_lines.append("")
                report_lines.append(f"**Status (Baseline vs New)**: {base_verdict} (runs: {', '.join(base_statuses)})")
                report_lines.append(f"**Baseline Reasoning**: {base_notes[0]}")
            report_lines.append("")
            report_lines.append("### Token Usage (summed over runs)")
            report_lines.append(f"- **Baseline**: {tokens['base'][0]} in, {tokens['base'][1]} out")
            report_lines.append(f"- **Old Skill**: {tokens['old'][0]} in, {tokens['old'][1]} out")
            report_lines.append(f"- **New Skill**: {tokens['new'][0]} in, {tokens['new'][1]} out")
            if tokens["old"][1] > 0:
                report_lines.append(f"- **Output Savings (New vs Old)**: {(1 - tokens['new'][1] / tokens['old'][1]) * 100:.1f}%")
            if tokens["base"][1] > 0:
                report_lines.append(f"- **Output Savings (New vs Baseline)**: {(1 - tokens['new'][1] / tokens['base'][1]) * 100:.1f}%")
            if tokens["old"][0] > 0:
                report_lines.append(f"- **Input Savings (New vs Old)**: {(1 - tokens['new'][0] / tokens['old'][0]) * 100:.1f}%")
            report_lines.append("")
            report_lines.extend(format_turns("New skill (run 1)", new_turns))
            report_lines.append("")

        status = overall_status(verdicts)
        print(f"\nEvaluation finished. Total API Calls made: {llm_call_count}", flush=True)
    finally:
        telemetry.close()
        shutil.rmtree(workspace, ignore_errors=True)

    records = read_records(telemetry_path)
    summary = summarize(records, quality_samples, pass_scores)
    rec_verdict, rec_reason = recommend(summary)

    report_lines.insert(3, f"Overall status: {status}")
    report_lines.extend(format_telemetry_report(records, summary, rec_verdict, rec_reason, run_context))

    report_path = root_dir / 'docs' / 'reports' / f"EVAL-{skill_name}-{run_id}.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(report_lines))

    print(f"Eval completed. Status: {status}. Report saved to {report_path}")
    print(f"Advisory Recommendation: {rec_verdict} ({rec_reason})", flush=True)
    sys.exit(exit_code(status, args.strict))


if __name__ == '__main__':
    main()
