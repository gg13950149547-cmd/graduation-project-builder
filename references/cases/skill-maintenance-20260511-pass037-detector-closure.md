# Skill Maintenance Case: pass037 Detector Closure

- date: 2026-05-11
- mode: skill-maintenance
- scope: documentation and rule-index maintenance only
- write boundary: `references/rule-owner-map.json`; `FILE-ROLE-INDEX.md`; `DURABLE-RULE-PROMOTION-AUDIT.md`; `references/user-feedback/maintenance-and-structure.md`; this case record
- script mutation: none
- thesis DOCX mutation: none

## Maintenance Reason

Pass037 closes the durable rule chain for three sample-self-check detector ids:

- `heading.baseline-contract`
- `toc.visible-format-contract`
- `figure.family-style-contract`

The required shape is:

- `scripts/sample_self_check.py` emits each id in the `Detector Registry` with an evidence object.
- `scripts/validate_skill_gate_record_gate.py` requires each id through `REQUIRED_SAMPLE_SELF_CHECK_DETECTORS`.
- `references/rule-owner-map.json` exposes the owner, validator, selftest, required load modes, and acceptance fields.
- `references/user-feedback/maintenance-and-structure.md` owns the durable prose rule as `EXEC-MAINT-069`.

## Multi-Agent And Source Boundary

- multi-agent authorization: yes, current user explicitly authorized multi agent maintenance
- agent role for this lane: documentation/rule-index maintainer only
- clean-source rationale: no thesis DOCX is touched; this pass only records the canonical skill-bundle rule closure
- canonical-helper-only rationale: no project-local helper, generated thesis builder, or workspace-local DOCX mutation script is created or modified
- duplicate-rule avoidance: this pass extends the existing sample-self-check detector chain under `EXEC-MAINT-068` instead of creating separate TOC, heading, or figure rule fragments

## Validation Plan

- Parse `references/rule-owner-map.json`.
- Run `scripts/check_utf8_clean.py --root . --json`.
- Run `scripts/validate_skill_gate.py --skill-root .`.
- Optional implementation-lane validation: targeted selftests for heading baseline, TOC visible format, figure family style, and sample-self-check stale/missing report rejection.
