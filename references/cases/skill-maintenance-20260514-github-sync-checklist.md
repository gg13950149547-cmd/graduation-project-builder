# Skill Maintenance Checklist: GitHub Sync

- run id: skill-maintenance-20260514-github-sync
- mode: skill-maintenance
- subtask: sync local graduation-project-builder skill bundle to GitHub
- source skill root: C:/Users/Administrator/.agents/skills/graduation-project-builder

## Required Steps

- [x] Explicit invocation recognized and routed to skill-maintenance mode.
- [x] `SKILL.md` loaded.
- [x] `references/user-feedback-persistence.md` loaded.
- [x] `references/user-feedback/maintenance-and-structure.md` loaded for EXEC-MAINT-065, EXEC-MAINT-071, and EXEC-MAINT-072.
- [x] `references/agents/agent-lanes.md` loaded.
- [x] Fresh skill-invocation lock created before mutation.
- [x] Pre-lock git probe recorded as contaminated/reference-only drift.
- [x] Agent run manifest and task-card record created in single-agent-no-auth mode.
- [ ] Re-check local git repository state after lock.
- [ ] Determine GitHub authentication and target remote.
- [ ] Initialize or connect a git repository without deleting existing files.
- [ ] Review changed/untracked files before commit.
- [ ] Commit only the intended skill bundle content.
- [ ] Push to the selected GitHub remote.
- [ ] Run skill bundle validation.
- [ ] Update manifest/task cards with evidence, commit, remote, and final verdict.
- [ ] Final handoff names exact repository/remote status and any unresolved blocker.

## Scope Limits

- Thesis DOCX/PDF files: not in scope.
- Current workspace project files: not in scope except this external control record is housed inside the canonical skill bundle.
- Downloads/installers: none expected; if needed, keep them on D:.

## Audit Notes

- Subagents were not explicitly authorized by the user, so no spawned agents may be claimed.
- Audit is sequential single-agent fallback and must review the final Git/GitHub evidence before handoff.
