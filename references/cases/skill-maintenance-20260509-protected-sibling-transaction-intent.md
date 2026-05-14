# Skill Maintenance Run 2026-05-09: Protected Sibling Transaction Intent

## Run Manifest

- run_id: skill-maintenance-20260509-protected-sibling-transaction-intent
- task_mode: skill-maintenance
- subtask: prevent protected sibling freeze lists from falsely triggering image mutation and whole-thesis claim gates
- scope: only `C:\Users\Administrator\.agents\skills\graduation-project-builder` and project-local intermediate records under `_analysis\run-20260509-clean-restart`; no original thesis DOCX overwrite
- authorization_source: user stated this session defaults to multi-agent authorization
- agent_mode: reused existing read-only subagents for selftest placement and clean-restart record audit; controller implemented script/rule changes
- required_lanes: controller; content-worker; format-worker; figure-worker; citation-worker; program-worker; acceptance-worker; audit
- active_lanes: controller; format-worker; figure-worker; acceptance-worker; audit
- skipped_lanes_with_reason: content-worker=no prose mutation in skill maintenance; citation-worker=no bibliography mutation; program-worker=no runtime project mutation
- audit_verdict: pass for targeted skill gate behavior; project thesis remains not final

## Change Summary

- `scripts/validate_thesis_mutation_transaction.py` now separates protected sibling freeze scope from actual mutation-intent text.
- `protected_sibling_surfaces` can list `figure_table_captions_and_holders` without requiring a figure manifest when source/final media relationships and drawing objects are unchanged.
- Negative guardrail text such as `no whole-thesis pass claim` and `do not rewrite figures/media/drawings` is no longer treated as a positive whole-thesis or image mutation claim.
- Real image operations and real source-to-final media/drawing diffs still route through the strict figure-manifest gate.
- `scripts/validate_thesis_mutation_transaction.py` gained `--json-output` for persistent UTF-8 validation reports without relying on shell redirection.
- `scripts/audit_docx_review_artifacts.py` gained `--json-output` for persistent UTF-8 JSON reports without relying on shell redirection.
- `scripts/repair_thesis_surface_format.py` and `scripts/audit_docx_review_artifacts.py` now reconfigure stdout/stderr to UTF-8 before CLI output to reduce Windows redirection encoding drift.

## Validation

- `py -3 -m py_compile scripts/validate_thesis_mutation_transaction.py scripts/selftest_skill_flow.py scripts/repair_thesis_surface_format.py scripts/audit_docx_review_artifacts.py`: PASS
- `py -3 scripts/selftest_skill_flow.py --case transaction_protected_sibling_figure_surface_no_manifest_when_unchanged --case transaction_chinese_image_mutation_requires_manifest --case transaction_media_diff_without_image_words_requires_manifest --case transaction_toc_image_target_rejected --quiet`: PASS
- `py -3 -m json.tool references/rule-owner-map.json`: PASS before record update; rerun required after final consolidation

## Remaining Risks

- Full `fast-thesis-records` is long and was not rerun as a single command in this continuation.
- The current project clean-restart DOCX is only a keyword-line local repair artifact unless its transaction and rendered evidence pass; it is not a final thesis handoff.
