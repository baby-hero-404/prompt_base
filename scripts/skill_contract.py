#!/usr/bin/env python3
import sys
import json
import re
import shutil
from pathlib import Path

def extract_clean_content(content):
    # Remove code blocks
    content = re.sub(r'```.*?```', '', content, flags=re.DOTALL)
    # Remove contract:ignore blocks
    content = re.sub(r'<!--\s*contract:ignore\s*-->.*?<!--\s*/contract:ignore\s*-->', '', content, flags=re.DOTALL)
    return content

def main():
    root_dir = Path(__file__).resolve().parent.parent
    registry_path = root_dir / 'registry.min.json'
    
    if not registry_path.exists():
        print("registry.min.json not found")
        sys.exit(1)
        
    with open(registry_path, 'r') as f:
        registry = json.load(f)
        
    valid_skills = set()
    for cat, skills in registry.get('skills', {}).items():
        for skill in skills:
            valid_skills.add(skill['name'])
            
    valid_agents = set()
    for agent in registry.get('agents', []):
        valid_agents.add(agent['name'])
        
    errors = 0
    warnings = 0
    
    skills_dir = root_dir / 'antigravity' / 'skills'
    for cat in ['core', 'tech', 'process', 'custom']:
        cat_dir = skills_dir / cat
        if not cat_dir.exists():
            continue
        for skill_dir in cat_dir.iterdir():
            if not skill_dir.is_dir():
                continue
                
            skill_md = skill_dir / 'SKILL.md'
            if not skill_md.exists():
                continue
                
            with open(skill_md, 'r') as f:
                content = f.read()
                
            # Extract allowed tools
            allowed_tools = set()
            if content.startswith('---'):
                end_fm = content.find('---', 3)
                if end_fm != -1:
                    fm_str = content[3:end_fm]
                    for line in fm_str.split('\n'):
                        if line.startswith('allowed-tools:'):
                            parts = line.split(':', 1)[1].split(',')
                            allowed_tools = {p.strip() for p in parts}
                            
            clean_content = extract_clean_content(content)
            
            # Verifies backtick repo paths exist
            paths = re.findall(r'`([a-zA-Z0-9_\-\./]+/[a-zA-Z0-9_\-\.]+)`', clean_content)
            for p in paths:
                if p.startswith('http') or '<' in p or '>' in p:
                    continue
                target_root = root_dir / p
                target_skill = skill_dir / p
                if not target_root.exists() and not target_skill.exists():
                    print(f"ERROR: Path `{p}` referenced in {skill_dir.name} does not exist.")
                    errors += 1
                    
            # Verifies referenced skills and agents
            refs = re.findall(r'\b([a-z0-9-]+)\s+(skill|agent)\b', clean_content, re.IGNORECASE)
            for ref_name, ref_type in refs:
                ref_name = ref_name.lower()
                
                # Heuristic: only check dangling references if they contain a hyphen 
                # (since most skill/agent names do, and it avoids catching "this skill", "a skill")
                if '-' not in ref_name:
                    continue
                    
                if ref_type.lower() == 'skill':
                    if ref_name not in valid_skills:
                        print(f"ERROR: Dangling reference to skill '{ref_name}' in {skill_dir.name}.")
                        errors += 1
                elif ref_type.lower() == 'agent':
                    if ref_name not in valid_agents:
                        print(f"ERROR: Dangling reference to agent '{ref_name}' in {skill_dir.name}.")
                        errors += 1
                        
            # Verifies named CLIs
            clis = re.findall(r'(?i)(Optional)?\s*CLI:\s*([a-zA-Z0-9_-]+)', clean_content)
            for optional, cli in clis:
                if not shutil.which(cli):
                    if optional:
                        print(f"WARN: Optional CLI '{cli}' not found in environment ({skill_dir.name}).")
                        warnings += 1
                    else:
                        print(f"ERROR: Required CLI '{cli}' not found in environment ({skill_dir.name}).")
                        errors += 1
                        
            # Verifies body-instructed tools (case sensitive to match exact tool names)
            tools = re.findall(r'use (?:the )?([A-Z][a-zA-Z/]+) tool', clean_content)
            for t in tools:
                if t not in allowed_tools:
                    print(f"ERROR: Body-instructed tool '{t}' not in allowed-tools of {skill_dir.name}.")
                    errors += 1

    if errors > 0:
        print(f"\nContract validation failed with {errors} errors and {warnings} warnings.")
        sys.exit(1)
    else:
        print(f"\nContract validation passed! ({warnings} warnings)")
        sys.exit(0)

if __name__ == '__main__':
    main()
