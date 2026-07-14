#!/usr/bin/env python3
"""Scaffold a new Prompt Base skill: create its directory, SKILL.md, and sync the registry."""
import argparse
import os
import re
import subprocess
import sys
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from generate_registry import build_registry

FRAMEWORK_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CATEGORIES = ["core", "tech", "process", "custom"]

SKILL_TEMPLATE = """---
name: {name}
description: "{description}"
allowed-tools: Read, Write, Edit, Glob, Grep{eval_line}
---

# {title}

## When to Use
- TODO: describe the triggering situations for this skill.

## Core Principles
- TODO: the 2-4 rules an agent must follow when this skill is active.

## Anti-Patterns
- TODO: common mistakes this skill should prevent.
"""


def slugify(name: str) -> str:
    slug = name.strip().lower()
    slug = re.sub(r"[^a-z0-9]+", "-", slug)
    return slug.strip("-")


def load_existing_skill_ids():
    ids = set()
    for cat in CATEGORIES:
        cat_path = os.path.join(FRAMEWORK_ROOT, "antigravity", "skills", cat)
        if os.path.isdir(cat_path):
            ids.update(d for d in os.listdir(cat_path) if os.path.isdir(os.path.join(cat_path, d)))
    return ids


def load_existing_agent_ids():
    agent_dir = os.path.join(FRAMEWORK_ROOT, "antigravity", "agents")
    if not os.path.isdir(agent_dir):
        return set()
    return {f[:-3] for f in os.listdir(agent_dir) if f.endswith(".md")}


def main():
    parser = argparse.ArgumentParser(description="Scaffold a new skill for Prompt Base.")
    parser.add_argument("name", help="Skill name, e.g. 'rust-patterns' (will be slugified).")
    parser.add_argument("--category", choices=CATEGORIES, default="custom")
    parser.add_argument("--description", default="")
    parser.add_argument("--trigger-case", help="A seed prompt to add to trigger_cases.json")
    parser.add_argument("--eval", action="store_true", help="Add eval: required to frontmatter")
    parser.add_argument("--no-install", action="store_true", help="Skip `make install` after scaffolding.")
    parser.add_argument("--dry-run", action="store_true", help="Print what would happen, write nothing.")
    args = parser.parse_args()
    
    trigger_case = args.trigger_case
    if not trigger_case and not args.dry_run:
        try:
            trigger_case = input("Enter a seed trigger case (a prompt that should trigger this skill): ").strip()
        except EOFError:
            pass

    slug = slugify(args.name)
    if not slug:
        sys.exit(f"❌ '{args.name}' has no valid characters for a skill name.")
    if slug != args.name:
        print(f"ℹ️  Normalized '{args.name}' -> '{slug}'")

    existing_skills = load_existing_skill_ids()
    existing_agents = load_existing_agent_ids()

    if slug in existing_skills:
        sys.exit(f"❌ Skill '{slug}' already exists. Choose a different name or edit it directly.")
    if slug in existing_agents:
        print(f"⚠️  Warning: an agent named '{slug}' already exists. This may confuse routing.")

    skill_dir = os.path.join(FRAMEWORK_ROOT, "antigravity", "skills", args.category, slug)
    if os.path.exists(skill_dir):
        sys.exit(f"❌ Directory already exists on disk: {skill_dir} (registry may be stale — run `make registry`).")

    description = args.description or f"TODO: describe when to use {slug}. Triggers on: keyword."
    title = slug.replace("-", " ").title()
    eval_line = "\neval: required" if args.eval else ""
    content = SKILL_TEMPLATE.format(name=slug, description=description, title=title, eval_line=eval_line)

    if args.dry_run:
        print(f"[dry-run] Would create {skill_dir}/SKILL.md:\n{content}")
        return

    os.makedirs(skill_dir, exist_ok=False)
    with open(os.path.join(skill_dir, "SKILL.md"), "w") as f:
        f.write(content)
    print(f"✅ Created {skill_dir}/SKILL.md")
    
    if trigger_case:
        cases_path = os.path.join(FRAMEWORK_ROOT, "tests", "skills", "trigger_cases.json")
        if os.path.exists(cases_path):
            with open(cases_path, "r") as f:
                cases = json.load(f)
            cases.append({"prompt": trigger_case, "expect": [slug]})
            with open(cases_path, "w") as f:
                json.dump(cases, f, indent=2)
            print(f"✅ Added trigger case to tests/skills/trigger_cases.json")

    print("🔄 Regenerating registry...")
    build_registry(FRAMEWORK_ROOT, force_prefix="")

    if args.no_install:
        print("⏭️  Skipping install (--no-install). Run `make install` when ready.")
        return

    print("📦 Installing to ~/.claude and ~/.gemini...")
    result = subprocess.run(["make", "-C", FRAMEWORK_ROOT, "install"])
    if result.returncode != 0:
        sys.exit("❌ `make install` failed — registry was updated but local installs may be stale.")

    print(f"\n✅ Skill '{slug}' scaffolded, registered, and installed.")
    print(f"👉 Next: edit {skill_dir}/SKILL.md — the description drives auto-trigger, don't ship the TODO placeholder.")


if __name__ == "__main__":
    main()
