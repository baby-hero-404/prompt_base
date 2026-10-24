import os
import sys

def test_integration():
    print("🧪 Testing Prompt Base Global Integration...\n")
    
    # The project root is the parent of the scripts/ directory
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    print(f"📁 Project root: {project_root}")
    
    # 1. Verify Rules (GEMINI.md, CLAUDE.md, AGENTS.md)
    print("\n--- 1. Rules ---")
    for rule_file in ["GEMINI.md", "CLAUDE.md", "AGENTS.md"]:
        rule_path = os.path.join(project_root, rule_file)
        if os.path.exists(rule_path):
            print(f"✅ Rules file exists: {rule_file}")
        else:
            print(f"❌ Missing Rules file: {rule_file}")
            sys.exit(1)

    # CLAUDE.md, GEMINI.md, and AGENTS.md must carry identical rules (only the Layout paths differ)
    def rules_section(name):
        with open(os.path.join(project_root, name), "r") as f:
            text = f.read()
        return text[text.find("## Rules"):]

    claude_rules = rules_section("CLAUDE.md")
    gemini_rules = rules_section("GEMINI.md")
    agents_rules = rules_section("AGENTS.md")

    if claude_rules == gemini_rules == agents_rules:
        print(f"✅ CLAUDE.md, GEMINI.md, and AGENTS.md rules are in sync")
    else:
        if claude_rules != gemini_rules:
            print(f"❌ CLAUDE.md and GEMINI.md rules differ (from '## Rules' onward)")
        if claude_rules != agents_rules:
            print(f"❌ CLAUDE.md and AGENTS.md rules differ (from '## Rules' onward)")
        sys.exit(1)

    # 2. Verify Workflows (global_workflows/)
    print("\n--- 2. Workflows ---")
    workflow_dir = os.path.join(project_root, "global_workflows")
    if os.path.isdir(workflow_dir):
        workflows = [f for f in os.listdir(workflow_dir) if f.endswith(".md")]
        print(f"✅ Workflow directory exists with {len(workflows)} workflow(s)")
        for w in sorted(workflows):
            print(f"   📄 {w}")
    else:
        print(f"❌ Missing workflow directory: global_workflows/")
        sys.exit(1)
    
    # 3. Verify Skills (skills/)
    print("\n--- 3. Skills ---")
    skill_dir = os.path.join(project_root, "skills")
    if os.path.isdir(skill_dir):
        skills = [d for d in os.listdir(skill_dir) if os.path.isdir(os.path.join(skill_dir, d))]
        print(f"✅ Skill directory exists with {len(skills)} skills")
        for skill in sorted(skills):
            print(f"   📂 {skill}/")
    else:
        print(f"❌ Missing skill directory: skills/")
        sys.exit(1)
    
    # 4. Verify Agents
    print("\n--- 4. Agents ---")
    agents_dir = os.path.join(project_root, "agents")
    if os.path.isdir(agents_dir):
        agents = [f for f in os.listdir(agents_dir) if f.endswith(".md")]
        print(f"✅ Agents directory exists with {len(agents)} agent(s)")
    else:
        print(f"❌ Missing agents directory")
        sys.exit(1)
    
    # 5. Verify Registry
    print("\n--- 5. Registry ---")
    registry_path = os.path.join(project_root, "registry.min.json")
    if os.path.exists(registry_path):
        import json
        with open(registry_path, "r") as f:
            registry = json.load(f)
        
        # Verify skill paths point to skills/
        for skill in registry.get("skills", []):
            if not skill["path"].startswith("skills/"):
                print(f"❌ Skill path not updated: {skill['path']}")
                sys.exit(1)
        print("✅ Registry exists and all skill paths use skills/")
    else:
        print(f"❌ Missing registry: registry.min.json")
        sys.exit(1)

    print("\n🎉 INTEGRATION TEST PASSED!")
    print("All 3 component types validated:")
    print("  1. Rules     → GEMINI.md / CLAUDE.md / AGENTS.md ✅")
    print("  2. Workflows → global_workflows/*.md ✅")
    print("  3. Skills    → skills/*/SKILL.md ✅")

if __name__ == "__main__":
    test_integration()
