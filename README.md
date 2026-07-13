# Prompt Base (Global Mode)

Prompt Base is a modular AI development framework designed to run **globally** from `~/.gemini`. It transforms your AI assistant into a specialized team of experts with deep domain knowledge — across all your projects.

## 🚀 Quick Setup

### Installation (Global — All Workspaces)

Clone this repository into `~/.gemini` so the `GEMINI.md` (or `CLAUDE.md`) file is picked up automatically (or symlink them to your workspace roots):

```bash
git clone https://github.com/baby-hero-404/prompt_base ~/.gemini
```

Then remove development-only files (scripts, docs, Makefile, README, .git, etc.):

```bash
bash ~/.gemini/scripts/cleanup.sh
```

> If the project is already cloned locally or `~/.gemini` (or `~/.claude`) exists, you can install/update it directly using make:
> ```bash
> git clone https://github.com/baby-hero-404/prompt_base
> cd prompt_base
> make install-gemini  # Install to ~/.gemini
> make install-claude  # Install to ~/.claude
> make install         # Install to both
> ```

After cleanup, only the runtime essentials remain in `~/.gemini`:

```
~/.gemini/
├── GEMINI.md              ← Rules (always active)
├── ARCHITECTURE.md        ← System map
├── registry.min.json      ← Skill discovery
├── core/                  ← Core logic
├── agents/                ← Agent definitions
└── antigravity/
    ├── global_workflows/  ← Workflows
    └── skills/            ← Skills
```

---

## 🏗️ Architecture: 3 Component Types

Prompt Base is built on **3 global component types**. Each has a dedicated storage location and activation model:

| # | Component | Purpose | Storage Path | Activation |
|---|-----------|---------|-------------|------------|
| 1 | **Rules** | Persistent behavior (coding style, safety, patterns) | `~/.gemini/GEMINI.md` | Always active |
| 2 | **Workflows** | On-demand modes triggered via slash commands | `~/.gemini/antigravity/global_workflows/*.md` | `/plan`, `/review`, `/create`, etc. |
| 3 | **Skills** | Auto-triggered knowledge modules | `~/.gemini/antigravity/skills/*/SKILL.md` | Automatic (keyword match) |

### How It Fits Together

```
~/.gemini/                          ← FRAMEWORK_ROOT
├── GEMINI.md                       ← Rules (always active)
├── ARCHITECTURE.md                 ← System map
├── core/                           ← Core logic (system prompt, rules, classifier)
├── agents/                         ← 14 Specialist Agent definitions
├── registry.min.json               ← Unified metadata index
└── antigravity/                    ← Antigravity platform integration
    ├── global_workflows/           ← Workflows (slash commands)
    │   ├── brainstorm.md
    │   ├── plan.md
    │   ├── create.md
    │   └── ...
    └── skills/                     ← Skills (auto-trigger)
        ├── core/
        ├── tech/
        ├── process/
        └── custom/
```

---

## 📖 Usage Guide

Prompt Base uses **Progressive Disclosure** (the "Librarian Protocol"). Skills remain dormant until you need them, keeping your context window clean and efficient.

### 1. Rules (Always Active)

Rules are defined in `~/.gemini/GEMINI.md` and apply to **every** conversation automatically. They include:

- Coding standards & clean code policies
- The Socratic Gate (mandatory clarification before complex tasks)
- Request classification (QUESTION → SIMPLE CODE → COMPLEX CODE)
- File dependency awareness

> You don't need to do anything — rules are always enforced.

### 2. Skills (Auto-Triggered)

You don't need to manually load skills. Simply describe what you want to do, and the orchestrator will activate the relevant skill based on your intent.

- **Trigger**: Use keywords like "design", "build", "fix", "analyze", or specific tech stacks like "React" or "Python".
- **Example**: "I need to design a landing page" → Triggers `ux-ui-pro-max`
- **Example**: "Refactor this API for performance" → Triggers `backend-specialist` + `performance-optimizer`
- **Example**: "Write unit tests for this module" → Triggers `test-engineer` + `testing-patterns`

Skills are stored at `~/.gemini/antigravity/skills/*/SKILL.md`.

