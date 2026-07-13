---
name: mcp-builder
description: "Use when building Model Context Protocol (MCP) servers, designing tool schemas, or implementing resource patterns."
allowed-tools: Read, Write, Edit, Glob, Grep
---

# MCP Builder

> Principles for building MCP servers.

---

## 1. MCP Overview

### What is MCP?

Model Context Protocol - standard for connecting AI systems with external tools and data sources.

### Core Concepts

| Concept | Purpose |
|---------|---------|
| **Tools** | Functions AI can call |
| **Resources** | Data AI can read |
| **Prompts** | Pre-defined prompt templates |

---

## 2. Server Architecture

### Project Structure

```
my-mcp-server/
├── src/
│   └── index.ts      # Main entry
├── package.json
└── tsconfig.json
```

### Transport Types

| Type | Use |
|------|-----|
| **Stdio** | Local, CLI-based (typical for Claude Desktop) |
| **Streamable HTTP** | Modern web-based (Recommended over SSE) |
| **SSE (Server-Sent Events)** | *Superseded*. Still relevant for legacy servers. |
| **WebSocket** | Real-time, bidirectional |

---

## 3. Tool Design Principles

### Good Tool Design

| Principle | Description |
|-----------|-------------|
| Clear name | Action-oriented (get_weather, create_user) |
| Single purpose | One thing well |
| Validated input | Schema with types and descriptions |
| Structured output | Predictable response format |

### Input Schema Design

| Field | Required? |
|-------|-----------|
| Type | Yes - object |
| Properties | Define each param |
| Required | List mandatory params |
| Description | Human-readable |

---

## 4. Resource Patterns

### Resource Types

| Type | Use |
|------|-----|
| Static | Fixed data (config, docs) |
| Dynamic | Generated on request |
| Template | URI with parameters |

### URI Patterns

| Pattern | Example |
|---------|---------|
| Fixed | `docs://readme` |
| Parameterized | `users://{userId}` |
| Collection | `files://project/*` |

---

## 5. Error Handling

### Error Types

| Situation | Response |
|-----------|----------|
| Invalid params | Validation error message |
| Not found | Clear "not found" |
| Server error | Generic error, log details |

### Best Practices

- Return structured errors
- Don't expose internal details
- Log for debugging
- Provide actionable messages

---

## 6. Multimodal Handling

### Supported Types

| Type | Encoding |
|------|----------|
| Text | Plain text |
| Images | Base64 + MIME type |
| Files | Base64 + MIME type |

---

## 7. Security Principles


## Extended References
For less-frequently-needed detail, see [`references/extended-reference.md`](references/extended-reference.md):
- Input Validation
- API Keys
- 8. Configuration
- Authentication (2025 Revision)
- Claude Desktop Config (Local/Basic)
- 9. Testing
- Test Categories
- 10. Best Practices Checklist
