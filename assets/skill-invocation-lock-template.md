# Skill Invocation Lock

- skill name: graduation-project-builder
- user invocation source:
- invocation detected: yes | no
- lock created before mutation?: yes | no
- run start order verdict: pass | blocked
- task mode:
- subtask:
- project root:
- requested mutation?: yes | no
- thesis/docx surface touched?: yes | no
- loaded entrypoint:
- loaded routed references:
- active checklist path:
- agent run manifest path:
- lane task card paths:
- project-local helper preflight report path:
- project-local helper risk count:
- project-local helper disposition:
- mutation transaction record path:
- mutation allowed verdict: pass | audit-only | blocked
- blocked reason:
- exact output path:
- exact output sha256:
- final gate record path:
- final gate command:
- final gate verdict: pass | blocked | pending
- explicit invocation source type:
- skill activation status:
- rule engine takeover verdict:
- prohibited bypasses checked:
- canonical gate required?: yes | no
- narrow/smoke gate substitute used?: yes | no
- failed evidence escalation verdict:
- no project-local thick helper execution before preflight?: yes | no | not-applicable
- no non-control action before lock?: yes | no
- no mutation before lock?: yes | no
- final handoff allowed verdict: pass | blocked | pending
- blocked evidence disposition:

## Use

Create this lock immediately after classifying the mode and before any file mutation or handoff. If any required value is missing, blocked, or contradicted by helper preflight evidence, the run is audit-only until the lock is repaired and rechecked.
The lock is also the anti-bypass record: after an explicit invocation, any execution that cannot fill these fields is not a skill-controlled run and must remain audit-only.
