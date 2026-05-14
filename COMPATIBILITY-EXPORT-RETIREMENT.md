# Compatibility Export Retirement Note

## Export Inventory

### SCRIPT_RUNTIME_FORBIDDEN_TOKENS_BY_FILE
- kind: alias
- retention tier: short-term-required
- active source: SCRIPT_RUNTIME_POLICY_BY_FILE[*].tokens
- external caller retirement status: not-applicable-while-short-term-required
- external caller retirement evidence: bridge intentionally retained while token-only compatibility surface remains active
- known direct local importers: scripts/selftest_skill_flow.py; scripts/validate_skill_gate_bundle.py
- compatibility surfaces: scripts/validate_skill_gate_registry.py
- retirement checklist: switch direct local callers to SCRIPT_RUNTIME_POLICY_BY_FILE token lists; verify no external token-only compatibility imports remain; remove the alias from compatibility exports and aggregators in the same change
- removal condition: remove only after token-only compatibility imports have been retired

### SEMANTIC_ONLY_RULE_FILES
- kind: legacy-export
- retention tier: conditional-removal-candidate
- active source: SEMANTIC_RULE_GROUPS_BY_FILE
- external caller retirement status: external-callers-retired
- external caller retirement evidence: 2026-04-20 local code-root audit found no external semantic-only compatibility callers outside the canonical skill bundle; see COMPATIBILITY-EXPORT-EXTERNAL-AUDIT-RECORD.md
- known direct local importers: scripts/selftest_skill_flow.py; scripts/validate_skill_gate_bundle.py
- compatibility surfaces: scripts/validate_skill_gate_registry.py
- retirement checklist: switch direct local callers to SEMANTIC_RULE_GROUPS_BY_FILE-based checks; verify no external semantic-only compatibility imports remain; remove the legacy export from compatibility exports and aggregators in the same change
- removal condition: remove only after semantic-only compatibility imports have been retired
