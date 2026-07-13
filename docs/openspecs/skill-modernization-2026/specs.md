# Specs: Skill Modernization 2026

## Added Requirements

### REQ-001: `database-design` covers vector databases and RAG modeling
> ❌ Status: Not Started

**Scenario:**
- WHEN an agent loads `database-design` to choose a data layer for a RAG or embedding-search feature
- THEN the skill must present pgvector, Pinecone, and Milvus as options with a selection guideline
- AND it must cover embedding-store schema modeling (vector column/index design) distinct from relational schema design

### REQ-002: `mcp-builder` teaches the current MCP transport and auth spec
> ❌ Status: Not Started

**Scenario:**
- WHEN an agent loads `mcp-builder` to choose a transport for a new MCP server
- THEN Streamable HTTP must be presented as the standard/recommended transport
- AND SSE must be marked as superseded, not listed as an equal current option
- AND an OAuth 2.1 auth-flow section must exist for remote MCP servers

### REQ-003: `api-patterns` covers Server Actions and AI streaming
> ❌ Status: Not Started

**Scenario:**
- WHEN an agent loads `api-patterns` to choose between API styles for a full-stack app with an LLM feature
- THEN Server Actions must appear as a selectable API style alongside REST/GraphQL/tRPC
- AND a streaming-response pattern for LLM token output (SSE, Vercel AI SDK) must be documented

### REQ-004: `game-development` covers LLM/AI-agent NPC integration
> ❌ Status: Not Started

**Scenario:**
- WHEN an agent loads `game-development` to design NPC behavior
- THEN the skill must document at least one pattern for LLM-driven NPC dialogue or procedural narrative generation
- AND clarify how it composes with the existing state-machine/ECS patterns already in the skill

## Modified Requirements

### REQ-M01: `react-patterns` gives RSC/Server Actions/concurrent rendering real coverage
> ⚠️ Status: In Progress (React 19 hooks section already exists; RSC/Server Actions/concurrent rendering are one-line mentions only)

**Scenario:**
- WHEN an agent loads `react-patterns` to decide whether a component should be a Server or Client Component
- THEN the skill must give a decision rule, not a one-line mention
- AND Server Actions must have a worked example (form submission or mutation)
- AND concurrent rendering (`useTransition`, Suspense boundaries) must be covered with a usage example

### REQ-M02: `nextjs-best-practices` reflects Next.js 15 caching and build defaults
> ❌ Status: Not Started

**Scenario:**
- WHEN an agent loads `nextjs-best-practices` for a new App Router project
- THEN the skill must state the Next.js version(s) it targets explicitly
- AND document that `fetch` is uncached by default (Next 15 behavior change) rather than the pre-15 cache-by-default model
- AND cover Partial Prerendering (PPR), Turbopack, and the `use cache` directive

### REQ-M03: `docker-expert` covers WASM/microVM runtimes
> ❌ Status: Not Started

**Scenario:**
- WHEN an agent loads `docker-expert` to choose a container runtime for an edge/serverless deployment
- THEN WASM containers and microVM (Firecracker-style) runtimes must be presented as alternatives to traditional Docker containers
- AND the skill must give a selection guideline (when traditional Docker vs. WASM vs. microVM applies)

### REQ-M04: `mobile-design` covers spatial computing and voice UI
> ❌ Status: Not Started

**Scenario:**
- WHEN an agent loads `mobile-design`'s platform-selection questions for a new mobile app
- THEN visionOS/XR must appear as a selectable platform alongside iOS/Android
- AND voice-driven/conversational UI guidance must exist for apps that need it

### REQ-M05: `coding-standards` version pins are current and non-mandate framing for trade-offs
> ❌ Status: Not Started

**Scenario:**
- WHEN an agent reads `coding-standards`' "Modern Tech Mandate" table
- THEN every pinned version must be the current stable major version at time of writing, not a stale 2024-25 snapshot
- AND framework choices with real trade-offs (Prisma vs. Drizzle, Express vs. Hono/Fastify) must be presented as a trade-off note, not an "avoid X" directive

### REQ-M06: `typescript-expert` states a TS version target in the main file
> ❌ Status: Not Started

**Scenario:**
- WHEN an agent loads `typescript-expert` without reading its reference sub-files
- THEN the main `SKILL.md` must state the TypeScript version(s) the guidance targets
- AND the three reference files (type-gymnastics, performance-and-build, checklists-and-decisions) must be confirmed current or updated

### REQ-M07: `seo-fundamentals` and `geo-fundamentals` no longer silently overlap
> ❌ Status: Not Started

**Scenario:**
- WHEN an agent loads `seo-fundamentals` for a task that is actually about ranking in AI answers/AI Overviews
- THEN the skill must either cover GEO itself or explicitly point to `geo-fundamentals`
- AND the two skills' YAML `description` frontmatter must be distinguishable enough for correct auto-trigger routing

### REQ-M08: `red-team-tactics` covers OWASP-aligned and AI attack surfaces
> ❌ Status: Not Started

**Scenario:**
- WHEN an agent loads `red-team-tactics` for an engagement scoped to a web application or AI feature
- THEN at least one OWASP-aligned web attack technique must be present
- AND at least one AI/LLM-specific attack technique (prompt injection, model exfiltration) must be present

### REQ-M09: `red-teaming`'s OWASP reference is version-dated
> ❌ Status: Not Started

**Scenario:**
- WHEN an agent compares `red-teaming`'s OWASP Top 10 reference to `vulnerability-scanner`'s
- THEN both must cite the same OWASP revision year explicitly

### REQ-M10: `parallel-agents` references a live agent source instead of a static table
> ❌ Status: Not Started

**Scenario:**
- WHEN the set of configured agents changes in a project
- THEN `parallel-agents`' "Available Agents" section must not require a manual edit to stay accurate (i.e., it points to a registry/config file rather than hardcoding agent names)

### REQ-M11: `behavioral-modes` has no stale dating or dangling headings
> ❌ Status: Not Started

**Scenario:**
- WHEN an agent reads the "Multi-Agent Collaboration Patterns" section of `behavioral-modes`
- THEN the section heading must not hardcode a specific year
- AND the "Combining Modes" heading must either contain content or be removed

## Removed Requirements
- None
