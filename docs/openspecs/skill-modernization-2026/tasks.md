# Tasks: Skill Modernization 2026

## P0 — Critical

### Task 1.1: Add vector-DB / RAG guidance to `database-design`
> Links to: REQ-001

**Acceptance Criteria:**
- [ ] pgvector, Pinecone, and Milvus each appear with a one-line selection guideline (when to pick which)
- [ ] Embedding-store schema modeling is documented distinctly from relational schema design
- [ ] If added as a new reference file (matching the skill's existing `database-selection.md`/`orm-selection.md` layering), it's linked from the main `SKILL.md` content map
- [ ] YAML `description` frontmatter updated if vector/RAG keywords should trigger this skill

### Task 1.2: Update `mcp-builder` transport and auth to the 2025 MCP spec
> Links to: REQ-002

**Acceptance Criteria:**
- [ ] Streamable HTTP documented as the standard/recommended transport
- [ ] SSE explicitly marked as superseded (not removed — still relevant for legacy servers, but not presented as an equal current choice)
- [ ] OAuth 2.1 auth-flow section added for remote MCP servers
- [ ] YAML `description` frontmatter reviewed for accuracy

## P1 — High

### Task 2.1: Deepen `react-patterns` RSC / Server Actions / concurrent rendering
> Links to: REQ-M01

**Acceptance Criteria:**
- [ ] Server vs. Client Component decision rule added (not just a one-line mention)
- [ ] Server Actions worked example added (form submission or mutation)
- [ ] `useTransition`/Suspense concurrent-rendering example added

### Task 2.2: Update `nextjs-best-practices` for Next.js 15 defaults
> Links to: REQ-M02

**Acceptance Criteria:**
- [ ] Target Next.js version(s) stated explicitly near the top of the file
- [ ] Uncached-by-default `fetch` behavior documented (replacing the pre-15 cache-by-default description)
- [ ] PPR, Turbopack, and `use cache` each covered

### Task 2.3: Add Server Actions + AI streaming to `api-patterns`
> Links to: REQ-003

**Acceptance Criteria:**
- [ ] Server Actions added as a selectable API style alongside REST/GraphQL/tRPC
- [ ] AI streaming response pattern documented (SSE for LLM tokens / Vercel AI SDK)

### Task 2.4: Add WASM/microVM runtimes to `docker-expert`
> Links to: REQ-M03

**Acceptance Criteria:**
- [ ] WASM containers documented as an alternative to traditional Docker containers
- [ ] microVM (Firecracker-style) runtimes documented
- [ ] Selection guideline added (traditional Docker vs. WASM vs. microVM)

### Task 2.5: Add spatial computing / voice UI to `mobile-design`
> Links to: REQ-M04

**Acceptance Criteria:**
- [ ] visionOS/XR added as a selectable platform in the platform-selection questions
- [ ] Voice-driven/conversational UI guidance added (new section or reference file, matching the skill's existing 16-reference-file layering)

### Task 2.6: Add LLM/AI-agent NPC integration to `game-development`
> Links to: REQ-004

**Acceptance Criteria:**
- [ ] At least one LLM-driven NPC dialogue or procedural-narrative pattern documented
- [ ] Documented interplay with existing state-machine/ECS patterns (not a bolted-on separate section)

### Task 2.7: Refresh `coding-standards` version pins and mandate framing
> Links to: REQ-M05

**Acceptance Criteria:**
- [ ] Every pinned version (Next.js, Node.js, etc.) confirmed current at time of edit
- [ ] "Avoid Express/Prisma"-style directives rewritten as trade-off notes
- [ ] Change cross-checked against `database-design`'s existing Drizzle-vs-Prisma framing for consistency

## P2 — Medium

### Task 3.1: State TS version target in `typescript-expert`
> Links to: REQ-M06

**Acceptance Criteria:**
- [ ] Target TypeScript version(s) stated in the main `SKILL.md`, not only implied by reference files
- [ ] The three reference files (type-gymnastics, performance-and-build, checklists-and-decisions) reviewed and confirmed current or updated

### Task 3.2: Resolve `seo-fundamentals` / `geo-fundamentals` overlap
> Links to: REQ-M07

**Acceptance Criteria:**
- [ ] Decision made and recorded: merge the two skills, or keep separate with explicit cross-reference
- [ ] If kept separate: `seo-fundamentals` links to `geo-fundamentals` for AI-answer-ranking topics, and both YAML `description` fields are distinguishable enough for correct auto-trigger routing
- [ ] If merged: old skill's directory removed, `registry.min.json` regenerated, no dangling references to the removed skill name elsewhere in the repo

### Task 3.3: Add OWASP/AI attack coverage to `red-team-tactics`
> Links to: REQ-M08

**Acceptance Criteria:**
- [ ] At least one OWASP-aligned web/cloud/container attack technique added
- [ ] At least one AI/LLM-specific attack technique added (prompt injection, model exfiltration, etc.)

### Task 3.4: Version-date `red-teaming`'s OWASP reference
> Links to: REQ-M09

**Acceptance Criteria:**
- [ ] OWASP Top 10 reference in `red-teaming` cites the same revision year as `vulnerability-scanner` ("2025")

## P3 — Low

### Task 4.1: Point `parallel-agents` at a live agent source
> Links to: REQ-M10

**Acceptance Criteria:**
- [ ] "Available Agents" table replaced with a reference to wherever agents are actually configured for a given project (not a hardcoded static list)

### Task 4.2: Clean up `behavioral-modes` dating and dangling heading
> Links to: REQ-M11

**Acceptance Criteria:**
- [ ] "(2025)" removed from the "Multi-Agent Collaboration Patterns" heading
- [ ] "Combining Modes" heading either filled in with content or removed

## P0 — Gating (do last, after any task above is merged)

### Task 5.1: Regenerate registry and redeploy
> Links to: all REQs above

**Acceptance Criteria:**
- [ ] `make registry` run after each completed skill edit (or batched at the end of a session — not left until the very end of the whole spec)
- [ ] `make install-claude` / `make install-gemini` run to redeploy
- [ ] Spot-check: `grep` the updated skill name/keywords against `registry.min.json` to confirm the description change (if any) took effect
