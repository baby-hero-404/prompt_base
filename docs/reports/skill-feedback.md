# Skill Feedback & Journal

This document tracks skill evaluation outcomes and serves as a journal for quality gate interventions.

## Rollback Procedure
If a skill modification causes performance degradation (WORSE score on golden eval) or breaks orchestrator routing:
1. `git log -p antigravity/skills/<skill_name>/SKILL.md` to review the breaking change.
2. `git checkout HEAD^ -- antigravity/skills/<skill_name>/SKILL.md` to revert the file.
3. Run `make registry` to sync the changes.
4. Run `make skill-check SKILL=<skill_name>` to ensure passing state.
5. Log the incident in the Feedback Journal below.

## Feedback Journal

| Date | Skill | Change Summary | Eval Status | Notes / Lessons |
|---|---|---|---|---|
| YYYY-MM-DD | skill-name | Brief description | SAME/BETTER/WORSE | Any insights from the judge or manual review |
