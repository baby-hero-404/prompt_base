#!/usr/bin/env python3
import sys
import json
import re
from collections import defaultdict
from pathlib import Path

def extract_triggers(description):
    """Extract keywords after 'Triggers on:' or 'Triggers on'."""
    match = re.search(r'Triggers on:?(.*)', description, re.IGNORECASE)
    if not match:
        return []
    keywords_part = match.group(1).strip()
    if keywords_part.endswith('.'):
        keywords_part = keywords_part[:-1]
    
    return [kw.strip().lower() for kw in keywords_part.split(',') if kw.strip()]

def main():
    root_dir = Path(__file__).resolve().parent.parent
    registry_path = root_dir / 'registry.min.json'
    cases_path = root_dir / 'tests' / 'skills' / 'trigger_cases.json'
    
    if not registry_path.exists():
        print("registry.min.json not found")
        sys.exit(1)
        
    with open(registry_path, 'r') as f:
        registry = json.load(f)
        
    skill_triggers = {}
    for cat, skills in registry.get('skills', {}).items():
        for skill in skills:
            name = skill['name']
            desc = skill.get('description', '')
            triggers = extract_triggers(desc)
            if triggers:
                skill_triggers[name] = triggers

    # Collision report
    kw_to_skills = defaultdict(list)
    for skill, kws in skill_triggers.items():
        for kw in kws:
            kw_to_skills[kw].append(skill)
            
    collisions = {kw: skills for kw, skills in kw_to_skills.items() if len(skills) > 1}
    if collisions:
        print("WARNING: Trigger keyword collisions detected!")
        for kw, skills in collisions.items():
            print(f"  - '{kw}' shared by: {', '.join(skills)}")
            
    if not cases_path.exists():
        print(f"{cases_path} not found")
        sys.exit(1)
        
    with open(cases_path, 'r') as f:
        cases = json.load(f)
        
    # Warn zero cases
    tested_skills = set()
    for case in cases:
        tested_skills.update(case.get('expect', []))
        
    registered_skills = set(skill_triggers.keys())
    missing = registered_skills - tested_skills
    for m in missing:
        print(f"WARN: Skill '{m}' has zero test cases in trigger_cases.json")
        
    # Evaluate Precision/Recall
    tp = defaultdict(int)
    fp = defaultdict(int)
    fn = defaultdict(int)
    
    for case in cases:
        prompt = case['prompt'].lower()
        expected = set(case.get('expect', []))
        
        actual = set()
        for skill, kws in skill_triggers.items():
            for kw in kws:
                if re.search(r'\b' + re.escape(kw) + r'\b', prompt):
                    actual.add(skill)
                    break
                    
        for skill in expected:
            if skill in actual:
                tp[skill] += 1
            else:
                fn[skill] += 1
                
        for skill in actual:
            if skill not in expected:
                fp[skill] += 1
                
    overall_ok = True
    print("\n--- Trigger Eval Results ---")
    
    threshold = 0.9
    for skill in sorted(tested_skills):
        t = tp[skill]
        f_p = fp[skill]
        f_n = fn[skill]
        
        precision = t / (t + f_p) if (t + f_p) > 0 else (1.0 if f_n == 0 else 0.0)
        recall = t / (t + f_n) if (t + f_n) > 0 else 0.0
        
        print(f"{skill}: Precision={precision:.2f}, Recall={recall:.2f}")
        
        if precision < threshold or recall < threshold:
            overall_ok = False
            print(f"  -> FAILED threshold {threshold}")
            
    if not overall_ok:
        print("\nTrigger test failed: One or more skills below threshold.")
        sys.exit(1)
    else:
        print("\nTrigger test passed!")
        sys.exit(0)

if __name__ == '__main__':
    main()
