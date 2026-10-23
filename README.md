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
├── agents/                ← Agent definitions
├── global_workflows/      ← Workflows
├── skills/                ← Skills
└── projects/              ← Project templates
```

---

## 🏗️ Architecture: 3 Component Types

Prompt Base is built on **3 global component types**. Each has a dedicated storage location and activation model:

| # | Component | Purpose | Storage Path | Activation |
|---|-----------|---------|-------------|------------|
| 1 | **Rules** | Persistent behavior (coding style, safety, patterns) | `~/.gemini/GEMINI.md` | Always active |
| 2 | **Workflows** | On-demand modes triggered via slash commands | `~/.gemini/config/global_workflows/*.md` | `/plan`, `/review`, `/create`, etc. |
| 3 | **Skills** | Auto-triggered knowledge modules | `~/.gemini/config/skills/*/SKILL.md` | Automatic (keyword match) |

### How It Fits Together

```
~/.gemini/                          ← FRAMEWORK_ROOT
├── GEMINI.md                       ← Rules (always active, self-contained)
├── ARCHITECTURE.md                 ← System map
├── registry.min.json               ← Unified metadata index
├── agents/                         ← 14 Specialist Agent definitions
├── global_workflows/               ← Workflows (slash commands)
│   ├── brainstorm.md
│   ├── plan.md
│   ├── create.md
│   └── ...
├── skills/                         ← Skills (auto-trigger)
│   ├── core/
│   ├── tech/
│   ├── process/
│   └── custom/
└── projects/                       ← Project templates
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
- Prompt-injection & supply-chain safety (only the user gives instructions; new dependencies are untrusted; never run unread scripts)

> You don't need to do anything — rules are always enforced.

### 2. Skills (Auto-Triggered)

You don't need to manually load skills. Simply describe what you want to do, and the orchestrator will activate the relevant skill based on your intent.

- **Trigger**: Use keywords like "design", "build", "fix", "analyze", or specific tech stacks like "React" or "Python".
- **Example**: "I need to design a landing page" → Triggers `ux-ui-pro-max`
- **Example**: "Refactor this API for performance" → Triggers `backend-specialist` + `performance-optimizer`
- **Example**: "Write unit tests for this module" → Triggers `test-engineer` + `testing-patterns`

Skills are stored at `~/.gemini/config/skills/*/SKILL.md`.

### 3. Workflows (Slash Commands)

Slash commands are on-demand automation scripts that orchestrate multiple Specialist Agents for complex tasks. They follow a logical development lifecycle:

