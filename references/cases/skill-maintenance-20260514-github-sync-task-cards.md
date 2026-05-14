# Agent Task Cards

## Controller
- card_id: skill-maintenance-20260514-github-sync-controller
- run_id: skill-maintenance-20260514-github-sync
- lane: controller
- role_alias_zh: 总控
- role_applicability: active
- attendance_status: active
- lane_alias_zh: 总控
- owner: local controller
- owner_alias_zh: 总控
- system_agent_id: local-controller
- authorization_source: no explicit subagent authorization
- agent_mode: single-agent-no-auth
- run_manifest_path: references/cases/skill-maintenance-20260514-github-sync-manifest.md
- objective: sync the canonical skill bundle to GitHub without touching thesis/project deliverables
- inputs: user request; SKILL.md; user-feedback-persistence.md; maintenance-and-structure.md; agent-lanes.md
- outputs: GitHub remote/commit/push evidence and final handoff
- dependencies: Git/GitHub authentication availability
- spawn_requested: no
- spawn_status: not-requested
- fallback_mode: single-agent-no-auth
- status: active
- sequential_audit_fallback_id: controller-local-audit
- audit_agent_alias_zh: 审核
- audit_required: yes
- audit_spawn_or_fallback_mode: sequential-audit-fallback
- action_audit_scope: all action cycles
- action_audit_verdict_cadence: per cycle
- action_audit_verdicts: bootstrap pass; git inspection pending; git mutation pending; validation pending
- mutation_audit_scope: control artifacts and git synchronization changes
- mutation_audit_verdicts: pending final review
- skill_invocation_verified: yes
- routed_references_verified: yes
- active_checklist_verified: yes
- user_request_compliance_verdict: pending
- loaded_rule_compliance_verdict: pending
- evidence_required: git status, remote target, commit hash, push result, validation output
- evidence_paths: pending
- blockers: pending GitHub remote/auth verification

## Content Worker
- lane: content-worker
- role_alias_zh: 内容
- role_applicability: not-applicable
- attendance_status: not-applicable
- not_applicable_reason: no thesis/content drafting surface in GitHub sync request
- agent_mode: single-agent-no-auth
- spawn_status: not-requested
- fallback_mode: not-applicable
- audit_agent_alias_zh: 审核

## Format Worker
- lane: format-worker
- role_alias_zh: 格式
- role_applicability: not-applicable
- attendance_status: not-applicable
- not_applicable_reason: no DOCX formatting surface in GitHub sync request
- agent_mode: single-agent-no-auth
- spawn_status: not-requested
- fallback_mode: not-applicable
- audit_agent_alias_zh: 审核

## Figure Worker
- lane: figure-worker
- role_alias_zh: 图表
- role_applicability: not-applicable
- attendance_status: not-applicable
- not_applicable_reason: no figure/table asset work in GitHub sync request
- agent_mode: single-agent-no-auth
- spawn_status: not-requested
- fallback_mode: not-applicable
- audit_agent_alias_zh: 审核

## Citation Worker
- lane: citation-worker
- role_alias_zh: 引用
- role_applicability: not-applicable
- attendance_status: not-applicable
- not_applicable_reason: no citation/reference work in GitHub sync request
- agent_mode: single-agent-no-auth
- spawn_status: not-requested
- fallback_mode: not-applicable
- audit_agent_alias_zh: 审核

## Program Worker
- lane: program-worker
- role_alias_zh: 程序
- role_applicability: not-applicable
- attendance_status: not-applicable
- not_applicable_reason: no graduation-project runtime/program delivery surface in GitHub sync request
- agent_mode: single-agent-no-auth
- spawn_status: not-requested
- fallback_mode: not-applicable
- audit_agent_alias_zh: 审核

## Acceptance Worker
- lane: acceptance-worker
- role_alias_zh: 验收
- role_applicability: not-applicable
- attendance_status: not-applicable
- not_applicable_reason: no thesis/program acceptance package is being delivered; final evidence is git sync and skill validation
- agent_mode: single-agent-no-auth
- spawn_status: not-requested
- fallback_mode: not-applicable
- audit_agent_alias_zh: 审核

## Audit
- card_id: skill-maintenance-20260514-github-sync-audit
- run_id: skill-maintenance-20260514-github-sync
- lane: audit
- role_alias_zh: 审核
- role_applicability: active
- attendance_status: active
- lane_alias_zh: 审核
- owner: local sequential audit fallback
- owner_alias_zh: 审核
- system_agent_id: controller-local-audit
- authorization_source: no explicit subagent authorization
- agent_mode: single-agent-no-auth
- run_manifest_path: references/cases/skill-maintenance-20260514-github-sync-manifest.md
- objective: verify user request compliance, changed-file scope, GitHub evidence, and validation result
- inputs: lock, checklist, manifest, task cards, git evidence
- outputs: final audit verdict
- dependencies: completed GitHub sync and validation evidence
- spawn_requested: no
- spawn_status: not-requested
- fallback_mode: sequential-audit-fallback
- status: active
- sequential_audit_fallback_id: controller-local-audit
- audit_required: yes
- audit_spawn_or_fallback_mode: sequential-audit-fallback
- action_audit_scope: all action cycles including read-only and mutation actions
- action_audit_verdict_cadence: per cycle
- action_audit_verdicts: bootstrap pass; final pending
- mutation_audit_scope: control artifacts and git synchronization
- mutation_audit_verdicts: pending
- reviewed_artifacts: pending
- reviewed_action_cycles: bootstrap complete; rest pending
- command_or_check: pending
- verdict: pending
- open_blockers: pending GitHub evidence
