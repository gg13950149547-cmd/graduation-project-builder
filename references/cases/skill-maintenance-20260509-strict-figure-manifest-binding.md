# Skill Maintenance Run 2026-05-09: Strict Figure Manifest Binding

## Run Manifest
- run_id: skill-maintenance-20260509-strict-figure-manifest-binding
- task_mode: skill-maintenance
- subtask: enforce fail-closed source/final DOCX binding, all-package image relationship scanning, and final-side replacement authorization for thesis figure manifests
- authorization_source: user explicitly requested multi-agent implementation in this session
- agent_mode: parallel-subagents plus controller implementation
- max_concurrent_live_agents: 4 observed live review workers plus controller; below cap 6
- live_agent_count_plan: reuse existing acceptance/figure review agents where available; spawn two read-only review agents for code and records; controller performs final merge
- dispatch_wave_plan: wave1 read-only review; wave2 controller implementation and targeted validation; wave3 sequential final audit update
- audit_presence_by_wave: read-only review agents plus controller sequential final audit
- concurrency_limit_verdict: pass
- required_lanes: controller; content-worker; format-worker; figure-worker; citation-worker; program-worker; acceptance-worker; audit
- complete_role_roster: controller=总控; content-worker=内容; format-worker=格式; figure-worker=图表; citation-worker=引用; program-worker=程序; acceptance-worker=验收; audit=审核
- role_attendance_matrix: controller active; figure-worker active; acceptance-worker active; audit active; content-worker not-applicable; format-worker not-applicable; citation-worker not-applicable; program-worker not-applicable
- not_applicable_lanes_with_reasons: content-worker=no thesis prose edit; format-worker=no target thesis DOCX mutation; citation-worker=no citation/bibliography mutation; program-worker=no project runtime mutation
- spawned_agent_ids: 019e0a66-685f-7da2-bb9c-c6ba7cc7a193; 019e0a66-790f-79b3-be29-436ffea1d912; 019e0a6e-bec7-71a2-b328-fcc4a0ebff6a; 019e0a6e-e996-7fc3-a73f-88e774f282f3
- spawned_agent_aliases_zh: 019e0a66-685f-7da2-bb9c-c6ba7cc7a193=验收; 019e0a66-790f-79b3-be29-436ffea1d912=图表; 019e0a6e-bec7-71a2-b328-fcc4a0ebff6a=审核-code; 019e0a6e-e996-7fc3-a73f-88e774f282f3=审核-records
- audit_agent_id: controller-final-audit
- sequential_audit_fallback_id: controller-final-audit
- audit_spawn_or_fallback_mode: spawned read-only review plus sequential final audit
- action_audit_scope: inspect figure contract, transaction validator, acceptance generator, final gate validator, selftests, owner map, file-role index, durable audit, and this case record
- action_audit_verdict_cadence: before mutation, after script mutation, after record mutation, after validation
- mutation_audit_scope: scripts/thesis_figure_contract.py; scripts/validate_thesis_mutation_transaction.py; scripts/generate_thesis_acceptance_record.py; scripts/validate_skill_gate_record_gate.py; scripts/selftest_skill_flow.py; references/rule-owner-map.json; FILE-ROLE-INDEX.md; DURABLE-RULE-PROMOTION-AUDIT.md; this case record
- handoff_status: targeted strict figure-manifest binding hardening passed selected validation; full fast-thesis-records single-command run timed out and was split to targeted coverage

## Active Checklist
- final DOCX figure manifest validation fails closed when source/final path or SHA binding is missing or mismatched: passed
- DOCX image relationship scanning covers all Word package relationship parts, not only main document relationships: passed
- authorized replacement entries bind both original and final media relationship identity and SHA256: passed
- source media removal is rejected when final media is missing: passed
- final-only media relationships are rejected unless represented by an explicit authorized final binding: passed
- acceptance record generation passes source DOCX into the canonical figure contract: passed
- owner map and maintenance records name the new selftest coverage before handoff: passed

