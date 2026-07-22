#!/usr/bin/env python3
import sys
import json
import yaml
from pathlib import Path

KNOWN_TOOLS = {"Read", "Write", "Edit", "Glob", "Grep", "Bash", "Agent", "RunCommand", "CreateFile"}

def lint_skill(skill_dir, registry_data, pre_gen=False):
    errors = []
    warnings = []
    
    skill_md = skill_dir / 'SKILL.md'
    if not skill_md.exists():
        return [f"Missing SKILL.md in {skill_dir.name}"], []

    with open(skill_md, 'r') as f:
        content = f.read()

    if not content.startswith('---'):
        return [f"Missing YAML frontmatter in {skill_dir.name}"], []

    end_frontmatter = content.find('---', 3)
    if end_frontmatter == -1:
        return [f"Unclosed YAML frontmatter in {skill_dir.name}"], []

    frontmatter_str = content[3:end_frontmatter]
    try:
        fm = yaml.safe_load(frontmatter_str)
    except yaml.YAMLError as e:
        return [f"Invalid YAML in {skill_dir.name}: {e}"], []

    name = fm.get('name')
    if name != skill_dir.name:
        errors.append(f"Name '{name}' does not match folder '{skill_dir.name}'")

    description = fm.get('description', '')
    if 'TODO' in description:
        errors.append(f"Description contains TODO in {skill_dir.name}")
    if len(description) < 20:
        errors.append(f"Description too short (<20 chars) in {skill_dir.name}")
    
    if "Triggers on" not in description and "Use when" not in description:
        errors.append(f"Description missing 'Triggers on' or 'Use when' in {skill_dir.name}")

    allowed_tools = fm.get('allowed-tools', '')
    if allowed_tools:
        tools = [t.strip() for t in allowed_tools.split(',')]
        for t in tools:
            if t not in KNOWN_TOOLS:
                errors.append(f"Unknown tool '{t}' in allowed-tools of {skill_dir.name}")

    body = content[end_frontmatter+3:].strip()
    lines = body.split('\n')
    
    if len(lines) > 300:
        errors.append(f"Body > 300 lines ({len(lines)}) in {skill_dir.name}")
    elif len(lines) > 150:
        warnings.append(f"Body > 150 lines ({len(lines)}) in {skill_dir.name}")
        
    if not pre_gen:
        found = False
        for skill in registry_data.get('skills', []):
            if skill.get('name') == name:
                found = True
                if skill.get('description') != description:
                    errors.append(f"Description mismatch with registry.min.json for {skill_dir.name}")
                break
                
        if not found:
            errors.append(f"Skill {skill_dir.name} missing from registry.min.json")
        
    return errors, warnings

def main():
    pre_gen = '--pre-gen' in sys.argv
    root_dir = Path(__file__).resolve().parent.parent
    skills_dir = root_dir / 'skills'
    registry_path = root_dir / 'registry.min.json'
    
    with open(registry_path, 'r') as f:
        registry_data = json.load(f)
        
    total_errors = 0
    total_warnings = 0
    
    if skills_dir.exists():
        for skill_dir in skills_dir.iterdir():
            if not skill_dir.is_dir():
                continue
            errs, warns = lint_skill(skill_dir, registry_data, pre_gen)
            
            for w in warns:
                print(f"WARN: {w}")
                total_warnings += 1
                
            for e in errs:
                print(f"ERROR: {e}")
                total_errors += 1
                
    if total_errors > 0:
        print(f"Lint failed with {total_errors} errors and {total_warnings} warnings.")
        sys.exit(1)
    else:
        print(f"Lint passed with {total_warnings} warnings.")
        sys.exit(0)

if __name__ == '__main__':
    main()
