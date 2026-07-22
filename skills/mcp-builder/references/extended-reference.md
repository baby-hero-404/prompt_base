### Input Validation

- Validate all tool inputs
- Sanitize user-provided data
- Limit resource access

### API Keys

- Use environment variables
- Don't log secrets
- Validate permissions

---

## 8. Configuration

### Authentication (2025 Revision)

The modern MCP specification standardizes on **OAuth 2.1** for remote server authentication.
- Implement standard OAuth 2.1 Authorization Code flow for external user auth.
- Use Bearer tokens for subsequent Streamable HTTP/WebSocket requests.
- Claude Desktop Config auth is largely meant for *local* testing or basic static tokens, not for production remote setups.

### Claude Desktop Config (Local/Basic)

| Field | Purpose |
|-------|---------|
| command | Executable to run |
| args | Command arguments |
| env | Environment variables (e.g., static API keys) |

---

## 9. Testing

### Test Categories

| Type | Focus |
|------|-------|
| Unit | Tool logic |
| Integration | Full server |
| Contract | Schema validation |

---

## 10. Best Practices Checklist

- [ ] Clear, action-oriented tool names
- [ ] Complete input schemas with descriptions
- [ ] Structured JSON output
- [ ] Error handling for all cases
- [ ] Input validation
- [ ] Environment-based configuration
- [ ] Logging for debugging

---

> **Remember:** MCP tools should be simple, focused, and well-documented. The AI relies on descriptions to use them correctly.