## Task Cards
- lane: controller; role_alias_zh: 总控; attendance_status: active; system_agent_id: main-thread; objective: implement strict figure manifest hardening and merge reviewer findings; evidence_required: diffs and validation commands
- lane: content-worker; role_alias_zh: 内容; attendance_status: not-applicable; system_agent_id: none; not_applicable_reason: no thesis prose mutation
- lane: format-worker; role_alias_zh: 格式; attendance_status: not-applicable; system_agent_id: none; not_applicable_reason: no target thesis DOCX formatting mutation
- lane: figure-worker; role_alias_zh: 图表; attendance_status: active; system_agent_id: 019e0a66-790f-79b3-be29-436ffea1d912; objective: review figure manifest fixture and selftest strategy; evidence_required: subagent findings
- lane: citation-worker; role_alias_zh: 引用; attendance_status: not-applicable; system_agent_id: none; not_applicable_reason: no citation or bibliography mutation
- lane: program-worker; role_alias_zh: 程序; attendance_status: not-applicable; system_agent_id: none; not_applicable_reason: no project runtime mutation
- lane: acceptance-worker; role_alias_zh: 验收; attendance_status: active; system_agent_id: 019e0a66-685f-7da2-bb9c-c6ba7cc7a193; objective: review acceptance generator source-docx propagation; evidence_required: subagent findings
- lane: audit; role_alias_zh: 审核; attendance_status: active; system_agent_id: controller-final-audit; objective: verify modified files, validation output, and no thesis DOCX mutation; evidence_required: final validation summary

## Implemented Changes
- `scripts/thesis_figure_contract.py`: added manifest-relative path normalization, strict top-level source/final DOCX path and SHA256 binding, full `word/**/_rels/*.rels` image relationship scanning, original/final media rid/target/SHA authorization checks, duplicate identity owner-part ambiguity checks, source media removal rejection, and final-only media addition rejection unless authorized as a replacement final binding.
- `scripts/validate_thesis_mutation_transaction.py`: passes transaction source/final DOCX and manifest path into `validate_figure_manifest`.
- `scripts/generate_thesis_acceptance_record.py`: passes `--source-docx` into `summarize_figure_contract` so acceptance-side figure validation compares source-to-final media.
- `scripts/validate_skill_gate_record_gate.py`: passes manifest path plus source DOCX derived from source review-artifact inventory into final gate figure manifest validation.
- `scripts/selftest_skill_flow.py`: added and registered strict figure manifest binding, header/footer media replacement, source media removal, transaction source SHA mismatch, and acceptance-generator source-docx propagation regressions.
- `references/rule-owner-map.json`, `FILE-ROLE-INDEX.md`, and `DURABLE-RULE-PROMOTION-AUDIT.md`: updated owner coverage and maintenance evidence for the new strict behavior.

## Validation Evidence
- `py -3 -m py_compile scripts/thesis_figure_contract.py scripts/validate_thesis_mutation_transaction.py scripts/generate_thesis_acceptance_record.py scripts/validate_skill_gate_record_gate.py scripts/selftest_skill_flow.py`: PASS.
- `py -3 scripts/selftest_skill_flow.py --quiet --case figure_manifest_missing_source_docx_for_final_media_rejected --case figure_manifest_final_docx_binding_sha_mismatch_rejected --case figure_manifest_authorized_final_media_hash_mismatch_rejected --case figure_manifest_header_footer_media_replacement_rejected --case figure_manifest_source_media_removed_rejected --case transaction_image_manifest_source_sha_mismatch_rejected`: PASS.
- `py -3 scripts/selftest_skill_flow.py --quiet --case acceptance_generator_passes_source_docx_to_figure_contract`: PASS.
- `py -3 scripts/selftest_skill_flow.py --quiet --case figure_manifest_source_final_media_hash_replacement_rejected --case transaction_image_manifest_invalid_but_pass_rejected --case transaction_image_manifest_final_docx_binding_missing_rejected --case gate_transaction_figure_manifest_path_mismatch_rejected --case transaction_valid_local_toc_pass --case figure_manifest_docx_toc_insertion_rejected`: PASS.
- `py -3 scripts/selftest_skill_flow.py --suite fast-thesis-records --quiet`: TIMEOUT at 360s single-command limit; targeted strict and related cases above passed.

## Remaining Risks
- Full `fast-thesis-records` completion remains unproven in one command for this run due to timeout; targeted cases covering the changed behavior passed.
- `sample_self_check.py` and `build_canonical_thesis.py` still have final-DOCX oriented figure validation paths that may require follow-up source-docx plumbing for full end-to-end generated-thesis flows; final acceptance and transaction gates now carry stricter source/final checks.
