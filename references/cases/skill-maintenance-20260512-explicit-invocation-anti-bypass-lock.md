# Skill Invocation Lock

- skill name: graduation-project-builder
- user invocation source: current user explicitly linked graduation-project-builder and requested canonical skill update
- invocation detected: yes
- lock created before mutation?: yes
- run start order verdict: pass
- task mode: skill-maintenance
- subtask: prevent explicit skill invocation from degrading into reference-only guidance or ad hoc execution
- project root: C:\Users\Administrator\.agents\skills\graduation-project-builder
- requested mutation?: yes
- thesis/docx surface touched?: no
- loaded entrypoint: C:\Users\Administrator\.agents\skills\graduation-project-builder\SKILL.md
- loaded routed references: references/user-feedback-persistence.md; references/user-feedback/maintenance-and-structure.md; references/agents/agent-lanes.md; C:\Users\Administrator\.codex\skills\.system\skill-creator\SKILL.md
- active checklist path: references/cases/skill-maintenance-20260512-explicit-invocation-anti-bypass-checklist.md
- agent run manifest path: references/cases/skill-maintenance-20260512-explicit-invocation-anti-bypass.md
- lane task card paths: references/cases/skill-maintenance-20260512-explicit-invocation-anti-bypass.md
- project-local helper preflight report path: not-applicable-skill-maintenance-no-thesis-docx-mutation
- project-local helper risk count: 0
- project-local helper disposition: clean-skill-maintenance-no-project-local-thesis-helper-use
- mutation transaction record path: not-applicable-no-thesis-docx-mutation
- mutation allowed verdict: pass
- blocked reason: none
- exact output path: C:\Users\Administrator\.agents\skills\graduation-project-builder
- exact output sha256: not-applicable-directory-output
- final gate record path: references/cases/skill-maintenance-20260512-explicit-invocation-anti-bypass.md
- final gate command: py -3 scripts\validate_skill_gate.py --skill-root .
- final gate verdict: pass

## Anti-Bypass Fields

- explicit invocation source type: user-linked skill token
- skill activation status: pass active fail-closed skill-controlled workflow
- rule engine takeover verdict: pass
- prohibited bypasses checked: pass no reference-only execution, ad hoc helper substitution, smoke-only gate, or handwritten handoff used
- canonical gate required?: yes
- narrow/smoke gate substitute used?: no
- failed evidence escalation verdict: pass failed evidence blocks handoff instead of moving to caveats
- no project-local thick helper execution before preflight?: yes
- no mutation before lock?: yes
- final handoff allowed verdict: pass
- blocked evidence disposition: none

## Use

This lock exists because the current maintenance task repairs a failure mode where explicit `graduation-project-builder` invocation was recognized but not allowed to control execution. The run may edit the canonical skill bundle only after this lock is present.
