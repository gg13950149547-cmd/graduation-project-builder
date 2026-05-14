# Skill Maintenance Case - 2026-05-10 Rendered Image Quality Gate

## Scope

- canonical skill root: `C:\Users\Administrator\.agents\skills\graduation-project-builder`
- project context: `D:\项目\校园异常行为检测研究`
- task mode: `skill-maintenance`
- thesis DOCX mutation in this case: no
- write boundary: canonical skill scripts, owner references, owner map, file-role index, durable audit, and this case record

## Failure Pattern

- A runtime screenshot or algorithm-result figure could pass by route, provenance, dimensions, and pass-shaped verdict fields while the rendered bitmap was actually blank, near-empty, a dominant solid-color block, or a purple placeholder.
- Size-only evidence could hide the bad rendered content because previous checks emphasized pixel dimensions and path existence.
- Related previously covered gates remain in force: figure comments with non-size requirements cannot be closed by size-only evidence; structural figures require draw.io/SVG/raster and reject Mermaid/PIL final sources; front-matter/TOC images are blocked unless source-preserved; abstract/keyword donor pollution is rejected by sample self-check and protected-surface gates.

## Durable Rules Touched

- `FB-LAYOUT-025`: runtime screenshot slots now require visual content, not only a caption-route-asset map.
- `FB-LAYOUT-029`: current screenshot asset checks must include rendered content quality, not file name or dimensions only.
- `CORE-FIGURE-004`: algorithm-result authenticity now includes bitmap visual quality for blank, solid-block, and purple-placeholder results.
- Existing `EXEC-MAINT-064`, `CORE-FIGURE-006`, `CORE-FIGURE-007`, `EXEC-MAINT-062`, `EXEC-MAINT-063`, `EXEC-MAINT-068`, `FMT-ABSTRACT-001`, and `QA-FINAL-050` mappings already cover the other requested failure families.

## Owner And Selftest Mapping

- validators: `scripts/thesis_figure_contract.py::validate_runtime_screenshot_entry`, `scripts/thesis_figure_contract.py::validate_algorithm_result_entry`, and `scripts/thesis_figure_contract.py::_image_visual_quality_issues`
- new selftests: `case_figure_manifest_runtime_screenshot_blank_render_rejected` and `case_figure_manifest_algorithm_result_purple_placeholder_rejected`
- owner map updated: `CORE-FIGURE-004` and `FB-LAYOUT-025`
- file role index updated for the new rendered image quality detector

## Validation

- `py -3 -m py_compile scripts\thesis_figure_contract.py scripts\selftest_skill_flow.py`: PASS
- `py -3 -m json.tool references\rule-owner-map.json`: PASS
- `py -3 scripts\selftest_skill_flow.py --quiet --fail-fast --case figure_manifest_runtime_screenshot_blank_render_rejected --case figure_manifest_algorithm_result_purple_placeholder_rejected --case figure_manifest_runtime_screenshot_full_window_valid --case figure_manifest_algorithm_result_real_provenance_valid --case figure_comment_size_only_false_pass_rejected --case figure_manifest_structural_mermaid_final_source_rejected --case figure_manifest_docx_toc_insertion_rejected --case figure_manifest_source_preserved_front_matter_image_valid --case protected_keyword_label_run_contains_content_rejected --case sample_self_check_rejects_template_donor_keywords_in_abstract_surfaces`: PASS
- `py -3 scripts\validate_skill_gate.py --skill-root .`: PASS
- `py -3 scripts\check_utf8_clean.py --root . --json`: PASS

## Residual Risks

- The visual-quality detector intentionally samples raster content and fails obvious blank/solid/purple placeholders; it is not a semantic OCR or UI-completeness model.
- Full fast-suite runtime may be longer than a single maintenance command budget; targeted cases are the expected proof for this gate.
