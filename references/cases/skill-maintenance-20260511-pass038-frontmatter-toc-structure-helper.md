# Skill Maintenance Case: pass038 front-matter TOC structure helper

- date: 2026-05-11
- scope: canonical skill maintenance plus project review-copy repair for `D:\项目\校园异常行为检测研究`
- authorization: user granted default multi-agent authorization for this session
- no-original-overwrite: required; thesis outputs must be new review copies only

## Root Cause

Repeated thesis repair attempts failed because front-matter, TOC, abstract title style, body heading baseline, and reference-residue cleanup were handled by risky project-local or broad helpers instead of one bounded canonical helper with package-diff evidence.

The first pass038 run exposed a helper bug: `remove_toc_contamination()` pre-scanned for the TOC title and carried `toc_started=true` into the mutation loop, so paragraphs before the TOC title could be deleted. A second risk was that Heading1 baseline replay removed the chapter opener's existing `w:pageBreakBefore`.

A later pass038 audit found that deleting the old "为补足参考文献来源..." repair-note paragraph also deleted source body citations `[12]` through `[25]`. The canonical fix is to replace the repair-note wording and relocate the existing citation paragraph after the final pre-existing body citation, preserving the source citation marker runs and hyperlink anchors instead of treating the markers as disposable residue.

## Canonical Boundary

- owner rule: `FMT-TOC-002`
- owner file: `references/thesis/format-rules/front-matter-and-toc.md`
- helper: `scripts/repair_thesis_frontmatter_toc_structure.py`
- allowed operations: `toc-contamination`, `duplicate-page-breaks`, `abstract-style`, `heading1-baseline`, `reference-residue`
- allowed changed DOCX parts: `word/document.xml`, and `word/styles.xml` only when `abstract-style` adds a missing style
- forbidden changes: media, relationships, comments, tracked changes, headers, footers, figure captions, table bodies, bibliography entries outside the locked residue paragraph; citation marker runs in the locked residue paragraph must be preserved, not deleted

## Regression Coverage

- `case_repair_frontmatter_toc_structure_preserves_frontmatter_valid`
- `case_repair_frontmatter_toc_structure_same_path_rejected`
- `case_repair_frontmatter_toc_structure_unknown_operation_rejected`
- `case_repair_frontmatter_toc_structure_reference_residue_preserves_citations_valid`
- `case_transaction_drawing_index_shift_without_image_manifest_valid`
- existing negative guards rerun: `case_transaction_drawing_extent_without_image_words_requires_manifest`, `case_transaction_caption_adjacency_without_image_words_requires_manifest`, `case_transaction_media_diff_without_image_words_requires_manifest`, `case_figure_manifest_drawing_extent_changed_rejected`

## Validation

- `py -3 -m py_compile scripts\repair_thesis_frontmatter_toc_structure.py scripts\selftest_skill_flow.py`
- `py -3 scripts\selftest_skill_flow.py --case repair_frontmatter_toc_structure_preserves_frontmatter_valid --case repair_frontmatter_toc_structure_same_path_rejected --case repair_frontmatter_toc_structure_unknown_operation_rejected --quiet`
- `py -3 -m py_compile scripts\validate_thesis_mutation_transaction.py scripts\selftest_skill_flow.py`
- targeted drawing/media transaction selftests for index-only shift, extent mutation, caption-adjacency mutation, and media replacement
- targeted reference-residue selftest proving citation run preservation

## Remaining Risk

Rendered PDF and full protected-surface evidence still decide whether a project review copy is handoff-ready. A helper report showing limited ZIP-part changes is necessary but not sufficient for thesis acceptance.
