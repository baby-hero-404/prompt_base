---
description: Initialize project with Minimal Viable Context (MVC).
---
# /init-context - MVC Initialization

1.  Analyze the current project type and explore its architecture.
2.  Identify domain logic and invariant rules.
3.  Set up Project Memory:
    - Determine `<project-name>` by combining the parent and leaf directory names of the workspace root (e.g., if workspace is `~/work/api`, the name is `work-api`).
    - If `~/.gemini/projects/<project-name>` does not exist, create the directory.
    - Copy templates from `~/.gemini/projects/_template/` and populate `PROFILE.md`, `DOMAIN.md`, and `manifest.json`.
4.  Suggest essential Core and Tech skills.
5.  Load the structured `project-memory` in `SLOT_MAP` alongside the suggested core and tech skills.
6.  Activate the `context-architect` agent to maintain token efficiency.
