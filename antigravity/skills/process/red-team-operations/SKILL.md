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


## Extended References
For less-frequently-needed detail, see [`references/extended-reference.md`](references/extended-reference.md):
- Key Techniques
- Operational Security
- 8. Lateral Movement Principles
- Credential Types
- Movement Paths
- 9. Active Directory Attacks
- Attack Categories
- 10. Web, Cloud & AI Attacks (2026 Landscape)
- Web & Cloud (OWASP-Aligned)
- AI/LLM Attacks
- 11. Reporting Principles
- Attack Narrative
- Detection Gaps
- 12. Ethical Boundaries (MANDATORY)
- 13. Anti-Patterns
