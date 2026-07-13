---
name: skill-loading
description: "Use when activating or discovering JIT Knowledge skills dynamically during a task."
---

# Skill Loading Protocol (JIT Knowledge)

You are responsible for keeping the context window lean while ensuring the AI has the necessary expertise.

### 1. Discovery Phase

- **Intent Analysis**: Determine the domain (Web, Mobile, Security, etc.) and specific technologies (React, Python, Docker).
- **Registry Search**: Use `grep` or keyword matching in `registry.min.json`. Look for "triggers" and "description" matches.
- **Agent Selection**: Identify which specialist agent handles this domain.

### 2. Activation Phase (Loading)

- **Primary Load**: View the `SKILL.md` file of the most relevant skill(s).
- **Dependency Check**: Check the YAML frontmatter of the loaded `SKILL.md`. If a `skills:` list exists, load those dependencies recursively.
- **Selective Reading**: If a skill directory contains multiple `.md` files (e.g., `ux-ui-pro-max`), read the main `SKILL.md` first to see which sub-files are REQUIRED vs OPTIONAL.

### 3. Execution Phase

- Use the injected knowledge to perform the task.
- Document any architectural decisions or new patterns learned.

### 4. Pruning Phase (Unloading)

- Once the specific sub-task or feature is complete, "unload" the knowledge by not referencing it in subsequent steps.
- If context window pressure is high, explicitly state that you are clearing dormant knowledge.

> 🔴 **MANDATORY:** Never load more than 3-4 skills at once unless absolutely necessary for a complex orchestration.
