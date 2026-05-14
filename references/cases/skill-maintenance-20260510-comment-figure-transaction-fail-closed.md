# Skill Maintenance Case: Comment, Figure, And Transaction Fail-Closed Repair

## Context

- Date: 2026-05-10
- Scope: canonical `graduation-project-builder` skill bundle only.
- Project trigger: `D:\项目\校园异常行为检测研究`
- Failed evidence baseline: pass020 review copy was treated as a false pass because source/final comments drifted, figure changes were not fully authorized, and transaction records were not SHA-bound.
- User authorization: multi-agent collaboration was explicitly authorized in the conversation. Existing live read-only agents were reused; when aggregate suite runtime exceeded the single-command timeout, verification used sequential split batches and recorded that fallback.

## Changes

- `scripts/audit_thesis_comment_resolution.py`
  - Fails all-comments-resolved claims without source DOCX.
  - Rejects same source/final DOCX path.
  - Compares source/final comment text, done state, and anchor count even when no ledger is supplied.
  - Requires explicit approval evidence before comment disposal can explain a missing source comment.

- `scripts/audit_docx_review_artifacts.py`
  - Records comment anchors by story part, anchor type, and id.
  - Rejects source-to-final comment anchor count loss or missing anchor ids.

- `scripts/validate_thesis_mutation_transaction.py`
  - Requires SHA fields for non-audit source/final/template/review DOCX locks.
  - Rejects source/final path equality.

- `scripts/thesis_figure_contract.py`
  - Fails missing image relationship targets or missing media hashes.
  - Treats missing hashes as media changes.
  - Scans nested body/table/SDT/textbox paragraphs for front-matter and TOC drawings.
  - Rejects drawing extents wider than available text width.

- `scripts/generate_thesis_acceptance_record.py`
  - Restores default comment-resolution fields in generated acceptance output so figure-contract validation is reachable.

- `scripts/selftest_skill_flow.py`
  - Adds regression coverage for missing source DOCX, source/final same path, comment anchor loss, review anchor id drift, unapproved comment disposal, missing transaction SHA fields, source/final same transaction paths, missing final media target, over-wide inserted figures, and nested front-matter/TOC drawings.

## 2026-05-10 Caption Detector Follow-Up

- Trigger: the campus abnormal-behavior thesis pass exposed a false figure-contract failure where explanatory paragraphs such as `图3-1展示...` were counted as official captions.
- Fix: `scripts/thesis_figure_contract.py::is_docx_figure_caption` now requires a separator after the figure number, so only official caption forms such as `图3-1  标题` or `图3-1：标题` enter caption adjacency/count checks.
- Coverage: added `scripts/selftest_skill_flow.py::case_figure_manifest_narrative_figure_reference_not_caption_valid` and mapped it to `FB-LAYOUT-027` in `references/rule-owner-map.json`.
- Impact: figure-contract caption counts no longer double-count figure explanation paragraphs before or after an image block.

## 2026-05-10 Source-Preserved Front-Matter Image Follow-Up

- Trigger: the same thesis exposed a second false failure where official source-preserved front-matter images were reported as TOC/front-matter insertions.
- Fix: `scripts/thesis_figure_contract.py::final_docx_figure_surface_issues` now accepts a source DOCX and suppresses the front-matter drawing issue only when the exact drawing object is preserved from source to final.
- Coverage: added `scripts/selftest_skill_flow.py::case_figure_manifest_source_preserved_front_matter_image_valid` and mapped it to `CORE-FIGURE-006` / `EXEC-MAINT-063` figure fail-closed coverage.
- Impact: new or changed front-matter/TOC drawings still fail, but official source-preserved cover/front-matter images no longer block a valid thesis repair.

## 2026-05-10 VML And Acceptance-Gate Follow-Up

- Trigger: later review found two remaining false-pass routes: legacy VML/WPS `w:pict` images had no measured extent, and final acceptance could still omit source-bound comment-resolution audit evidence.
- Fix: `scripts/thesis_figure_contract.py` now includes VML/WPS picture shapes in the drawing manifest and rejects over-wide legacy pictures. `scripts/generate_thesis_acceptance_record.py` now requires `--comment-resolution-ledger` and writes a comment-resolution audit report when source or final DOCX carries comments.
- Fixture correction: `case_figure_manifest_docx_toc_insertion_rejected` now uses a source DOCX without the TOC image, so the negative test proves real insertion rather than a source-preserved official image.
- Coverage: added/ran `case_figure_manifest_vml_pict_extent_exceeds_text_width_rejected`, `case_acceptance_generator_requires_comment_resolution_audit_when_comments_exist`, `case_comment_resolution_ledger_claim_requires_source_docx_without_cli_assert`, and `case_comment_resolution_ledger_schema_missing_rejected`.
- Verification: after the fixture correction, `py -3 scripts/selftest_skill_flow.py --suite fast-thesis-records --quiet` passed with 75 cases.

## Verification

- `py -3 -m py_compile scripts\audit_thesis_comment_resolution.py scripts\audit_docx_review_artifacts.py scripts\validate_thesis_mutation_transaction.py scripts\thesis_figure_contract.py scripts\generate_thesis_acceptance_record.py scripts\selftest_skill_flow.py` PASS.
- `py -3 -m json.tool references\rule-owner-map.json` PASS.
- `py -3 scripts\check_utf8_clean.py --root . --json` PASS.
- `py -3 scripts\validate_skill_gate.py --skill-root .` PASS.
- `py -3 scripts\selftest_skill_flow.py --suite fast-core --quiet` PASS.
- New 12-case regression batch PASS.
- Existing related 13-case figure/transaction batch PASS.
- `py -3 scripts\selftest_skill_flow.py --suite fast-thesis-records --quiet` timed out at about 424 seconds; all fast-thesis-record cases then passed in four split batches.

## Remaining Risk

- This case hardens the canonical gates. It does not itself repair the project DOCX.
- pass020 remains failed evidence and must not be handed off as complete.
- The next document pass must start from a clean source/review copy, preserve all teacher comments unless disposal is explicitly approved, and produce a new source/final SHA-bound transaction plus figure manifest.
