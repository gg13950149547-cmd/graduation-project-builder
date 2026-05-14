# Thesis Lane Freeze

- status: CLEARED
- incident id: 2026-04-19-thesis-lane-instability
- owner: graduation-project-builder skill audit
- scope:
  - `thesis-only`
  - `format-repair-only`
  - thesis phase of `program-plus-thesis`

## Reason

Repeated thesis runs have shown cross-session instability that is stronger than ordinary one-off formatting drift.

Observed failure families include:
- visible title text partially missing or clipped on rendered pages
- Chinese / English abstract title or keyword styling drifting after later passes
- front-matter roman-number chain and body arabic-number chain drifting after refresh or export
- references / acknowledgement title blocks colliding with the header zone or creating blank-page side effects

## Enforcement

While this file remains `ACTIVE`:
- do not let this skill mutate thesis DOCX, thesis PDF, TOC fields, page numbering, headers/footers, or thesis helper scripts
- do not run thesis fix-up automation against a live manuscript path
- do not promote durable corrections into `references/`, `assets/`, `memory.md`, validators, or scripts unless the current task is the skill-audit task itself
- allowed work is limited to:
  - audit
  - rule conflict review
  - validator / selftest / integration-gate work
  - incident documentation
  - skill-internal hardening

## Exit Criteria

The freeze may be cleared only after all of the following are true:
- the conflict matrix has been updated and reviewed
- `scripts/validate_skill_gate.py` still passes on the active bundle
- `scripts/selftest_skill_flow.py` passes on the active bundle
- `scripts/run_integration_gate.py` passes the real DOCX integration cases
- the regression fixtures for the 2026-04-19 thesis incident are documented and mapped to concrete gate coverage

## Clearance Record

- cleared on: 2026-04-19
- clearance basis:
  - `scripts/validate_skill_gate.py` passed
  - `scripts/selftest_skill_flow.py --include-integration` passed
  - `scripts/run_integration_gate.py` passed all real DOCX integration cases
