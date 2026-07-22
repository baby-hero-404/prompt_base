# API Style Selection (2025)

> REST vs GraphQL vs tRPC - Hangi durumda hangisi?

## Decision Tree

```
Who are the API consumers?
│
├── Public API / Multiple platforms
│   └── REST + OpenAPI (widest compatibility)
│
├── Complex data needs / Multiple frontends
│   └── GraphQL (flexible queries)
│
├── Next.js App Router (React 19+)
│   └── Server Actions (RPC over HTTP)
│
├── TypeScript frontend + backend (monorepo)
│   └── tRPC (end-to-end type safety)
│
├── LLM Tokens / Generative AI
│   └── Streaming HTTP / SSE (Vercel AI SDK)
│
├── Real-time / Event-driven
│   └── WebSocket + AsyncAPI
│
└── Internal microservices
    └── gRPC (performance) or REST (simplicity)
```

## Comparison

| Factor | REST | GraphQL | tRPC | Next.js Apps | AI Chat |
|--------|------|---------|------|--------------|---------|
| **Best for** | Public APIs | Complex apps | TS monorepos | Next.js Apps | AI Chat |
| **Learning curve** | Low | Medium | Low (if TS) | Low | Medium |
| **Over/under fetching** | Common | Solved | Solved | Solved | N/A |
| **Type safety** | Manual (OpenAPI) | Schema-based | Automatic | Automatic | Manual |
| **Caching** | HTTP native | Complex | Client-based | Next.js Cache | None |

## Selection Questions

1. Who are the API consumers?
2. Is the frontend TypeScript?
3. How complex are the data relationships?
4. Is caching critical?
5. Public or internal API?
