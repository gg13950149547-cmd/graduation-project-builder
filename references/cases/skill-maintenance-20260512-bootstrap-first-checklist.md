# Skill Maintenance Checklist: Explicit Invocation Bootstrap First

- [x] Create skill-maintenance lock before mutating canonical skill files.
- [x] Record single-agent/no-subagent maintenance mode.
- [x] Add an entrypoint bootstrap gate to `SKILL.md`.
- [x] Add durable owner rule for bootstrap-first behavior.
- [x] Expose the rule through the user-feedback router.
- [x] Add owner-map entry with validator and selftest coverage.
- [x] Add selftests proving the bootstrap-first rule is wired and rejects non-control action before lock.
- [x] Update file-role index so future edits know where the rule lives.
- [x] Run targeted selftest, anti-bypass selftests, UTF-8 check, skill gate, and fast-core.
- [x] Record final validation evidence in the manifest.
