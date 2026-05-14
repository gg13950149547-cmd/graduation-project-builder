# Skill Maintenance Case: Explicit Invocation Anti-Bypass

## Scope

- mode: skill-maintenance
- user request: modify `graduation-project-builder` so explicit invocation always activates the skill and cannot be bypassed by ad hoc execution.
- mutation boundary: canonical skill bundle only; no thesis DOCX mutation.
- authorization source: no same-turn subagent authorization; single-agent with sequential audit fallback.

## Agent Manifest

- run_id: skill-maintenance-20260512-explicit-invocation-anti-bypass
- task_mode: skill-maintenance
- subtask: fail closed when explicit skill invocation is not allowed to control execution
- authorization_source: no same-turn subagent authorization
- agent_mode: single-agent-no-auth
- max_concurrent_live_agents: 1
- live_agent_count_plan: controller only; audit is sequential fallback
- dispatch_wave_plan: one local implementation wave, one sequential audit pass
- audit_presence_by_wave: sequential audit fallback reviews changed owner files, templates, validators, selftests, and validation output
- required_lanes: controller; content-worker; format-worker; figure-worker; citation-worker; program-worker; acceptance-worker; audit
- complete_role_roster: controller=总控; content-worker=内容; format-worker=格式; figure-worker=图表; citation-worker=引用; program-worker=程序; acceptance-worker=验收; audit=审核
- role_attendance_matrix: controller active; acceptance-worker active; audit active-sequential-fallback; content-worker not-applicable; format-worker not-applicable; figure-worker not-applicable; citation-worker not-applicable; program-worker not-applicable
- not_applicable_lanes_with_reasons: no thesis content, format, figure, citation, or program artifact is being edited
- audit_verdict: pass
- action_audit_scope: rule owner, router, templates, validator, selftest, file-role index, validation output
- action_audit_verdict_cadence: after rule edit and after validation
- mutation_audit_scope: changed skill files only
- mutation_audit_verdicts: pass canonical skill-bundle files only; no thesis DOCX/PDF mutation
- skill_invocation_verified: pass
- routed_references_verified: pass
- active_checklist_verified: pass

## Task Cards

- controller: active; owns decomposition, edits, validation, and final merge.
- acceptance-worker: active; owns validator and selftest coverage.
- audit: sequential fallback; must reject completion if any owner-map, template, validator, selftest, or file-role-index update is missing.
- content-worker: not-applicable because no thesis text is edited.
- format-worker: not-applicable because no DOCX format surface is edited.
- figure-worker: not-applicable because no figure surface is edited.
- citation-worker: not-applicable because no citation surface is edited.
- program-worker: not-applicable because no software delivery surface is edited.

## Planned Changed Files

- `SKILL.md`
- `references/user-feedback-persistence.md`
- `references/user-feedback/maintenance-and-structure.md`
- `assets/skill-invocation-lock-template.md`
- `assets/final-acceptance-template.md`
- `references/rule-owner-map.json`
- `FILE-ROLE-INDEX.md`
- `scripts/validate_skill_gate_record_gate.py`
- `scripts/validate_skill_gate_registry_core.py`
- `scripts/selftest_skill_flow.py`
- `DURABLE-RULE-PROMOTION-AUDIT.md`

## Validation Evidence

- JSON parse: pass, `py -3 -c "import json, pathlib; json.load(open(pathlib.Path('references/rule-owner-map.json'), encoding='utf-8'))"`
- py_compile changed scripts: pass, `py -3 -m py_compile scripts\validate_skill_gate_record_gate.py scripts\validate_skill_gate_registry_core.py scripts\generate_thesis_acceptance_record.py scripts\selftest_skill_flow.py`
- targeted anti-bypass selftests: pass, `py -3 scripts\selftest_skill_flow.py --case skill_invocation_lock_missing_rejected --case skill_invocation_lock_blocked_rejected --case skill_invocation_lock_anti_bypass_field_missing_rejected --case skill_invocation_smoke_substitute_rejected --case skill_invocation_blocked_evidence_caveat_rejected --quiet`
- positive record selftests: pass, `py -3 scripts\selftest_skill_flow.py --case program_plus_thesis_valid --case format_repair_valid --case thesis_only_valid --quiet`
- skill gate: pass, `py -3 scripts\validate_skill_gate.py --skill-root .`
- UTF-8 clean: pass, `py -3 scripts\check_utf8_clean.py --root . --json`
- fast-core: pass, `py -3 scripts\selftest_skill_flow.py --suite fast-core --quiet --fail-fast`
