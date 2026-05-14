# Active Checklist: Reference, Acknowledgement, And Figure Size Skill Hardening

- mode: skill-maintenance
- source thesis mutation: forbidden in this run
- canonical skill bundle path: C:\Users\Administrator\.agents\skills\graduation-project-builder
- user-reported defects: reference content formatting is wrong; acknowledgement title has abnormal indentation; figures are compressed too much and should align with paragraph margins
- routed references loaded: `SKILL.md`; `references/user-feedback-persistence.md`; `references/agents/agent-lanes.md`; `references/user-feedback/citations-and-bibliography.md`; `references/user-feedback/template-and-layout.md`; `references/user-feedback/thesis-workflow.md`; `references/thesis/figure-rules/geometry-and-layout.md`; `references/thesis/format-rules/protected-surface-evidence-contract.md`
- required agent coverage: 引用, 格式, 图表, 验收, 审核; 内容 and 程序 marked not-applicable
- reference rule outcome: `FB-CITE-041` requires a bound bibliography content-format model source and rejects intrinsic-only pass claims when bibliography entries exist
- acknowledgement rule outcome: `FMT-EVID-012` rejects pass-shaped acknowledgement title evidence with template/actual indentation or position drift
- figure rule outcome: `FB-LAYOUT-071` treats `8.0 cm` and `9.0 cm` as floors only; default body figure width must align with paragraph/text margins
- selftest coverage: `reference_entry_content_run_format_rejected`; `acknowledgement_title_indent_drift_rejected`; `figure_width_not_paragraph_margin_aligned_rejected`
- consolidation files: `references/rule-owner-map.json`; `FILE-ROLE-INDEX.md`; `DURABLE-RULE-PROMOTION-AUDIT.md`; this case record set
- validation commands: py_compile changed scripts; rule-owner JSON parse; targeted selftests; `scripts/validate_skill_gate.py --skill-root .`; `scripts/check_utf8_clean.py --root . --json`
- final handoff condition: no thesis DOCX changed; targeted regressions pass; skill bundle gate passes; UTF-8 check passes; multi-agent record updated
