# Developer Guide: Adding a New Skill

> Step-by-step guide for contributors who want to add a new skill to Prompt Base.

---

## 📋 Prerequisites

Before you begin, make sure you have:

- The Prompt Base repository cloned locally
- Python 3.8+ installed (for registry scripts)
- PyYAML installed (`pip install pyyaml`) — used by the registry generator

---

## 🧠 Understanding Skills

A **Skill** is a specialized knowledge package that the AI agent loads on-demand. Each skill is a directory containing at least a `SKILL.md` file with YAML frontmatter metadata.

### How Skills Work

```
User Request → Orchestrator reads registry.min.json
                     │
                     ├── Matches keywords to skill description
                     ├── Loads the matching SKILL.md into context
                     ├── Agent executes using skill knowledge
                     └── Prunes skill from context when done
```

### Skill Categories

| Category | Path | Use For |
|----------|------|---------|
| `core` | `skills/core/` | Framework fundamentals (coding standards, planning, brainstorming) |
| `tech` | `skills/tech/` | Technology-specific knowledge (React, Go, Docker, etc.) |
| `process` | `skills/process/` | Development workflows (testing, security, deployment, etc.) |
| `custom` | `skills/custom/` | Project-specific or user-created skills |

---

## 🚀 Step-by-Step: Adding a New Skill

### Step 1: Choose the Category

Decide which category fits your skill:

| If your skill is about... | Choose |
|---------------------------|--------|
| A programming language, framework, or tool | `tech` |
| A development workflow, DevOps, or quality process | `process` |
| Core AI behavior (planning, brainstorming, etc.) | `core` |
| Something specific to a project or user | `custom` |

### Step 2: Create the Skill Directory

Name your directory using `kebab-case` (lowercase with hyphens):

```bash
# Example: adding a "redis-patterns" skill to the tech category
mkdir -p skills/tech/redis-patterns
```

### Step 3: Create the SKILL.md File

Every skill **must** have a `SKILL.md` file. This is the only required file.

Create `skills/tech/redis-patterns/SKILL.md`:

```markdown
---
name: redis-patterns
description: Redis caching patterns, data structures, and best practices. Use for caching, sessions, pub/sub, and rate limiting.
allowed-tools: Read, Write, Edit
---

# Redis Patterns

> Best practices for Redis in production applications.

## 1. Caching Strategies

| Strategy | Use When |
|----------|----------|
| **Cache-Aside** | Read-heavy, data doesn't change often |
| **Write-Through** | Data consistency is critical |
| **Write-Behind** | Write-heavy, eventual consistency OK |

## 2. Data Structure Selection

| Need | Use |
|------|-----|
| Simple key-value | `STRING` |
| Object with fields | `HASH` |
| Sorted rankings | `SORTED SET` |
| Queue/stack | `LIST` |
| Unique items | `SET` |

...your skill content continues...
```

#### Frontmatter Fields Reference

| Field | Required | Description |
|-------|----------|-------------|
| `name` | ✅ Yes | Skill ID — must match the directory name |
| `description` | ✅ Yes | One-line description used for auto-matching. **This is how the AI finds your skill** — include trigger keywords! |
| `allowed-tools` | No | Which tools the agent can use (Read, Write, Edit, Glob, Grep, Bash, Agent) |
| `version` | No | Version number for tracking changes |
| `priority` | No | `CRITICAL`, `HIGH`, `NORMAL`, `LOW` — affects loading order |

> **⚠️ Important**: The `description` field is critical for auto-triggering. Include relevant keywords that users would naturally say. For example:
> - ❌ Bad: `"Redis database skill"`
> - ✅ Good: `"Redis caching patterns, data structures, and best practices. Use for caching, sessions, pub/sub, and rate limiting."`

### Step 4: (Optional) Add Supporting Files

For complex skills, you can add optional directories:

```
redis-patterns/
├── SKILL.md          # (Required) Metadata & instructions
├── references/       # (Optional) Reference docs, cheat sheets
│   └── commands.md
├── scripts/          # (Optional) Helper scripts
│   └── benchmark.sh
├── assets/           # (Optional) Images, diagrams
│   └── architecture.png
└── templates/        # (Optional) Code templates
    └── cache-service.ts
```

The `SKILL.md` can reference these files — the agent will load them as needed:

```markdown
## Resources

| File | Description | When to Read |
|------|-------------|--------------|
| `references/commands.md` | Common Redis commands | Quick reference |
| `templates/cache-service.ts` | Cache service template | Creating new cache layer |
```

### Step 5: Register the Skill in the Registry

Add your skill entry to `registry.min.json` in the appropriate category:

```json
{
    "skills": {
        "tech": [
            ...existing skills...,
            {
                "id": "redis-patterns",
                "name": "redis-patterns",
                "description": "Redis caching patterns, data structures, and best practices. Use for caching, sessions, pub/sub, and rate limiting.",
                "path": "skills/tech/redis-patterns"
            }
        ]
    }
}
```

> **Field mapping:**
> | Registry Field | Source |
> |----------------|--------|
> | `id` | Directory name |
> | `name` | `name` from SKILL.md frontmatter |
> | `description` | `description` from SKILL.md frontmatter |
> | `path` | Relative path: `skills/<category>/<skill-name>` |

**Alternative:** Run the registry generator script to auto-generate from all SKILL.md files:

```bash
python3 scripts/generate_registry.py
```

### Step 6: Update ARCHITECTURE.md (if needed)

If your skill introduces a **new category** or changes the skill count significantly, update the skills table in `ARCHITECTURE.md`.

