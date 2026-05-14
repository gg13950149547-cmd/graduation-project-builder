# Skill Maintenance Case: OpenXML Compatibility Render Blocker

- date: 2026-05-10
- mode: skill-maintenance plus thesis-only recovery
- trigger: a repaired thesis DOCX could be opened by the user workflow but failed LibreOffice PDF export and `officecli validate` with invalid WordprocessingML property order and missing `mc:Ignorable` namespace declarations
- scope: canonical skill only; no original thesis overwrite

## Root Cause

- Previous bounded XML repairs preserved the DOCX package but did not normalize schema-sensitive child order inside `w:pPr`, `w:rPr`, and `w:style`.
- Some serialized parts carried `mc:Ignorable` values such as `w14 w15 wp14` while the corresponding namespace declarations were absent.
- This created a false-progress path: package-level preservation and text audits could pass while renderer/PDF evidence failed.

## Durable Rule

- `EXEC-MAINT-066` requires thesis DOCX helpers to preserve OpenXML compatibility before final handoff.
- The allowed recovery path is `scripts/repair_docx_openxml_compat.py`, which rewrites only selected XML parts, restores property child order, adds missing namespace declarations, and does not edit visible thesis text, media, relationships, comments, or fields.

## Coverage

- owner file: `references/user-feedback/maintenance-and-structure.md`
- router exposure: `references/user-feedback-persistence.md`
- owner map: `references/rule-owner-map.json`
- helper: `scripts/repair_docx_openxml_compat.py`
- selftest: `docx_openxml_compat_property_order_valid`
- file-role index: `FILE-ROLE-INDEX.md`

## Validation

- `py -3 -m py_compile scripts\repair_docx_openxml_compat.py scripts\inspect_docx_pagination_structure.py scripts\validate_skill_gate_record_gate.py scripts\generate_thesis_acceptance_record.py scripts\selftest_skill_flow.py`: PASS
- `py -3 -m json.tool references\rule-owner-map.json > $null`: PASS
- targeted selftests `docx_openxml_compat_property_order_valid`, `gate_live_toc_required_static_toc_rejected`, `acceptance_generator_live_toc_requirement_preserved`, `pagination_structure_live_toc_field_absent_rejected`, and `acceptance_generator_validator_failure_rewrites_handoff_blocked`: PASS
- `py -3 scripts\validate_skill_gate.py --skill-root .`: PASS
- `py -3 scripts\check_utf8_clean.py --root . --json`: PASS