### 3. Workflows (Slash Commands)

Slash commands are on-demand automation scripts that orchestrate multiple Specialist Agents for complex tasks. They follow a logical development lifecycle:

| Command | Description | When to Use |
|---------|-------------|-------------|
| `/brainstorm [topic]` | Structured exploration with 3+ approaches, pros/cons, effort estimates | Exploring options before committing |
| `/plan [task]` | Socratic discovery → technical blueprint at `docs/plans/PLAN-*.md` | Before any complex feature (**no code**) |
| `/create [feature]` | Full-stack implementation via coordinated expert agents | Building new features or prototypes |
| `/enhance [feature]` | Iterative improvement with dependency management | Adding modules to existing code |
| `/test [file/feature]` | Unit/integration tests (AAA pattern), coverage checks | Ensuring code reliability |
| `/debug [issue]` | Systematic root-cause analysis | Tricky bugs requiring deep investigation |
| `/review` | Formal audit of staged changes | Before committing code |
| `/deploy` | Production deployment with pre-flight checks | Releasing to production/staging |
| `/status` | Project-wide health check | Checking pending tasks & agent assignments |
| `/init-context` | Initialize context (MVC) | Start of every new conversation |
| `/deep-solve` | JIT Knowledge workflow | Complex multi-domain problems |
| `/restructure` | Maintenance & registry update | Framework maintenance |
| `/orchestrate` | Multi-agent coordination | Tasks requiring multiple perspectives |
| `/ux-ui-pro` | Design intelligence mode | Premium UI/UX design work |

Workflows are stored at `~/.gemini/antigravity/global_workflows/*.md`.

### 4. Specialized Skill: UX/UI Pro Max

A high-level design intelligence library for building premium interfaces:

- **Generate Design Systems**: Ask the AI to `Generate a design system for a [Product Type] [Industry]`.
- **Design Tools**: The AI searches through styles, palettes, and typography pairs stored in skill assets.
- **Persistence**: Use the `--persist` flag when generating designs to create a `MASTER.md` file in your `design-system/` folder.

---

## 🛠️ Framework Features

- **14 Specialist Agents**: Role-based AI personas (Frontend, Backend, Security, etc.).
- **50+ Skills**: JIT knowledge modules (React, Go, SQL, UX, etc.).
- **⚡ Token Efficiency**: Optimized "Lean Agent Profiles" and JIT Knowledge Loading to minimize cost and maximize reasoning precision.
- **🛡️ Socratic Gate**: Mandatory clarification protocol for complex tasks to ensure intent alignment before coding.
- **🚦 Recommended Flows**: Structured operational pipelines tailored to task complexity (see [Scenario Flows](ARCHITECTURE.md#%F0%9F%9A%A6-recommended-developer-flows-by-scenario)).

---

## 🧠 Creating Your Own Skills (Quick Guide)

Skills are modular knowledge packages that the AI loads on-demand based on user intent.

1. **Create Directory:** `antigravity/skills/<category>/<your-skill-name>` (Categories: `core`, `tech`, `process`, `custom`).
2. **Add `SKILL.md`:** Must contain YAML frontmatter with a keyword-rich `description` (used by the AI to auto-trigger the skill). Keep the content concise: use tables and code snippets instead of verbose text.
3. **Register & Validate:** Add it to `registry.min.json` and validate using `make audit`.

👉 For full instructions, templates, and best practices, refer to the detailed [**Skills Guide**](docs/skills-guide.md).

---

## 🔗 Documentation

- [Architecture](ARCHITECTURE.md) - Deep dive into how the system works.
- [Component Guide](docs/components.md) - Understanding Rules, Workflows, and the Skill loading protocol.
- [Governance (GEMINI.md)](GEMINI.md) - Operational rules and request classification logic.
- [Skills Guide](docs/skills-guide.md) - Detailed guide on building and customizing your own skills.

---

## 🙏 Acknowledgments

This framework's rigorous process execution, strict behavioral gates, and core workflow skills (including TDD, systematic debugging, planning, and multi-agent coordination) are heavily inspired by and adapted from the [obra/superpowers](https://github.com/obra/superpowers) methodology.
