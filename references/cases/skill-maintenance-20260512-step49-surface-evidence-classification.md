# Skill Maintenance Case: Step49 Surface Evidence Classification

Date: 2026-05-12

## Scope

- Mode: `skill-maintenance` plus exact-output thesis acceptance continuation.
- Thesis mutation scope: none in this case record; the original manuscript and review DOCX are not modified.
- Candidate thesis output under review: `review-pass-20260511-comment-format-step49-open-this.docx` in the project run directory.
- User authorization: prior messages explicitly authorized multi-agent collaboration. The platform already had six live agents, so fresh dispatch was unavailable and this traceability closeout records sequential fallback rather than claiming new live-agent work.

## Defect

The step49 acceptance record could only be trusted after two surface-evidence false-pass risks were closed:

- Caption typography evidence must not pass from a prose statement such as `no formal captions found`; it must expose numeric template/actual paragraph and typography fields even when a formal caption donor is absent.
- Direct surface metric validation must not classify TOC rows or figure/table captions as `body_text`, and must still detect inline abstract body paragraphs such as `摘 要：...` and `Abstract: ...`.

## Durable Rule Binding

- `FMT-EVID-010` owns the all-surface paragraph-dialog and typography evidence requirement.
- `scripts/measure_surface_hardfields.py::build_caption_typography_record` owns numeric fallback caption evidence.
- `scripts/validate_skill_gate_record_evidence.py::_body_text_paragraphs` and `_front_matter_surface_paragraphs` own robust body/abstract classification.
- Regression coverage is in `scripts/selftest_skill_flow.py` cases `surface_hardfields_caption_missing_pair_numeric_valid`, `gate_direct_body_text_excludes_toc_caption_valid`, and `gate_direct_inline_abstract_body_valid`.

## Validation PASS

- `py -3 -m py_compile scripts\validate_skill_gate_record_evidence.py scripts\measure_surface_hardfields.py scripts\generate_thesis_acceptance_record.py scripts\selftest_skill_flow.py`
- `py -3 -m json.tool references\rule-owner-map.json`
- `py -3 scripts\selftest_skill_flow.py --case surface_hardfields_caption_missing_pair_numeric_valid --case gate_direct_body_text_excludes_toc_caption_valid --case gate_direct_inline_abstract_body_valid --quiet`
- `py -3 scripts\validate_skill_gate.py --skill-root .`
- `py -3 scripts\check_utf8_clean.py --root . --json`
- `py -3 scripts\validate_skill_gate.py --gate-record <step49 final acceptance record>`

## Remaining Risk

This case closes the evidence-classification and numeric-field false-pass route. It does not claim new manuscript edits; any later manuscript mutation still needs a new source/final transaction, rendered evidence, and final gate on the exact output.
