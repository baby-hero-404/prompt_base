# Docker Review Checklist & Diagnostics

## 1. Code Review Checklist

### Optimization
- [ ] Multi-stage builds implemented?
- [ ] `.dockerignore` optimized?
- [ ] Dependencies installed BEFORE source code copy?

### Security
- [ ] Running as non-root (`USER`)?
- [ ] Sensitive info NOT in `ENV`?
- [ ] Distroless or Minimal image used?
- [ ] Healthcheck implemented?

### Compose/Runtime
- [ ] Resource limits defined?
- [ ] Internal networks used for backend?
- [ ] Restart policy set to `always` or `on-failure`?

---

## 2. Diagnostics Commands

| Context | Command |
|---------|---------|
| **Build Problems** | `docker build --no-cache -t debug .` |
| **Runtime Logs** | `docker logs -f <container_id>` |
| **Inspect Env** | `docker exec <id> env` |
| **Resource Usage** | `docker stats` |
| **Config Validation** | `docker-compose config` |

---

## 3. Common Issue Fixes

- **"No space left on device"**: Run `docker system prune`.
- **"Permission denied" on volumes**: Match the `UID/GID` between host and container.
- **"Connection refused"**: Check networking (service names are DNS in Compose).
- **Images too large**: Check if build tools were left in the final stage.
