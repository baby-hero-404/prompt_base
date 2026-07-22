import os
import json
import yaml

def get_frontmatter(file_path):
    with open(file_path, 'r') as f:
        content = f.read()
        if content.startswith('---'):
            try:
                parts = content.split('---')
                return yaml.safe_load(parts[1])
            except:
                return {}
    return {}

def build_registry(framework_dir=".", force_prefix=None):
    """
    Builds the registry.min.json file.
    framework_dir: The directory containing agents/, skills/, etc.
    force_prefix: Optional string to force as prefix (e.g., ".agents/")
    """
    # Current workspace root (where the script is being run from)
    workspace_root = os.getcwd()
    
    # Framework root (absolute)
    abs_framework_root = os.path.abspath(framework_dir)
    
    if force_prefix is not None:
        rel_prefix = force_prefix
        print(f"🔗 Using forced prefix: '{rel_prefix}'")
    else:
        # Path from workspace_root to framework_root
        try:
            rel_prefix = os.path.relpath(abs_framework_root, workspace_root)
            if rel_prefix == ".":
                rel_prefix = ""
            else:
                rel_prefix = rel_prefix + "/"
        except ValueError:
            # If on different drives (Windows), use absolute paths or fallback
            rel_prefix = abs_framework_root + "/"
        print(f"🔗 Calculated path prefix: '{rel_prefix}'")

    print(f"📍 Framework located at: {abs_framework_root}")

    registry = {
        "agents": [],
        "skills": []
    }

    # Agents
    agent_dir = os.path.join(abs_framework_root, "agents")
    if os.path.exists(agent_dir):
        for f in sorted(os.listdir(agent_dir)):
            if f.endswith('.md'):
                meta = get_frontmatter(os.path.join(agent_dir, f))
                registry["agents"].append({
                    "id": f.replace('.md', ''),
                    "name": meta.get('name', f),
                    "description": meta.get('description', ''),
                    "path": f"{rel_prefix}agents/{f}"
                })

    # Skills (located directly under skills/)
    skills_path = os.path.join(abs_framework_root, "skills")
    if os.path.exists(skills_path):
        for d in sorted(os.listdir(skills_path)):
            skill_dir = os.path.join(skills_path, d)
            skill_md = os.path.join(skill_dir, "SKILL.md")
            if os.path.isdir(skill_dir) and os.path.exists(skill_md):
                meta = get_frontmatter(skill_md)
                registry["skills"].append({
                    "id": d,
                    "name": meta.get('name', d),
                    "description": meta.get('description', ''),
                    "path": f"{rel_prefix}skills/{d}"
                })

    # Write registry to the framework_dir
    registry_file = os.path.join(abs_framework_root, "registry.min.json")
    with open(registry_file, "w") as f:
        json.dump(registry, f, indent=2)
    
    # Also create minified version
    min_file = os.path.join(abs_framework_root, "registry.min.json")
    with open(min_file, "w") as f:
        json.dump(registry, f, separators=(',', ':'))
        
    print(f"✅ Generated registry at: {registry_file}")

if __name__ == "__main__":
    import sys
    # Default to current directory where script resides
    script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    target_framework = script_dir
    
    if len(sys.argv) > 1:
        target_framework = sys.argv[1]
        build_registry(target_framework)
    else:
        # Default manual run: no prefix (global mode)
        build_registry(target_framework, force_prefix="")
