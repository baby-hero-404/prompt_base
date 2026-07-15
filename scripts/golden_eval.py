#!/usr/bin/env python3
import sys
import json
import re
import yaml
import tempfile
import shutil
from pathlib import Path
from datetime import datetime

import urllib.request
import urllib.error
import os
import time

DEFAULT_MODEL = os.environ.get("GEMINI_MODEL", "gemini-3.1-flash-lite")
MAX_TOOL_TURNS = 10

# Global counter to track API calls
llm_call_count = 0

FUNCTION_DECLARATIONS = [
    {
        "name": "read_file",
        "description": "Read the full contents of a file in the workspace.",
        "parameters": {
            "type": "object",
            "properties": {"path": {"type": "string", "description": "Path relative to the workspace root."}},
            "required": ["path"],
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
            with urllib.request.urlopen(req, timeout=120) as response:
                res_json = json.loads(response.read().decode('utf-8'))
                _save_res(res_json)
                return res_json
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt < 5:
                time.sleep(min(60, 5 * (attempt + 1)))  # 5,10,15,20,25s
                continue
            _save_res(None, f"HTTPError: {e}")
            return {"error": f"Gemini API call failed: {e}"}
        except urllib.error.URLError as e:
            _save_res(None, f"URLError: {e}")
            return {"error": f"Gemini API call failed: {e}"}
            
    _save_res(None, "Exhausted retries on 429")
    return {"error": "Gemini API call failed: exhausted retries on 429"}


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
            return p.read_text(errors="replace")[:20000]

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


def run_agent(prompt, workspace, root_dir, skill_content, prefix=""):
    """Runs the skill under test as a real tool-using agent, scoped to `workspace`."""
    
    global_instruction = "CRITICAL: Always use parallel tool calls when you need to read multiple files or fetch multiple resources at the same time to save API turns."
    final_instruction = f"{global_instruction}\n\n{skill_content}" if skill_content else global_instruction
    
    tools = [{"functionDeclarations": FUNCTION_DECLARATIONS}]
    contents = [{"role": "user", "parts": [{"text": prompt}]}]
    total_in_tokens = 0
    total_out_tokens = 0

    for _ in range(MAX_TOOL_TURNS): # Use the defined maximum tool turns (6)
        result = gemini_generate(contents, root_dir, system_instruction=final_instruction, tools=tools, prefix=prefix)
        if "error" in result:
            return f"ERROR: {result['error']}", total_in_tokens, total_out_tokens

        usage = result.get("usageMetadata", {})
        total_in_tokens += usage.get("promptTokenCount", 0)
        total_out_tokens += usage.get("candidatesTokenCount", 0)

        candidates = result.get("candidates")
        if not candidates:
            return f"ERROR: no candidates returned. Raw response: {json.dumps(result)}", total_in_tokens, total_out_tokens

        parts = candidates[0].get("content", {}).get("parts", [])
        contents.append({"role": "model", "parts": parts})

        function_calls = [p["functionCall"] for p in parts if "functionCall" in p]
        if not function_calls:
            texts = [p.get("text", "") for p in parts if "text" in p]
            joined = "\n".join(t for t in texts if t)
            return joined or f"ERROR: model returned no text and no tool calls. Raw candidate: {json.dumps(candidates[0])}", total_in_tokens, total_out_tokens

        response_parts = []
        for fc in function_calls:
            print(f"      * Tool call: {fc.get('name')}", flush=True)
            output = execute_tool(fc.get("name"), fc.get("args", {}) or {}, workspace)
            response_parts.append({
                "functionResponse": {"name": fc.get("name"), "response": {"result": output}}
            })
        contents.append({"role": "user", "parts": response_parts})

    return "ERROR: exceeded max tool turns without a final answer", total_in_tokens, total_out_tokens


def judge_results(old_res, new_res, rubric, model, root_dir, prefix=""):
    template_path = root_dir / 'evals' / 'golden' / 'judge_template.txt'
    with open(template_path, 'r') as f:
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
    if "error" in result:
        return {"score": 0, "status": "SAME", "reasoning": f"Judge call failed: {result['error']}"}

    candidates = result.get("candidates") or []
    if not candidates:
        return {"score": 0, "status": "SAME", "reasoning": "Judge returned no candidates"}

    output = "".join(p.get("text", "") for p in candidates[0].get("content", {}).get("parts", [])).strip()
    if "{" in output and "}" in output:
        json_str = output[output.find("{"):output.rfind("}") + 1]
        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            pass

    return {"score": 0, "status": "SAME", "reasoning": "Failed to parse judge output: " + output}


def find_skill_dir(root_dir, skill_name):
    for cat in ['core', 'tech', 'process', 'custom']:
        p = root_dir / 'antigravity' / 'skills' / cat / skill_name
        if p.exists():
            return p
    return None


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Run golden evaluation for a skill.")
    parser.add_argument("skill_name", help="Name of the skill to evaluate")
    parser.add_argument("--prompt", help="Inline prompt to test without needing a task.yaml", default=None)
    args = parser.parse_args()

    skill_name = args.skill_name
    root_dir = Path(__file__).resolve().parent.parent
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
        eval_dir = root_dir / 'evals' / 'golden' / skill_name
        if not eval_dir.exists():
            print(f"No golden tasks found for {skill_name} at {eval_dir}. Skipping golden eval.")
            sys.exit(0)
            
        tasks = []
        for task_file in sorted(eval_dir.glob("*.yaml")):
            with open(task_file, 'r') as f:
                task = yaml.safe_load(f)
                task['name'] = task_file.name
                tasks.append(task)

    # Old version comes straight from git — the working-tree SKILL.md is never touched.
    try:
        rel_path = skill_md.relative_to(root_dir)
        import subprocess
        res = subprocess.run(["git", "show", f"HEAD:{rel_path}"], cwd=root_dir, capture_output=True, text=True, check=True)
        old_content = res.stdout
    except Exception:
        print("Failed to get HEAD version from git. Skipping.")
        sys.exit(0)

    workspace = tempfile.mkdtemp(prefix="golden-eval-")
    fixtures_dir = root_dir / 'evals' / 'golden' / 'fixtures'
    try:
        if fixtures_dir.exists():
            for item in fixtures_dir.iterdir():
                if item.is_dir():
                    shutil.copytree(item, Path(workspace) / item.name)
                else:
                    shutil.copy2(item, workspace)

        report_lines = [f"# Golden Eval Report: {skill_name}", f"Date: {datetime.now().isoformat()}", ""]
        overall_status = "SAME"
        
        print(f"Starting golden evaluation for skill: {skill_name}...", flush=True)
        print(f"Using judge model: {DEFAULT_MODEL}", flush=True)

        for task in tasks:
            print(f"\nEvaluating task: {task['name']}...", flush=True)
            
            prompt = task['prompt']
            rubric = task['rubric']
            judge_model = task.get('judge_model') or DEFAULT_MODEL

            print(f"  - Running agent with BASELINE (no skill)...", flush=True)
            baseline_res, base_in, base_out = run_agent(prompt, workspace, root_dir, skill_content="", prefix="baseline_")
            if baseline_res.startswith("ERROR:"):
                print(f"\n[FATAL ERROR] {baseline_res}\nEvaluation aborted to save quota.", flush=True)
                sys.exit(1)

            print(f"  - Running agent with OLD version (from git HEAD)...", flush=True)
            old_res, old_in, old_out = run_agent(prompt, workspace, root_dir, old_content, prefix="old_")
            if old_res.startswith("ERROR:"):
                print(f"\n[FATAL ERROR] {old_res}\nEvaluation aborted to save quota.", flush=True)
                sys.exit(1)
            
            print(f"  - Running agent with NEW version (local changes)...", flush=True)
            new_res, new_in, new_out = run_agent(prompt, workspace, root_dir, new_content, prefix="new_")
            if new_res.startswith("ERROR:"):
                print(f"\n[FATAL ERROR] {new_res}\nEvaluation aborted to save quota.", flush=True)
                sys.exit(1)

            print(f"  - Judging results (Old vs New)...", flush=True)
            judge = judge_results(old_res, new_res, rubric, judge_model, root_dir, prefix="judge_old_new_")
            if judge.get('reasoning', '').startswith("Judge call failed:"):
                print(f"\n[FATAL ERROR] {judge.get('reasoning')}\nEvaluation aborted to save quota.", flush=True)
                sys.exit(1)

            print(f"  - Judging results (Baseline vs New)...", flush=True)
            judge_base = judge_results(baseline_res, new_res, rubric, judge_model, root_dir, prefix="judge_base_new_")

            status = judge.get('status', 'SAME')
            if status == 'WORSE':
                overall_status = 'WORSE'

            report_lines.append(f"## Task: {task['name']}")
            report_lines.append(f"**Status (Old vs New)**: {status}")
            report_lines.append(f"**Score**: {judge.get('score', 0)}")
            report_lines.append(f"**Reasoning**: {judge.get('reasoning', '')}")
            report_lines.append("")
            report_lines.append(f"**Status (Baseline vs New)**: {judge_base.get('status', 'SAME')}")
            report_lines.append(f"**Baseline Reasoning**: {judge_base.get('reasoning', '')}")
            report_lines.append("")
            report_lines.append(f"### Token Usage")
            report_lines.append(f"- **Baseline**: {base_in} in, {base_out} out")
            report_lines.append(f"- **Old Skill**: {old_in} in, {old_out} out")
            report_lines.append(f"- **New Skill**: {new_in} in, {new_out} out")
            
            if old_out > 0:
                savings = 1 - (new_out / old_out)
                report_lines.append(f"- **Output Savings (New vs Old)**: {savings * 100:.1f}%")
            if base_out > 0:
                savings_base = 1 - (new_out / base_out)
                report_lines.append(f"- **Output Savings (New vs Baseline)**: {savings_base * 100:.1f}%")
            if old_in > 0:
                in_savings = 1 - (new_in / old_in)
                report_lines.append(f"- **Input Savings (New vs Old)**: {in_savings * 100:.1f}%")
            report_lines.append("")
            
        print(f"\nEvaluation finished. Total API Calls made: {llm_call_count}", flush=True)
    finally:
        shutil.rmtree(workspace, ignore_errors=True)

    report_path = root_dir / 'docs' / 'reports' / f"EVAL-{skill_name}-{datetime.now().strftime('%Y%m%d%H%M%S')}.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    with open(report_path, 'w') as f:
        f.write('\n'.join(report_lines))

    print(f"Eval completed. Status: {overall_status}. Report saved to {report_path}")
    sys.exit(1 if overall_status == 'WORSE' else 0)


if __name__ == '__main__':
    main()
