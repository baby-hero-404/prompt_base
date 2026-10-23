---
name: tech-research-framework
description: "Use when researching new technologies, understanding internal architectures, building Proof of Concepts (POCs), benchmarking, and writing technical documentation. Triggers on research, poc, new technology."
---

# Engineering Technology Research & POC Standard (Staff Engineer Framework)

> This framework provides a scalable engineering workflow. Not every artifact is mandatory. Select the appropriate level of documentation, testing, benchmarking, and operational practices based on technology complexity and project maturity.

## 0. Project Initialization Phase

Before implementation, define the project scope. If any core parameters are missing or ambiguous, the **Agent MUST ask for clarification** instead of guessing defaults:

```yaml
project:
  technology: Redis # e.g. Redis, Kafka, ClickHouse
  domain: Distributed Cache # e.g. Distributed Cache, Message Queue, OLAP
  scenario: Rate Limiter # e.g. Event-driven payment pipeline, Realtime Leaderboard
  implementation_language: Go # e.g. Go, Python, Java, Rust, Node.js
  maturity_level: Engineering # Learning | Engineering | Production Simulation
  objective:
    - Understand architecture
    - Build realistic scenario POC
    - Benchmark performance vs baseline
```

## 0.5 Problem Definition Phase

Before selecting technology, define the core problem to answer "Why does this technology exist in this context?":
- **Business/technical problem**: The core issue to solve (e.g., Build realtime leaderboard).
- **Functional requirements**: What the system must do.
- **Non-functional requirements**: Scale, latency, consistency needs (e.g., Latency <10ms, 100k updates/sec, Eventual consistency acceptable).
- **Constraints**: Limitations (e.g., Limited infrastructure, strict budget).

## 1. Purpose

This framework defines the standard to:
- Research a new technology.
- Understand deep internal architecture.
- Build a Proof of Concept (POC).
- Benchmark real-world capabilities against baselines.
- Write professional technical documentation.
- Create reusable engineering artifacts.

Applies to: Distributed Systems, Database, Message Queue, Cache, Search Engine, Cloud Native Technology, Infrastructure Components.

## 2. Project Structure Standard

See [`references/structure-and-deliverables.md`](references/structure-and-deliverables.md) (section 2) for the required directory layout.

## 3. Language Independent Design

Projects can use any language. The agent determines project parameters during initialization:
- `implementation_language`: (e.g. Go, Python, Java, Rust, Node.js)
- `domain`: (e.g. Message Queue, Distributed Cache, Search Engine)
- `scenario`: (e.g. Event-driven payment pipeline, Realtime Leaderboard)

**NOTE**: Do NOT write `implementation_language=...` or `domain=...` at the top of `README.md` or any source/doc files. These are purely internal parameters for context.

Language choice guidance:
- **Go**: Distributed system, infra, network
- **Python**: Experiment, data analysis, automation
- **Java/Kotlin**: Enterprise ecosystem
- **Rust**: Performance/system programming
- **Node.js**: API/event-driven demo

## 4. Recommended Deliverables

See [`references/structure-and-deliverables.md`](references/structure-and-deliverables.md) (section 4) for the deliverable list and templates.

## 5. Infrastructure Standard

- Do not install technology directly (e.g., `apt install`).
- Use containerized infrastructure whenever external dependencies are required. Docker Compose is the default local orchestration method.
- **Requirements**: Reproducible, Version pinned, Config externalized via `.env` (no hardcoding ports/hosts in Makefile), Health check on services, `depends_on` with `service_healthy` condition, Persistent volume.

## 6. Automation Standard

Use `Makefile` as the entry point, wrapping the language's modern package manager (`uv`/`poetry` for Python, `pnpm` for Node, `cargo` for Rust, `go` for Go).
Standard command set to maintain consistency across repos:
- `setup`: Install dependencies and prepare environment.
- `infra-up`: Start containerized dependencies (if any).
- `infra-down`: Stop and remove containerized dependencies.
- `test`: Run unit and integration tests.
- `lint`: Run code formatters and linters.
- `run`: Start the application/demo.
- `benchmark`: Execute performance tests.
- `docs`: Generate or serve documentation.
- `clean`: Remove build artifacts and temporary files.
- `all`: Install -> Start Infrastructure -> Run Test -> Run Benchmark -> Generate Report.

