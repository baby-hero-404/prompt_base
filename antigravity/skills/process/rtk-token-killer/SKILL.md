---
name: rtk-token-killer
description: "Use when running shell commands to reduce context token usage by 60-90%. Triggers on rtk, token killer."
allowed-tools: Read, Write, Edit, Glob, Grep
---

# RTK (Rust Token Killer) - Token-Optimized CLI Commands
Reduce context token usage by 60-90% by running shell commands with the `rtk` prefix.

## 🚨 Safety & Fallback (No-Install Protection)
If `rtk` is not installed on the system, running it directly will throw a "command not found" error. 
To prevent this, **always declare this safe fallback function** at the start of your terminal session before running any commands:
```bash
rtk() { if command -v rtk >/dev/null 2>&1; then command rtk "$@"; else "$@"; fi }
```

## 🛠️ Usage Rules
- Prefix all shell commands with rtk (e.g., rtk git status, rtk pytest).
- Prefix each segment in command chains: rtk git add . && rtk git commit -m "msg".
- If a command is not natively filtered by RTK, it will pass through safely and run normally.

## 📦 Key Supported CLI Filters
- **Git & PRs**: rtk git status/diff/log, rtk gh
- **Files & Search**: rtk ls, rtk tree, rtk find, rtk grep, rtk read, rtk diff
- **Tests & Linters**: rtk test, rtk err, rtk pytest, rtk cargo test, rtk jest, rtk tsc, rtk lint, rtk prettier
- **Languages & Packages**: rtk npm, rtk npx, rtk pnpm, rtk pip, rtk cargo, rtk go, rtk dotnet
- **DB, Cloud & Infrastructure**: rtk docker, rtk kubectl, rtk psql, rtk prisma, rtk aws
- **Networking**: rtk curl, rtk wget
