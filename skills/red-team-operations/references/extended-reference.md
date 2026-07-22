### Key Techniques

| Technique | Purpose |
|-----------|---------|
| LOLBins | Use legitimate tools |
| Obfuscation | Hide malicious code |
| Timestomping | Hide file modifications |
| Log clearing | Remove evidence |

### Operational Security

- Work during business hours
- Mimic legitimate traffic patterns
- Use encrypted channels
- Blend with normal behavior

## 8. Lateral Movement Principles

### Credential Types

| Type | Use |
|------|-----|
| Password | Standard auth |
| Hash | Pass-the-hash |
| Ticket | Pass-the-ticket |
| Certificate | Certificate auth |

### Movement Paths

- Admin shares
- Remote services (RDP, SSH, WinRM)
- Exploitation of internal services

## 9. Active Directory Attacks

### Attack Categories

| Attack | Target |
|--------|--------|
| Kerberoasting | Service account passwords |
| AS-REP Roasting | Accounts without pre-auth |
| DCSync | Domain credentials |
| Golden Ticket | Persistent domain access |

## 10. Web, Cloud & AI Attacks (2026 Landscape)

### Web & Cloud (OWASP-Aligned)

| Attack | Target |
|--------|--------|
| **SSRF to IMDS** | Cloud metadata (AWS/GCP/Azure) |
| **JWT Confusion/None** | Authentication bypass |
| **Container Escape** | Kubernetes/Docker host access |
| **Insecure Direct Object Reference (IDOR)** | Tenant data isolation bypass |

### AI/LLM Attacks

| Attack | Target |
|--------|--------|
| **Prompt Injection** | Bypassing LLM guardrails |
| **Data Poisoning** | Corrupting RAG retrieval sources |
| **Model Exfiltration** | Extracting model weights or system prompts |
| **Indirect Injection** | Malicious payload in scraped webpage |

## 11. Reporting Principles

**Structure:**
1. **Executive Summary**: Business impact, risk level
2. **Findings**: Vulnerability, evidence, impact
3. **Remediation**: How to fix, priority
4. **Technical Details**: Steps to reproduce

**Evidence:**
- Screenshots with timestamps
- Request/response logs
- Sanitized sensitive data

### Attack Narrative

Document the full attack chain:
1. How initial access was gained
2. What techniques were used
3. What objectives were achieved
4. Where detection failed

### Detection Gaps

For each successful technique:
- What should have detected it?
- Why didn't detection work?
- How to improve detection

## 12. Ethical Boundaries (MANDATORY)

- [ ] Written authorization before testing
- [ ] Stay within defined scope
- [ ] Report critical issues immediately
- [ ] Protect discovered data
- [ ] Document all actions
- [ ] **NEVER** Denial of Service (DoS) (unless scoped)
- [ ] **NEVER** Social Engineering without explicit scope
- [ ] **NEVER** Destroy production data
- [ ] **NEVER** Access beyond proof of concept
- [ ] **NEVER** Retain sensitive data

## 13. Anti-Patterns

| ❌ Don't | ✅ Do |
|----------|-------|
| Rush to exploitation | Follow methodology |
| Cause damage | Minimize impact |
| Skip reporting | Document everything |
| Ignore scope | Stay within boundaries |

> **Remember:** Red team simulates attackers to improve defenses, not to cause harm.
