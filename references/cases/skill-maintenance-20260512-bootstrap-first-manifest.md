# Skill Maintenance Manifest: Explicit Invocation Bootstrap First

## Run Fields

- run_id: skill-maintenance-20260512-bootstrap-first
- task_mode: skill-maintenance
- subtask: prevent explicit graduation-project-builder invocations from starting as reference-only execution
- authorization_source: no same-turn subagent authorization
- agent_mode: single-agent-no-auth
- max_concurrent_live_agents: 1
- live_agent_count_plan: controller only; audit is sequential fallback
- dispatch_wave_plan: one local maintenance wave, one sequential audit pass
- audit_presence_by_wave: sequential audit fallback reviews changed files and validation output
- required_lanes: controller; content-worker; format-worker; figure-worker; citation-worker; program-worker; acceptance-worker; audit
- complete_role_roster: controller; content-worker; format-worker; figure-worker; citation-worker; program-worker; acceptance-worker; audit
- role_attendance_matrix: controller active; acceptance-worker active; audit active sequential fallback; all content/format/figure/citation/program lanes not-applicable
- not_applicable_lanes_with_reasons: no thesis text, format surface, figure, citation, or program artifact is edited
- spawn_attempted: no
- spawned_agent_ids: none
- sequential_fallback_reason: no explicit subagent authorization
- sequential_audit_fallback_id: local-controller-audit
- audit_verdict: pass
- action_audit_scope: entrypoint rule, router, owner map, selftest, file-role index, validation
- mutation_audit_scope: canonical skill bundle files only; no project thesis DOCX or software mutation
- skill_invocation_verified: pass
- routed_references_verified: pass
- active_checklist_verified: pass

## Planned Changed Files

- `SKILL.md`
- `references/user-feedback-persistence.md`
- `references/user-feedback/maintenance-and-structure.md`
- `references/rule-owner-map.json`
- `FILE-ROLE-INDEX.md`
- `scripts/selftest_skill_flow.py`
- `references/cases/skill-maintenance-20260512-bootstrap-first-lock.md`
- `references/cases/skill-maintenance-20260512-bootstrap-first-checklist.md`
- `references/cases/skill-maintenance-20260512-bootstrap-first-manifest.md`

## Validation Evidence

- targeted bootstrap selftests: pass, `py -3 scripts\selftest_skill_flow.py --case explicit_invocation_bootstrap_first_documented_valid --case explicit_invocation_bootstrap_non_control_before_lock_rejected --quiet`
- targeted anti-bypass selftests: pass, `py -3 scripts\selftest_skill_flow.py --case skill_invocation_lock_missing_rejected --case skill_invocation_lock_blocked_rejected --case skill_invocation_lock_anti_bypass_field_missing_rejected --case skill_invocation_smoke_substitute_rejected --case skill_invocation_blocked_evidence_caveat_rejected --quiet`
- JSON parse: pass, `py -3 -c "import json,pathlib; json.load(open(pathlib.Path('references/rule-owner-map.json'),encoding='utf-8'))"`
- py_compile changed scripts: pass, `py -3 -m py_compile scripts\validate_skill_gate_record_gate.py scripts\validate_skill_gate_registry_core.py scripts\generate_thesis_acceptance_record.py scripts\selftest_skill_flow.py`
- skill gate: pass, `py -3 scripts\validate_skill_gate.py --skill-root .`
- UTF-8 clean: pass, `py -3 scripts\check_utf8_clean.py --root . --json`
- fast-core: pass, `py -3 scripts\selftest_skill_flow.py --suite fast-core --quiet --fail-fast`

## Multi-Agent Audit Closure

- rules-chain audit: initial gap was direct validator coverage and parse evidence; closed by adding `no non-control action before lock?`, validator owner `validate_skill_invocation_lock`, and JSON parse evidence.
- validation audit: initial conditional pass with missing negative timing case; closed by adding `case_explicit_invocation_bootstrap_non_control_before_lock_rejected`.
- record audit: initial gap was open checklist, lock, and manifest fields; closed in this record set after validation.
- boundary verdict: pass, canonical skill bundle files only; no thesis DOCX/PDF or project program artifact was mutated.
