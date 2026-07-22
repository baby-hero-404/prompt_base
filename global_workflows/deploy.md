---
description: Production deployment with pre-flight checks and safety procedures.
---

# /deploy - Production Deployment Procedure

$ARGUMENTS

---

## 5-Phase Deployment Safety

1. **Prepare**: Verify local build passes 100% (`npm run build`, `npm run lint`).
2. **Backup**: Backup production database / state before deployment.
3. **Deploy**: Push to target platform (Vercel/Railway/VPS).
4. **Verify**: Check health check endpoints and inspect server logs.
5. **Confirm/Rollback**: Rollback immediately if errors occur; confirm if healthy.
