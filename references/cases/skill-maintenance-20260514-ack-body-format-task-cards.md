# Agent Task Cards

## controller
- card_id: skill-maintenance-20260514-ack-body-format-controller
- run_id: skill-maintenance-20260514-ack-body-format
- lane: controller
- role_alias_zh: 总控
- role_applicability: active
- attendance_status: active
- owner: current Codex controller
- system_agent_id: controller
- authorization_source: user requested multi-agent review
- agent_mode: parallel-subagents plus controller integration
- objective: integrate read-only agent findings into a canonical skill patch
- inputs: SKILL.md; user-feedback rules; protected-surface contract; validator scripts; selftests
- outputs: patched skill bundle and validation summary
- spawn_status: not-requested
- fallback_mode: controller-direct
- audit_required: yes
- audit_agent_id: `019e2365-d67a-7221-bb51-3cc5b05e2627`
- action_audit_scope: all action cycles
- mutation_audit_scope: skill bundle changes only
- status: active

## content-worker
- card_id: skill-maintenance-20260514-ack-body-format-content
- run_id: skill-maintenance-20260514-ack-body-format
- lane: content-worker
- role_alias_zh: 内容
- role_applicability: not-applicable
- attendance_status: not-applicable
- not_applicable_reason: no thesis prose is being rewritten
- system_agent_id: none
- spawn_status: not-requested
- fallback_mode: not-applicable
- audit_required: yes
- status: not-applicable

## format-worker
- card_id: skill-maintenance-20260514-ack-body-format-format
- run_id: skill-maintenance-20260514-ack-body-format
- lane: format-worker
- role_alias_zh: 格式
- role_applicability: active
- attendance_status: active
- owner: read-only format review agent plus controller patch
- system_agent_id: `019e2362-aaef-7b62-a1fe-2fa69a2b67bf`
- spawn_status: spawned
- spawn_agent_id: `019e2362-aaef-7b62-a1fe-2fa69a2b67bf`
- objective: identify why acknowledgement protected-surface formatting drift passed
- inputs: protected-surface contract; sample_self_check; body style audit; gate validators
- outputs: read-only finding that acknowledgement_body skips or lacks hard run/paragraph drift closure
- evidence_required: validator/selftest after patch
- evidence_paths: targeted selftests; validate_skill_gate.py bundle gate; fast/fast-core selftest summaries
- audit_required: yes
- status: completed-read-only-review

## figure-worker
- card_id: skill-maintenance-20260514-ack-body-format-figure
- run_id: skill-maintenance-20260514-ack-body-format
- lane: figure-worker
- role_alias_zh: 图表
- role_applicability: not-applicable
- attendance_status: not-applicable
- not_applicable_reason: no figures, tables, or media are touched
- system_agent_id: none
- spawn_status: not-requested
- fallback_mode: not-applicable
- audit_required: yes
- status: not-applicable

## citation-worker
- card_id: skill-maintenance-20260514-ack-body-format-citation
- run_id: skill-maintenance-20260514-ack-body-format
- lane: citation-worker
- role_alias_zh: 引用
- role_applicability: not-applicable
- attendance_status: not-applicable
- not_applicable_reason: no bibliography or citation marker logic is touched in this pass
- system_agent_id: none
- spawn_status: not-requested
- fallback_mode: not-applicable
- audit_required: yes
- status: not-applicable

## program-worker
- card_id: skill-maintenance-20260514-ack-body-format-program
- run_id: skill-maintenance-20260514-ack-body-format
- lane: program-worker
- role_alias_zh: 程序
- role_applicability: active
- attendance_status: active
- owner: controller
- system_agent_id: controller
- spawn_status: sequential-fallback
- objective: patch Python validators and tests in the canonical skill bundle
- inputs: validator scripts and selftest suite
- outputs: changed script files
- audit_required: yes
- status: completed

## acceptance-worker
- card_id: skill-maintenance-20260514-ack-body-format-acceptance
- run_id: skill-maintenance-20260514-ack-body-format
- lane: acceptance-worker
- role_alias_zh: 验收
- role_applicability: active
- attendance_status: active
- owner: read-only acceptance review agent plus controller validation
- system_agent_id: `019e2365-d67a-7221-bb51-3cc5b05e2627`
- spawn_status: spawned
- spawn_agent_id: `019e2365-d67a-7221-bb51-3cc5b05e2627`
- objective: identify validator/selftest fields needed for acknowledgement_body drift rejection
- inputs: validate_skill_gate_record_evidence; generate_thesis_acceptance_record; selftest_skill_flow
- outputs: read-only finding that acknowledgement_body needs paragraph/typography hard-field validator and negative tests
- evidence_required: targeted selftests and skill gate
- evidence_paths: targeted selftests; validate_skill_gate.py bundle gate; fast/fast-core selftest summaries
- audit_required: yes
- status: completed-read-only-review

## audit
- card_id: skill-maintenance-20260514-ack-body-format-audit
- run_id: skill-maintenance-20260514-ack-body-format
- lane: audit
- role_alias_zh: 审核
- role_applicability: active
- attendance_status: active
- owner: spawned review plus controller final audit
- system_agent_id: `019e2365-d67a-7221-bb51-3cc5b05e2627`; controller-final-validation
- spawn_status: spawned-readonly-plus-sequential-final
- objective: verify the patch has a durable rule owner, validator coverage, selftest coverage, and validation evidence
- inputs: changed files and validation outputs
- outputs: final audit verdict in manifest/checklist
- audit_required: yes
- status: completed
