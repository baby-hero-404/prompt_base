# Docker Compose & Orchestration Patterns

## 1. Service Dependencies
Use `depends_on` with `condition: service_healthy` to ensure startup order.
```yaml
services:
  app:
    depends_on:
      db:
        condition: service_healthy
```

---

## 2. Health Checks
**Mandatory** for production resilience and orchestration.
```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:3000/health"]
  interval: 30s
  timeout: 10s
  retries: 3
```

---

## 3. Network Isolation
Isolate backend services from the public internet using custom bridge networks.
```yaml
networks:
  frontend:
  backend:
    internal: true
```

---

## 4. Volume Persistence
- Use **Named Volumes** for databases (e.g., `postgres_data:/var/lib/postgresql/data`).
- Use **Bind Mounts** ONLY for development shadowing (e.g., `- .:/app`).
