# Skill Maintenance Case: Bibliography Numbering And Formula Lead-In Gate

- date: 2026-05-11
- mode: skill-maintenance plus thesis repair
- scope: canonical skill gate hardening before repairing the current Transformer neural translation thesis
- write boundary: citation audit, formula audit, regression selftests, durable rule owners, rule-owner map, file-role index, promotion audit, and this case record

## Maintenance Reason

A read-only audit of the current thesis found two pass-shaped risks that were not hard enough in the skill gate:

- bibliography entries could contain both visible manual bracket numbers such as `[1]` and paragraph-level Word automatic numbering, which may render duplicated numbers even when citation order checks pass
- a paragraph ending with a formula lead-in such as `下式表示：` could be followed directly by explanation text such as `其中...`, meaning the formula promised by the prose was missing

Both defects affect final thesis acceptance and should be caught before handoff instead of being treated as cosmetic review notes.

## Rule Changes

- `FB-CITE-038` owns the rule that bibliography entries must not combine manual `[n]` visible text with `w:numPr` Word numbering.
- `FMT-FORMULA-002` owns the rule that a formula lead-in must be followed by a real formula surface or the lead-in must be rewritten.

## Enforcement

- validator: `scripts/audit_thesis_citations.py::audit_docx`
- validator: `scripts/audit_docx_formula_objects.py::audit_docx`
- selftest: `scripts/selftest_skill_flow.py::case_bibliography_manual_auto_numbering_rejected`
- selftest: `scripts/selftest_skill_flow.py::case_formula_leadin_without_formula_rejected`

## Validation Plan

- Compile changed scripts.
- Parse `references/rule-owner-map.json`.
- Run the two targeted regression selftests.
- Run `scripts/check_utf8_clean.py --root . --json`.
- Run `scripts/validate_skill_gate.py --skill-root .`.

## Acceptance Impact

A final thesis cannot claim citation/reference or formula acceptance when either new detector fails on the exact final DOCX. The correct repair is a new review copy with the conflicting numbering or missing formula lead-in resolved, followed by fresh audits bound to that output.
