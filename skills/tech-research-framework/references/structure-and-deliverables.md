# Structure and Deliverables

Sections 2 and 4 of `SKILL.md`. Loaded on demand.

## 2. Project Structure Standard

Every project should start from this structure and adapt based on technology characteristics:

```text
demo-[technology-name]/
├── README.md
├── docs/
│   ├── research.md
│   ├── architecture.md
│   ├── practice_scenarios.md
│   ├── benchmark.md
│   ├── decision_summary.md
│   ├── security.md
│   ├── troubleshooting.md
│   ├── adr/
│   │   └── 001-design-decision.md
│   └── media/
│       ├── architecture.png
│       └── sequence.png
├── infra/
│   ├── docker-compose.yml
│   ├── config/
│   └── scripts/
├── app/               # MUST follow idiomatic structure of PROJECT_LANGUAGE (e.g. Go uses cmd/pkg, Python uses src/ or module-name)
├── benchmark/
│   ├── load-test/
│   └── result/
├── scripts/
│   ├── export-docs/
│   └── automation/
├── Makefile
├── .env.example
└── .gitignore
```

## 4. Recommended Deliverables

While a comprehensive project typically includes these artifacts, adapt deliverables based on technology characteristics.

### A. README (`README.md`)
Must include:
1. **Quick Setup**: Step-by-step instructions to get the project running immediately.
2. **Learning Roadmap**: A structured guide on how to learn the technology through this project (what to read first, what components to explore).

**IMPORTANT**: Do NOT mention "tech-research-framework" or internal AI instructions in the generated README or project documentation. The output should appear as an authentic, professional open-source project.

<!-- contract:ignore -->
### B. Research Document (`docs/research.md`)
Must include:
1. **Technology Profile / Analysis Matrix**:
   - **Category**: (e.g. Message Queue, Distributed Database)
   - **Storage Model**: (e.g. Commit Log, LSM Tree, B-Tree, In-Memory)
   - **Consistency Model**: (e.g. Strong Consistency, Eventual, Linearizable)
   - **Replication & Scaling**: (e.g. Partition-based, Raft Consensus, Active-Passive)
   - **Delivery / Transaction Guarantees**: (e.g. At-least-once, Exactly-once, ACID)
   - **Performance Characteristics**: Primary bottleneck (e.g. Sequential disk write vs Memory latency), Latency factor, Throughput factor.
2. **Problem Statement**: What problem does this solve?
3. **Core Concepts & Architecture**: High-level design & memory/storage/network models.
4. **Failure Handling**: Crash, Network partition, Disk failure.
5. **Trade-offs**: Pros / Cons & alternatives.

### C. Architecture Document (`docs/architecture.md`)
Must include:
- **System Diagram**: Overall system components and connections.
- **Sequence Diagram**: Detailed request flow, failure recovery, and graceful shutdown flows.

### D. POC Implementation
- **Goal**: Simulate a real use case, not a toy demo.
- **Example**: Instead of simple SET/GET for Redis, build a Rate Limiter or API Gateway. Instead of simple Producer/Consumer for Kafka, build an Order Service -> Kafka -> Payment/Notification Service.

### E. Benchmark (`benchmark/`)
Must include:
- **Benchmark Environment**: Document reproducibility metadata in the report (Hardware: CPU, RAM, Disk. Software: OS, Docker version, Technology version. Workload: Dataset size, Concurrency, Duration).
- **Baseline Comparison**: Compare results against a baseline (e.g., In-Memory vs Disk-based, Redis GET vs DB query).
- **Metrics**: Performance (Throughput, TPS, MB/s), Latency (P50, P95, P99), Resource Usage (CPU, Memory, Network, Disk IO).
- **Report**: Save in `benchmark/result/report.md` with bottleneck analysis.

### F. Engineering Documentation
- **Decision Summary** in `docs/decision_summary.md`. Format: Problem, Candidates, Decision, Why, Trade-off. Used to justify the core technology choice.
- **ADR (Architecture Decision Record)** in `docs/adr/`. Must include Context, Decision, Alternative, and Trade-off.

### G. Practice & Edge Cases (`docs/practice_scenarios.md`)
- **Goal**: Help users practice step-by-step, remember theoretical concepts, and deeply understand edge cases through hands-on experimentation with the POC.
- **Interactive Scenarios**: Step-by-step commands or scripts to run against the built demo (e.g., publish a message, consume it, view logs). Maps directly to the theoretical concepts in `research.md`. Each scenario MUST define `Difficulty` (e.g., Beginner, Advanced) and `Goal` (e.g., Understand producer-consumer).
- **Edge Case Simulation**: Concrete steps to trigger and observe edge cases (e.g., kill a node during a transaction, simulate a network partition, inject malformed data, exceed rate limits, or fill up disk space). Each simulation MUST define `Difficulty` and `Goal`.
- **Behavior Analysis**: Expected outcomes for each step and why they happen based on the system's architecture.

### H. Security Consideration (`docs/security.md`)
Must review and document:
- **Secret management**, **Authentication**, **Authorization** (e.g., No password vs ACL in Redis, PLAINTEXT vs SSL/SASL in Kafka).
- **Network exposure**, **Container privilege**, and **Dependency vulnerability**.
<!-- /contract:ignore -->

