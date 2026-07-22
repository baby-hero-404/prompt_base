import json
import os
import sys
import re

def check_structure():
    print("📋 Prompt Base - Final Audit\n")
    issues = []
    
    # 0. Root Detection
    root_dir = None
    
    # Allow override via --root flag
    if "--root" in sys.argv:
        idx = sys.argv.index("--root")
        if idx + 1 < len(sys.argv):
            root_dir = sys.argv[idx + 1]
    
    # Allow positional argument (e.g., `python3 checklist.py .`)
    if root_dir is None:
        positional_args = [a for a in sys.argv[1:] if not a.startswith("--")]
        if positional_args:
            root_dir = positional_args[0]
    
    # Default: global install at ~/.gemini
    if root_dir is None:
        root_dir = os.path.expanduser("~/.gemini")
        # Fallback: if running from the repo directory itself
        if not os.path.exists(root_dir) and os.path.exists("GEMINI.md"):
            root_dir = "."

    print(f"🔍 Checking structure using root: {root_dir}")

    # 1. Critical Files (Rules + Core)
    critical_files = [
        f"{root_dir}/ARCHITECTURE.md",
        f"{root_dir}/GEMINI.md",
        f"{root_dir}/registry.min.json",
        ]

    for f in critical_files:
        if os.path.exists(f):
            print(f"✅ {f} found.")
        else:
            issues.append(f"❌ Missing critical file: {f}")

    # 2. Directory Structure — 3 component types
    dirs = [
        f"{root_dir}/agents",
        f"{root_dir}/skills",
        f"{root_dir}/global_workflows",
    ]
    
    for d in dirs:
        if os.path.isdir(d):
            print(f"✅ Directory {d} exists.")
        else:
            issues.append(f"❌ Missing directory: {d}")

    # 3. Registry Consistency
    registry_path = f"{root_dir}/registry.min.json"
    if os.path.exists(registry_path):
        with open(registry_path, "r") as f:
            registry = json.load(f)
            
            # Check Agents
            for agent in registry.get("agents", []):
                full_path = os.path.join(root_dir, agent["path"])
                if not os.path.exists(full_path):
                    issues.append(f"❌ Registry points to non-existent agent: {full_path}")
            
            # Check Skills (paths now under skills/)
            for skill in registry.get("skills", []):
                full_path = os.path.join(root_dir, skill["path"])
                if not os.path.exists(full_path):
                    issues.append(f"❌ Registry points to non-existent skill: {full_path}")
        print("✅ Registry consistency check complete.")

    # 4. Deep Skill Verification & Orphans
    print("🔍 Performing deep skill verification...")
    skill_root = f"{root_dir}/skills"
    registered_paths = set()
    
    # Collect all registered paths
    if os.path.exists(registry_path):
        with open(registry_path, "r") as f:
            registry = json.load(f)
            for skill in registry.get("skills", []):
                skill_path = os.path.join(root_dir, skill["path"])
                registered_paths.add(os.path.abspath(skill_path))

                if not skill.get("description"):
                    issues.append(f"⚠️ Skill missing description: {skill['id']}")

                # Check for SKILL.md
                if os.path.isdir(skill_path):
                    skill_md_path = os.path.join(skill_path, "SKILL.md")
                    if not os.path.exists(skill_md_path):
                        issues.append(f"❌ Skill directory missing SKILL.md: {skill_path}")
                    else:
                        with open(skill_md_path, "r", encoding="utf-8") as smd:
                            line_count = sum(1 for _ in smd)
                            if line_count > 175:
                                issues.append(f"⚠️ SKILL.md exceeds 175 lines ({line_count} lines) in {skill_path}. Recommend moving details into a references/ subdirectory read on demand.")

    # Check for Orphans
    if os.path.exists(skill_root):
        for d in os.listdir(skill_root):
            d_path = os.path.join(skill_root, d)
            if os.path.isdir(d_path):
                if os.path.exists(os.path.join(d_path, "SKILL.md")):
                    if os.path.abspath(d_path) not in registered_paths:
                         issues.append(f"⚠️ Orphaned skill found: {d_path}")

    # 5. Workflow Verification
    print("🔍 Checking workflows...")
    workflow_dir = f"{root_dir}/global_workflows"
    if os.path.isdir(workflow_dir):
        workflow_files = [f for f in os.listdir(workflow_dir) if f.endswith(".md")]
        print(f"✅ Found {len(workflow_files)} workflow(s) in {workflow_dir}")
    else:
        issues.append(f"❌ Missing workflow directory: {workflow_dir}")

    # 6. Orphaned Agents Check
    agents_dir = f"{root_dir}/agents"
    if os.path.exists(agents_dir):
        agent_ids = set()
        if os.path.exists(registry_path):
            with open(registry_path, "r") as f:
                reg = json.load(f)
                for a in reg.get("agents", []):
                    agent_path = os.path.join(root_dir, a["path"])
                    agent_ids.add(os.path.abspath(agent_path))
                    if not a.get("description"):
                         issues.append(f"⚠️ Agent missing description: {a['name']}")

        for f in os.listdir(agents_dir):
            if f.endswith(".md"):
                f_path = os.path.abspath(os.path.join(agents_dir, f))
                if f_path not in agent_ids:
                    issues.append(f"⚠️ Orphaned agent found: {os.path.join(agents_dir, f)}")

    # Summary
    print("\n--- Audit Result ---")
    if not issues:
        print("🚀 ALL SYSTEMS NOMINAL. Prompt Base is ready.")
        sys.exit(0)
    else:
        print(f"Found {len(issues)} issues:")
        for issue in issues:
            print(issue)
        sys.exit(1)

if __name__ == "__main__":
    check_structure()
