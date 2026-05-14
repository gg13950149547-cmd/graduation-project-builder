# Agent Run Manifest: Reference, Acknowledgement, And Figure Size Skill Hardening

## Run Fields

- run_id: skill-maintenance-20260512-ref-ack-figure-size
- task_mode: skill-maintenance
- subtask: repair durable skill rules and validation for reference-entry content formatting, acknowledgement title indentation, and paragraph-margin figure sizing
- authorization_source: user explicitly requested multi-agent collaboration in this thread
- agent_mode: reused existing platform subagents plus controller integration
- max_concurrent_live_agents: 6
- live_agent_count_used: 5
- spawn_attempted: no
- sequential_fallback_reason: not-needed; current five agents were available and completed read-only review
- content-worker: not-applicable; no thesis prose edit requested
- program-worker: not-applicable; no software surface requested
- controller_alias_zh: 总控
- citation_worker_alias_zh: 引用
- format_worker_alias_zh: 格式
- figure_worker_alias_zh: 图表
- acceptance_worker_alias_zh: 验收
- audit_worker_alias_zh: 审核
- complete_role_roster: 总控=active; 内容=not-applicable; 格式=active; 图表=active; 引用=active; 程序=not-applicable; 验收=active; 审核=active
- touched_surface_families: references_entries; acknowledgement_title; body figures and screenshots
- canonical_skill_bundle_path: C:\Users\Administrator\.agents\skills\graduation-project-builder
- thesis_docx_mutation: forbidden; no thesis DOCX/PDF changed

## Dispatch Evidence

- 引用: 019e1978-d11e-73d3-89f4-0ec1a5dc9ac1; read-only review found bibliography content-format model evidence was under-bound without `--reference-docx`.
- 格式: 019e1978-dc0b-7ac3-8c63-8436075bc1fd; read-only review found `FMT-EVID-012` lacked owner-map enforcement and `acknowledgement_title` needed numeric indent/position comparison.
- 图表: 019e1978-e52d-7012-9043-82bf0e34551f; read-only review recommended final figure width be checked against DOCX text width with a default ratio gate.
- 验收: 019e1978-ee91-7db2-b93b-79425c9a77e6; read-only review confirmed new rules must propagate to owner-map, acceptance fields, validators, and selftests.
- 审核: 019e1978-f894-7ef1-8cc6-9d6d7d73959f; read-only review identified `FB-CITE-041`, `FB-LAYOUT-071`, `FMT-EVID-012`, and case-record closure as the remaining promotion gaps.
- controller: controller-local; integrated findings, patched canonical skill files, and ran validation.

## Implementation Summary

- reference entries: `FB-CITE-041` added; DOCX font audit and gate now require `bibliography content-format model checks: pass` plus a bound model source when bibliography entries exist.
- acknowledgement title: `FMT-EVID-012` owner-map enforcement added; evidence validator rejects pass-shaped `acknowledgement_title` records with alignment, indent, tab, centerline, left-x, or x-position drift.
- figures: `FB-LAYOUT-071` added; `audit_docx_figure_extents.py` reports `width_text_ratio`, `text_width_cm`, `min_text_width_ratio`, and `paragraph_margin_width_drift_count`, and rejects body figures below paragraph-margin width by default.
- consolidation: `FILE-ROLE-INDEX.md`, `DURABLE-RULE-PROMOTION-AUDIT.md`, rule owner map, routed rule files, and selftests were updated.

## Validation Status

- py_compile changed scripts: pass
- rule-owner-map JSON parse: pass
- targeted selftests: pass for `figure_width_not_paragraph_margin_aligned_rejected`, `reference_entry_content_run_format_rejected`, and `acknowledgement_title_indent_drift_rejected`
- skill gate: pass with `py -3 scripts\validate_skill_gate.py --skill-root .`
- UTF-8 clean: pass with `py -3 scripts\check_utf8_clean.py --root . --json`

## Handoff Boundary

- final_status: skill-only implementation complete; final gate and UTF-8 checks passed
- exact_output_path: not-applicable; no thesis DOCX output in this run
- remaining_risk: full `FB-CITE-*` owner-map modernization remains outside this focused repair and must not be claimed as complete
