---
name: red-team-operations
description: "Use when planning offensive security methodology, simulating attack phases, analyzing detection evasion, or applying PTES/MITRE ATT&CK principles."
---

# Red Team Operations & Penetration Testing

> "Think like an attacker. Find weaknesses before malicious actors do."
> Adversary simulation principles based on PTES and MITRE ATT&CK frameworks.

## 1. Methodology: PTES Phases

1. **PRE-ENGAGEMENT**: Define scope, rules of engagement, authorization
2. **RECONNAISSANCE**: Passive → Active information gathering
3. **THREAT MODELING**: Identify attack surface and vectors
4. **VULNERABILITY ANALYSIS**: Discover and validate weaknesses
5. **EXPLOITATION**: Demonstrate impact (Proof of Concept only)
6. **POST-EXPLOITATION**: Privilege escalation (Theoretical only)
7. **REPORTING**: Document findings with evidence

## 2. MITRE ATT&CK Phases

### Attack Lifecycle

```
RECONNAISSANCE → INITIAL ACCESS → EXECUTION → PERSISTENCE
       ↓              ↓              ↓            ↓
   PRIVILEGE ESC → DEFENSE EVASION → CRED ACCESS → DISCOVERY
       ↓              ↓              ↓            ↓
LATERAL MOVEMENT → COLLECTION → C2 → EXFILTRATION → IMPACT
```

### Phase Objectives

| Phase | Objective |
|-------|-----------|
| **Recon** | Map attack surface |
| **Initial Access** | Get first foothold |
| **Execution** | Run code on target |
| **Persistence** | Survive reboots |
| **Privilege Escalation** | Get admin/root |
| **Defense Evasion** | Avoid detection |
| **Credential Access** | Harvest credentials |
| **Discovery** | Map internal network |
| **Lateral Movement** | Spread to other systems |
| **Collection** | Gather target data |
| **C2** | Maintain command channel |
| **Exfiltration** | Extract data |

## 3. Attack Surface Categories & Vulnerability Prioritization

### OWASP Top 10 Focus (2025)
- **Broken Access Control**: IDOR, privilege escalation, SSRF
- **Security Misconfiguration**: Cloud configs, headers, defaults
- **Supply Chain Failures**: Deps, CI/CD, lock file integrity
- **Cryptographic Failures**: Weak encryption, exposed secrets
- **Injection**: SQL, command, LDAP, XSS
- **Insecure Design**: Business logic flaws
- **Auth Failures**: Weak passwords, session issues

### Vulnerability Prioritization

**Risk Assessment Formula:**
$$ Risk = Likelihood \times Impact $$

| Severity | Action |
|----------|--------|
| **Critical** | Immediate report, stop testing if data at risk |
| **High** | Report same day |
| **Medium** | Include in final report |
| **Low** | Document for completeness |

## 4. Reconnaissance Principles

### Passive vs Active

| Type | Trade-off |
|------|-----------|
| **Passive** | No target contact, limited info |
| **Active** | Direct contact, more detection risk |

### Information Targets

| Category | Value |
|----------|-------|
| Technology stack | Attack vector selection |
| Employee info | Social engineering |
| Network ranges | Scanning scope |
| Third parties | Supply chain attack |

## 5. Initial Access Vectors

### Selection Criteria

| Vector | When to Use |
|--------|-------------|
| **Phishing** | Human target, email access |
| **Public exploits** | Vulnerable services exposed |
| **Valid credentials** | Leaked or cracked |
| **Supply chain** | Third-party access |

## 6. Privilege Escalation Principles

### Windows Targets

| Check | Opportunity |
|-------|-------------|
| Unquoted service paths | Write to path |
| Weak service permissions | Modify service |
| Token privileges | Abuse SeDebug, etc. |
| Stored credentials | Harvest |

### Linux Targets

| Check | Opportunity |
|-------|-------------|
| SUID binaries | Execute as owner |
| Sudo misconfiguration | Command execution |
| Kernel vulnerabilities | Kernel exploits |
| Cron jobs | Writable scripts |

## 7. Defense Evasion Principles

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