### Step 7: Validate (Quality Gates)

Run the quality check pipeline to verify your skill:

```bash
make skill-check SKILL=skill-name
```

This automatically runs:
- **Tier 1 (Linter)**: Validates frontmatter, description, and formatting.
- **Tier 2 (Trigger Test)**: Tests trigger keyword precision and recall.
- **Tier 0 (Contract Check)**: Validates all repo paths, CLIs, tools, and referenced skills.

### Step 8: Golden Eval (Optional)

If your skill has `eval: required` in its frontmatter, `skill-check` will prompt you to run an evaluation:

```bash
make skill-eval SKILL=skill-name
```
This compares the `HEAD` version vs your changes against predefined golden tasks using an LLM Judge. 
> **Configuration**: This test runs a live LLM evaluation loop. It requires a `GEMINI_API_KEY` to be defined in your `.env` file at the root of the project. By default, it uses `gemini-2.0-flash`, but you can customize this by setting `GEMINI_MODEL="your-preferred-model"` in the `.env` file.

### Step 9: Merge and Journal

If changes are successful and verified, merge them. Record any significant evaluation outcomes or rollbacks in `docs/reports/skill-feedback.md`.

---

## 📐 SKILL.md Writing Guidelines

### Do's

| Rule | Why |
|------|-----|
| **Use tables** for reference material | Fast scanning, low token cost |
| **Use decision trees** | Helps the AI choose the right pattern |
| **Include code examples** | Concrete patterns the AI can follow |
| **Add anti-patterns** | Prevents the AI from making common mistakes |
| **Keep it concise** | Every token matters — avoid verbose explanations |

### Don'ts

| Avoid | Why |
|-------|-----|
| Lengthy prose paragraphs | Wastes context window tokens |
| Duplicate content from other skills | Increases context bloat |
| Overly broad descriptions | Causes false-positive skill matching |
| Missing trigger keywords in description | Skill won't be auto-discovered |

### Template Structure

A well-structured `SKILL.md` follows this pattern:

```markdown
---
name: skill-name
description: Short trigger-keyword-rich description.
allowed-tools: Read, Write, Edit
---

# Skill Name

> One-line philosophy or principle.

## 1. Core Principles / Decision Matrix

(Tables with key decisions the AI must make)

## 2. Patterns & Best Practices

(The main knowledge content)

## 3. Code Examples

(Concrete, copy-paste-ready code)

## 4. Anti-Patterns

(What NOT to do, with explanations)

## 5. Decision Checklist

(Quick checklist the AI can run through)
```

---

## 📂 Full Example: End-to-End

Here's a complete walkthrough of adding a `graphql-patterns` skill:

### 1. Create directory

```bash
mkdir -p skills/tech/graphql-patterns
```

### 2. Create SKILL.md

```bash
cat > skills/tech/graphql-patterns/SKILL.md << 'EOF'
---
name: graphql-patterns
description: GraphQL API design patterns, schema design, resolvers, and performance. Use for GraphQL, Apollo, schema, query, mutation, subscription.
allowed-tools: Read, Write, Edit
---

# GraphQL Patterns

> Schema-first thinking for type-safe APIs.

## 1. Schema Design Principles

| Principle | Rule |
|-----------|------|
| **Nullable by default** | Only mark fields `!` when guaranteed |
| **Connections for lists** | Use Relay-style pagination |
| **Input types** | Separate input from output types |
| **Enums** | Use for fixed sets of values |

## 2. Resolver Patterns

| Pattern | Use When |
|---------|----------|
| **DataLoader** | N+1 query problem |
| **Field resolver** | Computed fields |
| **Middleware** | Auth, logging, caching |

## 3. Anti-Patterns

| ❌ Don't | ✅ Do |
|----------|-------|
| Expose DB schema directly | Design client-focused schema |
| Deep nesting (>3 levels) | Flatten with connections |
| Giant query types | Split into domains |
EOF
```

### 3. Add to registry.min.json

Add this entry to `"skills" > "tech"` array:

```json
{
    "id": "graphql-patterns",
    "name": "graphql-patterns",
    "description": "GraphQL API design patterns, schema design, resolvers, and performance. Use for GraphQL, Apollo, schema, query, mutation, subscription.",
    "path": "skills/tech/graphql-patterns"
}
```

### 4. Validate

```bash
make audit
```

Expected output:
```
✅ Skill directory exists
✅ SKILL.md found
✅ Description present
🚀 ALL SYSTEMS NOMINAL
```

---

## 🔧 Useful Scripts

| Script | Command | Purpose |
|--------|---------|---------|
| **Audit** | `make audit` | Validate all skills, agents, and registry consistency |
| **Test** | `make test` | Run integration tests |
| **Generate Registry** | `python3 scripts/generate_registry.py` | Auto-rebuild registry.min.json from all SKILL.md files |

---

## ❓ FAQ

### My skill isn't being triggered — what's wrong?

Check your `description` field in SKILL.md. It must contain the **keywords** users would naturally use. The orchestrator matches user intent against skill descriptions.

### Can I have sub-files in my skill?

Yes. Use a content map table in your SKILL.md to tell the agent which file to read and when. See the `app-builder` skill for an example of a multi-file skill.

### How many skills can I add?

There's no hard limit. The Librarian Protocol uses lazy loading — only matched skills are loaded into context.

### Do I need to update GEMINI.md when adding a skill?

No. Skills are discovered through `registry.min.json`. You only need to update `GEMINI.md` if you're changing rules or adding new slash commands.