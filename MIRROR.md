# Mirror Skill Copy

This directory is a mirror copy of the canonical `graduation-project-builder` skill.

## Canonical Source

- `C:\Users\Administrator\.agents\skills\graduation-project-builder`

Do not treat this directory as the source of truth. Sync from the canonical copy when changes are made.

Before using a mirrored copy in a project:

- run `scripts/selftest_skill_flow.py` on that exact mirror
- run `scripts/validate_skill_gate.cmd` or `scripts/validate_skill_gate.py` on that exact mirror
- if either check fails or required assets / references / scripts are missing, the mirror is invalid and must be resynced before execution
