# Skill Maintenance Case: Comment Format Front-Matter And Figure Evidence

## Scope

- Date: 2026-05-11
- Mode: canonical skill-maintenance plus project thesis repair continuation
- User authorization: multi-agent collaboration authorized in the current thread
- Project root: `D:\项目\校园异常行为检测研究`
- Source DOCX: `D:\项目\校园异常行为检测研究\校园异常检测v2(1)(1).docx`
- Current candidate under review: `D:\项目\校园异常行为检测研究\_analysis\run-20260511-comment-format-repair\stage\step-20-heading-direct-format.docx`

## Failure Pattern

Repeated repair passes could still report success while the final handoff used stale or weak evidence:

- English abstract indentation and keyword label/content split were not exposed as hard metrics in the front-matter report.
- Figure-size comments could pass from width-only or caption-overcount evidence instead of final-DOCX body figure extents.
- Front-matter drawings and narrative prose such as `图3-1展示了...` could pollute figure counts.
- Comment-resolution ledgers could cite old figure/caption reports instead of exact-output detector evidence.

## Canonical Fix

- `scripts/audit_docx_frontmatter_structure.py` is the front-matter hard-field evidence owner for abstract and keyword surfaces.
- `scripts/audit_docx_figure_extents.py` is the final-DOCX figure display-size and adjacency evidence owner for comment-driven figure-size repairs.
- `references/rule-owner-map.json` maps the front-matter audit into `FMT-ABSTRACT-001` and maps the figure-extents audit into `FB-THESIS-003` / `EXEC-MAINT-068`.
- `FILE-ROLE-INDEX.md` records both scripts as active canonical scripts and documents their evidence responsibilities.

## Multi-Agent Findings Incorporated

- Audit lane found stale final-path/SHA references and missing final acceptance binding.
- Format lane found that the candidate's English abstract and body line spacing had usable direct OOXML metrics, but the old reports did not expose enough details for a hard handoff.
- Figure lane found that old caption/explanation evidence overcounted narrative figure references and that the v2 figure-extents report is the correct source for body figure count and size closure.

## Validation Targets

- `py -3 -m py_compile scripts\audit_docx_frontmatter_structure.py scripts\audit_docx_figure_extents.py scripts\selftest_skill_flow.py`
- `py -3 -m json.tool references\rule-owner-map.json > $null`
- `py -3 scripts\selftest_skill_flow.py --case frontmatter_audit_reports_english_indent_metrics_valid --case audit_figure_extents_oversized_body_image_rejected --case audit_figure_extents_frontmatter_image_rejected --case audit_figure_extents_caption_overcount_guard_valid --quiet`
- `py -3 scripts\validate_skill_gate.py --skill-root .`
- `py -3 scripts\check_utf8_clean.py --root . --json`

## Remaining Project-Handoff Requirement

The project review copy must still regenerate exact-final acceptance evidence bound to the promoted DOCX path and SHA256. Old `final-*`, `step-19`, or stale `review-pass-20260511-comment-format-current-open-this.docx` evidence must not be cited as the final closure record.
