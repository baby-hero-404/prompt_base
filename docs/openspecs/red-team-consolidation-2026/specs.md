# Specs: Red Team Skill Consolidation

## Added Requirements

### REQ-001: Create `red-team-operations`
> ❌ Status: Not Started

**Scenario:**
- WHEN `red-team-operations/SKILL.md` is read
- THEN it must contain `red-teaming`'s PTES methodology, OWASP-aligned attack surface (dated "2025"), and ethical boundaries checklist
- AND it must contain `red-team-tactics`'s full MITRE ATT&CK phase catalog, AD attack techniques, and the "Web, Cloud & AI Attacks (2026 Landscape)" section added by skill-modernization-2026
- AND section numbering is contiguous with no duplicates (the source `red-team-tactics` file was already fixed to 1-11 contiguous; preserve that ordering logic when merging, don't reintroduce a collision)
- AND `red-team-tactics/` and `red-teaming/` must no longer exist as directories

## Removed Requirements
- REQ-R01: Remove `red-team-tactics`
- REQ-R02: Remove `red-teaming`
