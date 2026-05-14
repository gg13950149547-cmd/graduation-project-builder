# Skill Structure Audit 2026-04-25

## Summary
- active non-archive files inspected: 147
- active text/json files inspected: 130
- archived root backup files: 6
- manifest rule count: 202
- legacy numeric headings remaining in user-feedback rule files: 0

## Rule Owner Model
- `references/rule-owner-map.json` is now the owner index for durable user-feedback rules.
- User-feedback headings use stable namespaced IDs while preserving legacy numeric aliases in heading text and manifest fields.
- `references/user-feedback-persistence.md` routes by child file namespace and manifest instead of exact numeric ranges.

## Backup Cleanup
- moved backup: `references/archive/backups/memory.md.bak-clean-20260325-231050`
- moved backup: `references/archive/backups/SKILL.md.backup-20260410-final-mojibake-fix`
- moved backup: `references/archive/backups/SKILL.md.backup-20260410-utf8bomfix`
- moved backup: `references/archive/backups/SKILL.md.bak-20260323-221556`
- moved backup: `references/archive/backups/SKILL.md.bak-clean-20260325-231050`
- moved backup: `references/archive/backups/SKILL.md.bak-merge-20260409-1919`

## Remaining Structural Risks
- `validate_skill_gate_registry_bundle.py` still contains legacy required-line registries for non-manifest hard gates; this is intentional for compatibility while manifest validation is introduced.
- Some non-user-feedback markdown files still use ordinary numbered section headings; they are section numbers, not manifest-owned durable rule IDs.
- WPS/Office COM rendering remains environment-dependent and should be interpreted separately from static skill validation.

## Validator Coupling Notes
- occurrences of `REQUIRED_RULE_LINES_BY_FILE` token in registry bundle: 3
- New durable rule ownership should be added to the manifest first, then router and selftest, rather than adding exact router range strings.

## Final Validation 2026-04-25
- `scripts/check_utf8_clean.py --root <skill-root> --json`: PASS, checked 128 files with no issues.
- `scripts/validate_skill_gate.cmd --skill-root <skill-root>`: PASS.
- `scripts/selftest_skill_flow.py`: PASS, `OVERALL=PASS`.
- Active user-feedback rule headings no longer use duplicate numeric IDs.
- Root backup files were removed from the active scan surface and archived under `references/archive/backups/`.
- `scripts/run_integration_gate.py`: selected real DOCX cases PASS after renderer diagnostic separation:
  - `complete_sample_smoke`: PASS with `sample_self_check --fail-on-issues`; the previous masked self-check failure is fixed.
  - `sample_self_check_abstract_self_donor_alias_detection`: PASS for rule detection; real renderers failed first, so the case recorded `renderer_warning` and used a diagnostic PDF only to continue DOCX-rule validation.
  - `paragraph_review_microcycle`: PASS with rendered review PDFs.
  - `serialized_helper_mutation_chain`: PASS with staged DOCX/PDF mutation evidence.
  - `frontmatter_roundtrip`: PASS with rendered front-matter PDF.
- Local Office/WPS renderer instability remains an environment diagnostic, not a static skill-structure failure.
