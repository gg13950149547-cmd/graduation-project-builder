# Compatibility Export External Audit

## Audit Meta
- audit record date: 2026-04-20
- audit scope: local Python code roots under %USERPROFILE%\.agents, %USERPROFILE%\.codex\skills, and %USERPROFILE%\Documents\Codex, excluding the canonical skill bundle itself and transient session/log caches

## Export Audit Inventory

### SCRIPT_RUNTIME_FORBIDDEN_TOKENS_BY_FILE
- retention tier at audit time: short-term-required
- audited local direct importers: scripts/selftest_skill_flow.py; scripts/validate_skill_gate_bundle.py
- audited compatibility surfaces: scripts/validate_skill_gate_registry.py
- external caller retirement status: not-applicable-while-short-term-required
- external caller retirement evidence: bridge intentionally retained while token-only compatibility surface remains active

### SEMANTIC_ONLY_RULE_FILES
- retention tier at audit time: conditional-removal-candidate
- audited local direct importers: scripts/selftest_skill_flow.py; scripts/validate_skill_gate_bundle.py
- audited compatibility surfaces: scripts/validate_skill_gate_registry.py
- external caller retirement status: external-callers-retired
- external caller retirement evidence: 2026-04-20 local code-root audit found no external semantic-only compatibility callers outside the canonical skill bundle; see COMPATIBILITY-EXPORT-EXTERNAL-AUDIT-RECORD.md
