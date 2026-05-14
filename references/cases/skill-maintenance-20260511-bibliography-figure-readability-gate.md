# Skill Maintenance Case: Bibliography Leading Number And Figure Readability Gate

- date: 2026-05-11
- mode: skill-maintenance plus thesis repair
- scope: current campus abnormal-behavior thesis repair and canonical gate hardening
- authorization: user authorized multi-agent collaboration; citation, figure, TOC/pagination, and skill-gate lanes performed read-only review while the controller made serialized skill edits

## Trigger

The current step26 thesis candidate still had two pass-shaped failures:

- Bibliography entry labels `[12]` through `[25]` carried `w:vertAlign=superscript`, but citation-order and older bibliography-count evidence still passed.
- Seven structural figures were inserted at about `10.00 x 1.89 cm`, leaving process and architecture diagrams unreadable while older figure checks only rejected oversized images.

## Skill Changes

- `scripts/audit_docx_font_encoding.py` now runs an intrinsic bibliography leading-number check on the exact final DOCX even when no reference/template DOCX is supplied.
- Bibliography leading labels fail when the visible `[n]` token carries `w:vertAlign=superscript` or `w:vertAlign=subscript`.
- `scripts/selftest_skill_flow.py` now has targeted regression coverage for bibliography leading-number vertical alignment and structural figure undersizing.
- `FB-CITE-040`, `FB-THESIS-003`, and `EXEC-MAINT-068` record the durable owner chain for these defects.

## Validation Plan

- `py -3 -m py_compile scripts\audit_docx_font_encoding.py scripts\audit_docx_figure_extents.py scripts\selftest_skill_flow.py`
- `py -3 scripts\selftest_skill_flow.py --case docx_font_audit_bibliography_leading_number_vertalign_rejected --case audit_figure_extents_structural_undersized_rejected --quiet`
- `py -3 -m json.tool references\rule-owner-map.json > $null`
- `py -3 scripts\check_utf8_clean.py --root . --json`
- `py -3 scripts\validate_skill_gate.py --skill-root .`

## Acceptance Impact

A final thesis cannot pass references when bibliography entry labels are citation-style superscript/subscript text. A final thesis cannot pass figure-size review when structural figures are too flat to read, even if the figures do not exceed width or page-height limits.

## Continuation: Step28 False-Pass Closure

- date: 2026-05-11
- trigger: user reported that reference numbers, unreadable figures, TOC format, and whole-document pagination still failed after step28.
- multi-agent status: five existing read-only agents were used; four returned findings before this continuation, and the remaining lane did not return within the wait window, so the controller proceeded with sequential fallback for implementation.
- skill changes:
  - `repair_front_matter_page_numbering.py` accepts inline Chinese abstract labels such as `摘 要：...` as a valid front-matter sentinel instead of failing closed on documents without a standalone abstract-title paragraph.
  - `audit_docx_figure_extents.py` adds `structural_min_readable_width_cm` with default `9.0`, so narrow structural figures fail even when their height is acceptable.
  - `selftest_skill_flow.py` adds inline-abstract page-number coverage and structural figure narrow-width coverage, and promotes bibliography-numbering/figure-readability cases into `fast-thesis-records`.
  - `rule-owner-map.json` marks `FB-THESIS-006`, `FB-THESIS-007`, and `FB-LAYOUT-064` as enforceable with validator/selftest owners.
- validation target:
  - `py -3 -m py_compile scripts\repair_front_matter_page_numbering.py scripts\audit_docx_figure_extents.py scripts\selftest_skill_flow.py`
  - targeted selftests for inline abstract, structural width/height, bibliography leading-number, and bibliography auto/manual conflict
  - JSON parse, UTF-8 clean, and `validate_skill_gate.py --skill-root .`
