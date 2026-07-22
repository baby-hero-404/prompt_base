# Dockerfile Best Practices & Multi-Stage Builds

## 1. Multi-Stage Build Pattern
Separate build environment from runtime to minimize image size.

```dockerfile
# Stage 1: Build
FROM node:18-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# Stage 2: Runtime
FROM node:18-alpine AS runtime
WORKDIR /app
COPY --from=build /app/dist ./dist
COPY --from=build /app/node_modules ./node_modules
CMD ["node", "dist/index.js"]
```

---

## 2. Layer Caching Optimization
Order commands from least-frequently changed to most-frequently changed.
- ✅ **ALWAYS** copy `package.json` and install dependencies BEFORE copying the rest of the source code.

---

## 3. Image Size Reduction
- **Base Image**: Prefer `alpine` or `distroless` over full Debian/Ubuntu images.
- **Cleanup**: Remove package manager cache in the same `RUN` layer (e.g., `apk add --no-cache ...`).
- **.dockerignore**: Exclude `node_modules`, `.git`, and build logs from the build context.

---

## 4. Advanced: BuildKit Mounts
Use `--mount=type=cache` to speed up dependency installation across builds.
```dockerfile
RUN --mount=type=cache,target=/root/.npm \
    npm ci
```
