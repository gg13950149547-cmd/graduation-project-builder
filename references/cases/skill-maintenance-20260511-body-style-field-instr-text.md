# Skill Maintenance Case: Body-Style Field Instruction Visibility

- date: 2026-05-11
- mode: skill-maintenance plus thesis-only follow-up
- rule owner: `FB-CITE-039`
- affected validator: `scripts/audit_docx_body_style.py`
- regression coverage: `scripts/selftest_skill_flow.py::case_audit_body_style_ignores_field_instr_text_valid`

## Defect

Late thesis body-style review reported `HYPERLINK \l "cite_ref_*"` inside body paragraph excerpts. Those strings came from Word field instruction nodes (`w:instrText`) rather than rendered body text. Treating them as visible text created false mixed-script/font drift and made final evidence harder to interpret.

## Repair

The body-style audit now extracts visible paragraph text only from rendered text nodes (`w:t`) and tabs. Hidden field instruction text is excluded from paragraph excerpts and mixed-script run checks. Citation leakage is still handled by the citation audit, which checks rendered marker text, superscript state, hyperlink style, and anchor leakage.

## Acceptance

The targeted selftest builds a DOCX paragraph with a hidden `HYPERLINK` field instruction and a visible superscript citation marker. The body-style audit must pass, and the report must not expose the hidden field instruction as body text.
