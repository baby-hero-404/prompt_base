# Docker Container Security & Hardening

## 1. Non-Root Execution
**Mandatory**: Never run as `root` in production.
```dockerfile
RUN addgroup -g 1001 -S nodejs && \
    adduser -S nextjs -u 1001 -G nodejs
USER nextjs
```

---

## 2. Secrets Management
- **Never use ENV for secrets**: Environment variables leak in `docker inspect` and logs.
- **Docker Secrets**: Use `/run/secrets/` in Swarm/Compose.
- **Build Secrets**: Use `--mount=type=secret` for build-time credentials.

---

## 3. Minimal Attack Surface
- Remove unnecessary tools (`curl`, `git`, `python`) from the final runtime image.
- Use **Distroless** (`gcr.io/distroless/nodejs`) for maximum security.

---

## 4. Runtime Hardening
- **Read-only Root FS**: `readonly_rootfs: true` in Compose.
- **Drop Capabilities**: Limit what the container can do to the host kernel.
- **Resource Limits**: Always define CPU and memory limits to prevent DoS by resource exhaustion.
