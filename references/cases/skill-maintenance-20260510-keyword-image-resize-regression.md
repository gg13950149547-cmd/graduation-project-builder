# Skill Maintenance Case - 2026-05-10 Keyword/Image Resize Regression

## Scope

- canonical skill root: `C:\Users\Administrator\.agents\skills\graduation-project-builder`
- project context: `D:\项目\校园异常行为检测研究`
- thesis DOCX mutation in this case: no
- original manuscript overwrite: no
- agent mode: authorized multi-agent review plus controller merge, max live agents 3

## Failure Pattern

- `repair_thesis_surface_format.py` had an image display-resize plan path that could mutate `wp:extent` / `a:ext` without a transaction-owned figure manifest.
- Generic body prose containing words such as `图像预处理` could be escalated as image mutation intent when no real image/drawing action existed.
- Keyword repair could pick TOC/template-instruction donor paragraphs, causing keyword label/content formatting to collapse into the wrong front-matter style.
- The new selftest `repair_thesis_surface_format_keyword_toc_template_donor_fallback_valid` initially failed because the fixture did not isolate abstract/keyword repair from body-prose normalization.

## Durable Rules Touched

- `FB-LAYOUT-038`: ordinary explanatory body prose with `图像...` is not a figure caption or image mutation by itself.
- `FMT-ABSTRACT-001`: keyword label/content formatting must stay distinct and cannot use TOC/template instruction donors.
- `EXEC-MAINT-063`: display-only image resizing is a drawing-object mutation and must go through transaction/figure-manifest ownership.
- `CORE-TRANS-001`: transaction intent must require a manifest only for actual image/drawing mutation, not for generic prose terms.

## Code And Reference Changes

- `scripts/repair_thesis_surface_format.py`: rejects non-empty `plan.image_display_resize`; avoids ElementTree truth-value warnings in keyword run selection.
- `scripts/validate_thesis_mutation_transaction.py`: image mutation intent ignores generic `image` / `图像` words unless paired with a specific image/drawing action or actual media/drawing diff.
- `scripts/selftest_skill_flow.py`: adds and fixes regression cases for keyword donor fallback, image resize rejection, body `图像...` prose, and transaction non-escalation.
- `references/rule-owner-map.json`: adds enforceable owner metadata, router anchor, required load modes, and selftest owners for the new rules.
- `FILE-ROLE-INDEX.md` and focused user-feedback/thesis rule files record the helper boundaries.

## Verification

- `py -3 -m py_compile scripts\repair_thesis_surface_format.py scripts\validate_thesis_mutation_transaction.py scripts\selftest_skill_flow.py`: PASS
- `py -3 -m json.tool references\rule-owner-map.json > $null`: PASS
- `py -3 scripts\selftest_skill_flow.py --quiet --fail-fast --case repair_thesis_surface_format_keyword_toc_template_donor_fallback_valid --case repair_thesis_surface_format_image_display_resize_without_manifest_rejected --case figure_manifest_image_word_body_paragraph_not_caption_valid --case transaction_image_word_body_text_no_manifest_valid --case figure_manifest_narrative_figure_reference_not_caption_valid --case figure_manifest_drawing_extent_changed_rejected --case transaction_drawing_extent_without_image_words_requires_manifest`: PASS
- `py -3 scripts\validate_skill_gate.py --skill-root .`: PASS
- `py -3 scripts\check_utf8_clean.py --root . --json`: PASS

## Residual Risks

- The current thesis review copy pass023 remains blocked and is not a final handoff candidate.
- A later pass024 must create a source/final-bound transaction, comment-resolution ledger, figure manifest evidence, and refreshed TOC/front-matter evidence before any acceptance claim.
- Live TOC conversion is still not proven by this maintenance case; static TOC repair must be explicitly recorded if used.
