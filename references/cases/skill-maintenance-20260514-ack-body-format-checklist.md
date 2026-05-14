# Skill Maintenance Checklist: Acknowledgement Body Format Gate

- [x] Classify mode as `skill-maintenance`, not thesis repair.
- [x] Record that prior lock-before-action violation is contaminated/reference-only drift.
- [x] Load skill router, user-feedback router, maintenance rules, final-QA rules, agent-lane rules, and protected-surface contract.
- [x] Externalize invocation lock, checklist, run manifest, and task cards before skill mutation.
- [x] Include multi-agent read-only review evidence in the manifest.
- [x] Inspect existing acknowledgement/references protected-surface validators and selftests.
- [x] Patch validator so `acknowledgement_body` rejects title contamination, typography drift, and paragraph-dialog drift.
- [x] Patch generated acceptance evidence fields if needed so acknowledgement body hard fields are named distinctly.
- [x] Add selftests for acknowledgement body title contamination and paragraph/typography drift.
- [x] Update rule owner map and maintenance case record so the durable rule has owner, validator, selftest, and acceptance fields.
- [x] Run targeted selftests and syntax checks.
- [x] Run skill bundle gate or record exact blocker.
- [x] Update final lock/manifest verdicts after validation.

## Validation Summary

- `python -m py_compile scripts\validate_skill_gate_registry_core.py scripts\validate_skill_gate_record_gate.py scripts\selftest_skill_flow.py` passed.
- `python -m py_compile scripts\validate_skill_gate_record_evidence.py scripts\validate_skill_gate_record_gate.py scripts\generate_thesis_acceptance_record.py scripts\selftest_skill_flow.py` passed earlier in the same run.
- `python -c "import json; json.load(open(r'references\rule-owner-map.json', encoding='utf-8'))"` passed.
- `python scripts\check_utf8_clean.py --root . --json` passed with 219 checked files and 0 issues.
- `python scripts\validate_skill_gate.py --skill-root .` passed.
- `python scripts\selftest_skill_flow.py --case acknowledgement_body_title_contamination_drift_rejected --case protected_acknowledgement_body_paragraph_typography_drift_rejected --quiet --fail-fast` passed.
- `python scripts\selftest_skill_flow.py --case program_only_valid --quiet --fail-fast` passed.
- `python scripts\selftest_skill_flow.py --case review_copy_exact_output_promotion_binding_valid --quiet --fail-fast` passed.
- `python scripts\selftest_skill_flow.py --suite fast-core --quiet --fail-fast` passed with 38 cases.
- `python scripts\selftest_skill_flow.py --suite fast --quiet --fail-fast` passed with 196 cases.

## Guardrail

This pass changes only the canonical skill bundle. It does not edit the scallop thesis manuscript or any DOCX/PDF deliverable.
