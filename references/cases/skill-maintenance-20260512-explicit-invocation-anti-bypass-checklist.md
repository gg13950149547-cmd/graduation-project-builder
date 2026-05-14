# Explicit Invocation Anti-Bypass Checklist

- [x] Add a durable rule that explicit invocation is a state transition, not reference context.
- [x] Expose the rule through SKILL.md and user-feedback routing.
- [x] Add lock/template fields for anti-bypass state, canonical gate enforcement, and failed-evidence escalation.
- [x] Extend validators so pass-shaped records fail when anti-bypass fields are missing or contradictory.
- [x] Add selftests for missing anti-bypass lock fields and narrow-checker substitution.
- [x] Update rule-owner map and file-role index.
- [x] Record consolidation and validation evidence.
