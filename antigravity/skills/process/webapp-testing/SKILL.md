---
name: webapp-testing
description: "Use when writing or running web application E2E tests, Playwright scripts, or performing deep audits. Triggers on e2e, playwright, testing."
allowed-tools: Read, Write, Edit, Glob, Grep, Bash
---

# Web App Testing

> Discover and test everything. Leave no route untested.

## 🔧 Runtime Scripts

**Execute these for automated browser testing:**

| Script | Purpose | Usage |
|--------|---------|-------|
<!-- contract:ignore -->
| `scripts/playwright_runner.py` | Basic browser test | `python scripts/playwright_runner.py https://example.com` |
| | With screenshot | `python scripts/playwright_runner.py <url> --screenshot` |
| | Accessibility check | `python scripts/playwright_runner.py <url> --a11y` |
<!-- /contract:ignore -->

**Requires:** `pip install playwright && playwright install chromium`

---

## 1. Deep Audit Approach

### Discovery First

| Target | How to Find |
|--------|-------------|
| Routes | Scan app/, pages/, router files |
| API endpoints | Grep for HTTP methods |
| Components | Find component directories |
| Features | Read documentation |

### Systematic Testing

1. **Map** - List all routes/APIs
2. **Scan** - Verify they respond
3. **Test** - Cover critical paths

---

## 2. Testing Pyramid for Web

```
        /\          E2E (Few)
       /  \         Critical user flows
      /----\
     /      \       Integration (Some)
    /--------\      API, data flow
   /          \
  /------------\    Component (Many)
                    Individual UI pieces
```

---

## 3. E2E Test Principles

### What to Test

| Priority | Tests |
|----------|-------|
| 1 | Happy path user flows |
| 2 | Authentication flows |
| 3 | Critical business actions |
| 4 | Error handling |

### E2E Best Practices

| Practice | Why |
|----------|-----|
| Use data-testid | Stable selectors |
| Wait for elements | Avoid flaky tests |
| Clean state | Independent tests |
| Avoid implementation details | Test user behavior |

---

## 4. Playwright Principles

### Core Concepts

| Concept | Use |
|---------|-----|
| Page Object Model | Encapsulate page logic |
| Fixtures | Reusable test setup |
| Assertions | Built-in auto-wait |
| Trace Viewer | Debug failures |

### Configuration

| Setting | Recommendation |
|---------|----------------|
| Retries | 2 on CI |
| Trace | on-first-retry |
| Screenshots | on-failure |
| Video | retain-on-failure |

---

## 5. Visual Testing

### When to Use

| Scenario | Value |
|----------|-------|
| Design system | High |
| Marketing pages | High |
| Component library | Medium |
| Dynamic content | Lower |

### Strategy

- Baseline screenshots
- Compare on changes
- Review visual diffs
- Update intentional changes

---

## 6. API Testing Principles


## Extended References
For less-frequently-needed detail, see [`references/extended-reference.md`](references/extended-reference.md):
- Coverage Areas
- 7. Test Organization
- File Structure
- Naming Convention
- 8. CI Integration
- Pipeline Steps
- Parallelization
- 9. Anti-Patterns