## 7. Code Quality & Observability Standard

POCs must demonstrate engineering practices proportional to their defined maturity level.
- **Structure**: MUST strictly follow the idiomatic project layout of the chosen `PROJECT_LANGUAGE`. Do NOT force Go's layout (`cmd/`, `internal/`, `pkg/`) onto Python, Node.js, Java, or Rust projects.
- **Dependency Management**: Dependencies MUST have exact or compatible version constraints (e.g. `pyproject.toml`/`requirements.txt` with locked versions, `package-lock.json`, `go.mod`).
- **Environment & Config**: All hostnames, ports, and credentials MUST be externalized into `.env` and typed configs (e.g. `pydantic-settings`, `viper`).
- **Observability Requirements by Maturity Level**:
  - **Level 1**: Basic logging.
  - **Level 2**: Structured logging (JSON/KV) and Health Endpoints (`/health`, `/ready`).
  - **Level 3**: Metrics (Prometheus format), Distributed Tracing, and Monitoring integration.

## 8. Resilience & Failure Injection (Maturity Level 3)

For Maturity Level 3 projects, resilience testing must be documented and automated where possible:
- **Container Failure**: `docker kill <service>` -> observe failover / retry behavior.
- **Network Latency/Partition**: Inject delay via `toxiproxy` or `tc` -> observe timeout & circuit breaker.
- **Graceful Shutdown**: Send `SIGTERM` -> verify pending messages/transactions flush cleanly.
- **Scaling Validation**: Add node, remove node, rebalance workload -> observe system recovery and stability.

<!-- contract:ignore -->
## 9. CI/CD (Optional)

CI/CD is recommended when:
- Multiple contributors are involved.
- Long-running tests are required.
- Benchmark regression matters.
- Documentation generation is automated.

Use CI pipelines when automation value justifies the complexity (e.g. GitHub Actions `.github/workflows/ci.yml`).
<!-- /contract:ignore -->

## 10. Maturity Level

Define the project's maturity level during initialization:
- **Maturity Level 1 - Learning**: Understand concepts (e.g., Redis data structure explorer). Focus on simplicity and clarity.
- **Maturity Level 2 - Engineering**: Build a realistic system (e.g., Distributed rate limiter, Event-driven pipeline). Focus on clean architecture and tests.
- **Maturity Level 3 - Production Simulation**: Near production readiness (Includes Observability, Resilience/Failure injection, Load testing, Scaling test).

<!-- contract:ignore -->
## 11. Output Acceptance Criteria

Before declaring the task complete, the agent MUST verify this checklist:

- [ ] Project can run on a clean machine without hidden dependencies
- [ ] Infrastructure orchestrations (e.g., `docker-compose up`) run without errors
- [ ] `make all` / setup commands execute cleanly
- [ ] `README.md` setup instructions verified
- [ ] Benchmark baseline and result report generated in `benchmark/result/`
- [ ] Practice scenarios and edge cases documented in `docs/practice_scenarios.md`
- [ ] Engineering decisions justified in `docs/decision_summary.md`
- [ ] Security considerations documented in `docs/security.md`
- [ ] System and Sequence diagrams included in `docs/architecture.md`
- [ ] Unit & Integration tests passing
- [ ] No hardcoded secrets, ports, or hostnames in code/Makefile
<!-- /contract:ignore -->

## 12. Final Workflow

1. Initialization Phase (Confirm Technology, Language, Maturity Level, Goals)
2. Problem Definition Phase (Business problem, Requirements, Constraints)
3. Technology Profile & Internal Architecture Research
4. Build Infrastructure & Configuration
5. Implement POC
6. Observability & Resilience Setup (for Maturity Level 2/3)
7. Benchmark against Baseline
8. Analyze Bottlenecks & Results
9. Write Engineering Documentation (Decision Summary, Security, ADR, Architecture, Practice Scenarios, README)
10. Verify Output Acceptance Criteria
11. Final Delivery
