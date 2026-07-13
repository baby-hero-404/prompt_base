# Specs: Testing Skill Routing Clarification

## Added Requirements

### REQ-001: Determine whether real routing conflict exists
> ❌ Status: Not Started

**Scenario:**
- WHEN `tdd-workflow`'s and `testing-patterns`'s YAML `description` fields are compared side by side
- THEN the specific overlapping trigger keywords (if any) must be listed explicitly
- AND any concrete instance of an agent, workflow, or session transcript showing ambiguous routing between the two must be cited, or the absence of such evidence must be explicitly noted

## Modified Requirements

### REQ-M01: Disambiguate `testing-patterns`'s description (conditional on REQ-001)
> ❌ Status: Not Started — blocked on REQ-001

**Scenario:**
- WHEN REQ-001 finds real, evidenced overlap
- THEN `testing-patterns`'s YAML `description` is narrowed to clarify it as a pattern/reference library, distinct from `tdd-workflow`'s process-discipline scope
- AND neither skill's body content or file structure changes — this is a description-only edit
- WHEN REQ-001 finds no real overlap (only theoretical keyword co-occurrence)
- THEN no change is made, and this proposal closes as "investigated, no action needed"

## Removed Requirements
- None