| Command | Description | When to Use |
|---------|-------------|-------------|
| `/brainstorm [topic]` | Structured exploration with 3+ approaches, pros/cons, effort estimates | Exploring options before committing |
| `/plan [task]` | Socratic discovery → technical blueprint (into the task's OpenSpec set at `docs/openspecs/<task>/`) | Before any complex feature (**no code**) |
| `/create [feature]` | Full-stack implementation via coordinated expert agents | Building new features or prototypes |
| `/enhance [feature]` | Iterative improvement with dependency management | Adding modules to existing code |
| `/test [file/feature]` | Unit/integration tests (AAA pattern), coverage checks | Ensuring code reliability |
| `/debug [issue]` | Systematic root-cause analysis | Tricky bugs requiring deep investigation |
| `/review` | Formal audit of staged changes | Before committing code |
| `/deploy` | Production deployment with pre-flight checks | Releasing to production/staging |
| `/status` | Project-wide health check | Checking pending tasks & agent assignments |
| `/init-context` | Initialize context (MVC), read-only | Start of a conversation in an unfamiliar project |
| `/init-memory` | Opt-in persistent memory in `docs/ai/` (profile, invariants, decisions) | Only in projects that need memory across sessions |
| `/deep-solve` | JIT Knowledge workflow | Complex multi-domain problems |
| `/restructure` | Maintenance & registry update | Framework maintenance |
| `/orchestrate` | Multi-agent coordination | Tasks requiring multiple perspectives |
| `/ux-ui-pro` | Design intelligence mode | Premium UI/UX design work |

Workflows are stored at `~/.gemini/config/global_workflows/*.md`.

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

1. **Scaffold:** Run `python scripts/create_skill.py <your-skill-name>` to auto-generate the directory, template, and register it.
2. **Edit:** Add your knowledge, tables, and code snippets to the generated `SKILL.md`.
3. **Verify:** Run `make skill-check SKILL=<name>` to pass the 3-Tier Quality Gates (Lint, Trigger Precision, Contract Check).
4. **Evaluate (Optional):** Run `make skill-eval SKILL=<name>` to run an LLM-as-judge regression test if your skill has `eval: required`. 
   *(Note: requires `GEMINI_API_KEY` in your `.env` file. You can also override the default model by setting `GEMINI_MODEL="gemini-2.0-flash"`).*

👉 For full instructions, templates, and best practices, refer to the detailed [**Skills Guide**](docs/skills-guide.md).

---

## 🔗 Documentation

- [Architecture](ARCHITECTURE.md) - Deep dive into how the system works.
- [Component Guide](docs/components.md) - Understanding Rules, Workflows, and the Skill loading protocol.
- [Governance (GEMINI.md)](GEMINI.md) - Operational rules and request classification logic.
- [Skills Guide](docs/skills-guide.md) - Detailed guide on building and customizing your own skills.
- [Quality Gates Summary](docs/quality-gates-summary.md) - Overview of all testing and verification pipelines.

---

## 🙏 Acknowledgments & External References

This framework's rigorous process execution, strict behavioral gates, and specialized domain skills are inspired by and adapted from leading open-source projects and engineering doctrines:

- **Core Methodology & Socratic Gates**: Adapted from **[obra/superpowers](https://github.com/obra/superpowers)** (TDD, systematic debugging, planning, and multi-agent coordination).
- **Token Efficiency & JIT Protocols**: Adapted from **[JuliusBrussee/caveman](https://github.com/JuliusBrussee/caveman)** (terse output compression, dynamic section-level context filtering) and **[rtk-ai/rtk](https://github.com/rtk-ai/rtk)** (`rtk-token-killer` terminal output compression).
- **Design Intelligence & Craft Rules**: Adapted from **[OpenDesign](https://github.com/nexu-io/open-design)** (`taste-skill`, universal craft rules for typography/color/motion, and 151 portable design systems).
- **Next.js & React 19 Best Practices**: Adapted from **[vercel-labs/agent-skills](https://github.com/vercel-labs/agent-skills)** (70 atomic performance rules, eliminating waterfalls, server actions security, `after()` API) and **[gohypergiant/agent-skills](https://github.com/gohypergiant/agent-skills)** (`accelint-react-best-practices`, "NEVER Do React" anti-patterns catalog, React Compiler gating).
- **Flutter & Mobile Architecture**: Adapted from Google's **[flutter/agent-plugins](https://github.com/flutter/agent-plugins)** (layout constraint diagnostics, task verification loops) and **[Mauriciog87/flutter-agent-skill](https://github.com/Mauriciog87/flutter-agent-skill)** (Three-Layer MVVM architecture, Riverpod/BLoC state matrix, memory disposal lifecycle, and Flame 2D game development).
- **Golang Enterprise Engineering**: Adapted from **[cexll/golang-base-practices-skills](https://github.com/cexll/golang-base-practices-skills)** (4-layer DDD architecture, closure-based GORM transaction safety, `errgroup` concurrency, table-driven testing) and **[mfmezger/ai_agent_dotfiles](https://github.com/mfmezger/ai_agent_dotfiles)** ("Concrete types first", caller-defined minimal interfaces, context hygiene, and critical Go footguns catalog).

### 📚 Reference Repositories & Discovery Reports

| Repository | Domain / Focus | Key Contributions | Discovery Report |
|---|---|---|---|
| [obra/superpowers](https://github.com/obra/superpowers) | Methodology & Workflows | TDD, planning, systematic debugging, behavioral gates | — |
| [JuliusBrussee/caveman](https://github.com/JuliusBrussee/caveman) | Token Compression | Terse mode, JIT v2 markdown section filtering | [DISCOVERY-caveman.md](docs/discovery/DISCOVERY-caveman.md) |
| [rtk-ai/rtk](https://github.com/rtk-ai/rtk) | Terminal Token Reduction | Command output filtering via `rtk-token-killer` | — |
| [nexu-io/open-design](https://github.com/nexu-io/open-design) | Design Systems & UI Craft | `ux-ui-pro-max`, anti-slop rules, design dials, tokens | [DISCOVERY-open-design-ui.md](docs/discovery/DISCOVERY-open-design-ui.md) |
| [vercel-labs/agent-skills](https://github.com/vercel-labs/agent-skills) | Next.js 15+ & React Performance | 70 atomic rules, eliminating waterfalls, server actions auth, `after()` | [DISCOVERY-nextjs-agent-skills.md](docs/discovery/DISCOVERY-nextjs-agent-skills.md) |
| [gohypergiant/agent-skills](https://github.com/gohypergiant/agent-skills) | React 19 Defensiveness | "NEVER Do React" catalog, React Compiler gating | [DISCOVERY-nextjs-agent-skills.md](docs/discovery/DISCOVERY-nextjs-agent-skills.md) |
| [flutter/agent-plugins](https://github.com/flutter/agent-plugins) | Flutter / Dart (Official) | Layout constraint diagnostics, task feedback loops, MCP | [DISCOVERY-flutter-skills.md](docs/discovery/DISCOVERY-flutter-skills.md) |
| [Mauriciog87/flutter-agent-skill](https://github.com/Mauriciog87/flutter-agent-skill) | Flutter Architecture & Gaming | Three-Layer MVVM, Riverpod/BLoC matrix, Flame 2D engine | [DISCOVERY-flutter-skills.md](docs/discovery/DISCOVERY-flutter-skills.md) |
| [cexll/golang-base-practices-skills](https://github.com/cexll/golang-base-practices-skills) | Enterprise Go & Microservices | 4-layer DDD layout, GORM transactions, `errgroup`, 99% coverage | [DISCOVERY-golang-skills.md](docs/discovery/DISCOVERY-golang-skills.md) |
| [mfmezger/ai_agent_dotfiles](https://github.com/mfmezger/ai_agent_dotfiles) | Idiomatic Go & Footguns | "Concrete types first", caller interfaces, context propagation | [DISCOVERY-golang-skills.md](docs/discovery/DISCOVERY-golang-skills.md) |

### 📦 Installing RTK

To install the `rtk` CLI utility on Linux/macOS:

```bash
# Run the installation script
curl -fsSL https://raw.githubusercontent.com/rtk-ai/rtk/refs/heads/master/install.sh | sh

# The binary is installed to ~/.local/bin. Add it to your PATH if needed:
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc  # or ~/.zshrc
```

