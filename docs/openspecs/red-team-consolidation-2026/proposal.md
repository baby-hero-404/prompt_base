# Proposal: Red Team Skill Consolidation

## Why
`red-team-tactics` (technique catalog: MITRE ATT&CK phases, AD attacks, and — as of the recent skill-modernization pass — a "Web, Cloud & AI Attacks" section) and `red-teaming` (PTES methodology, OWASP-aligned attack surface, ethical boundaries checklist) are genuinely complementary rather than duplicative: one is "how do I execute a specific technique," the other is "how do I structure and scope an engagement." Unlike the UI/UX and verification cases, this is the best-justified consolidation of the original bundled proposal — the boundary between the two is largely artificial from an LLM-routing perspective, since a real engagement needs both simultaneously.

**Important dependency:** both source skills were recently updated by the skill-modernization-2026 effort — `red-team-tactics` gained a "## 8. Web, Cloud & AI Attacks (2026 Landscape)" section (OWASP-aligned web/cloud attacks + AI/LLM attack techniques), and `red-teaming` had its OWASP Top 10 reference explicitly dated to "(2025)". Both additions must carry over into the merged skill — this proposal is not operating on the pre-modernization content.

## What Changes
- Merge `red-team-tactics` and `red-teaming` into a single new skill, `red-team-operations`, combining methodology (PTES phases, ethical boundaries, OWASP-aligned attack surface) with tactics (MITRE ATT&CK technique catalog, AD attacks, the recently-added Web/Cloud/AI attacks section).
- Update `security-auditor` (the only agent referencing either skill) to use the new combined skill name.

## Capabilities

### New Capabilities
- `red-team-operations`: unified methodology + tactics skill.

### Removed Capabilities
- Standalone access to `red-team-tactics` and `red-teaming`.

## Impact

| Area | Files Affected |
|------|----------------|
| Skill (created) | `antigravity/skills/process/red-team-operations/SKILL.md` |
| Skill (removed) | `antigravity/skills/process/red-team-tactics/` |
| Skill (removed) | `antigravity/skills/process/red-teaming/` |
| Agent frontmatter | `antigravity/agents/security-auditor.md` (`skills:` list references both `red-team-tactics` and `red-teaming`) |
| Registry | `registry.min.json` (regenerated) |
