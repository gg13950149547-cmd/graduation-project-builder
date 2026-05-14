# Skill Maintenance Case - 2026-05-10 Sample Self-Check Source/Surface Binding

## Scope

- canonical skill root: `C:\Users\Administrator\.agents\skills\graduation-project-builder`
- project context: `D:\项目\校园异常行为检测研究`
- task mode: `skill-maintenance`
- thesis DOCX mutation in this case: no
- script mutation in this case: no
- write boundary: source-of-truth documentation, owner map, file-role index, durable audit, and this case record only

## Failure Pattern

- A sample self-check figure-contract call could bind source/final comparison to `reference_docx` instead of the manifest-bound `source_docx`, weakening source-to-final media and drawing checks.
- Body prose such as `图3-1展示了...` could be interpreted as a caption-like figure surface instead of a normal explanatory paragraph.
- Cover identity value-line detection could scan bibliography/reference legend rows such as `文献类型` and report a false cover-field failure.
- Image-dimension self-check output could be bypassed or softened by disabled/not-applicable wording while body images still existed.
- Abstract and keyword donor checks needed explicit coverage against TOC rows, template instruction notes, reference legends, red annotations, or self-donor aliases.

## Durable Rules Touched

- `EXEC-MAINT-068`: new canonical maintenance rule for sample self-check source/surface binding and detector false-positive prevention.
- `FB-LAYOUT-038`: caption detection must reject explanatory prose such as `图3-1展示了...`.
- `EXEC-MAINT-063`: figure contracts and sample self-checks must use manifest-bound source/final DOCX evidence.
- `FB-LAYOUT-070`: protected cover/front-matter donor families include cover identity value-line boundaries.
- `FMT-ABSTRACT-001`: abstract and keyword surfaces must keep clean template/reference donors and reject donor pollution.
- `QA-FINAL-050`: repeated thesis defects need named detector closure, including image-dimension disabled wording.

## Owner And Selftest Mapping

- `EXEC-MAINT-068` owner file: `references/user-feedback/maintenance-and-structure.md`
- `EXEC-MAINT-068` validators: `scripts/sample_self_check.py` and `scripts/thesis_figure_contract.py`
- `EXEC-MAINT-068` selftests: `case_sample_self_check_figure_contract_uses_manifest_source_valid`, `case_sample_self_check_figure_intro_reference_not_caption_valid`, `case_sample_self_check_cover_value_line_ignores_reference_legend_valid`, `case_integration_gate_image_dimension_valid`, and `case_integration_gate_abstract_self_donor_alias_valid`
- Existing rule owner mappings were extended for `FB-LAYOUT-038`, `FMT-ABSTRACT-001`, `QA-FINAL-050`, `EXEC-MAINT-063`, and `FB-LAYOUT-070`.

## Multi-Agent Record

- user note: the user stated this was a multi-worker maintenance round and instructed this worker not to revert others' changes.
- this worker role: controller/documentation maintainer.
- other worker outputs: treated as already-present script/selftest changes and case history; this pass did not inspect or revert their code edits.
- audit mode: single-controller documentation consolidation with no script mutation.

## Validation

- `py -3 -m json.tool references\rule-owner-map.json > $null`: PASS
- `py -3 scripts\selftest_skill_flow.py --quiet --fail-fast --case sample_self_check_figure_contract_uses_manifest_source_valid --case sample_self_check_figure_intro_reference_not_caption_valid --case sample_self_check_cover_value_line_ignores_reference_legend_valid --case integration_gate_image_dimension_valid --case integration_gate_abstract_self_donor_alias_valid`: PASS
- `py -3 scripts\validate_skill_gate.py --skill-root .`: PASS
- `py -3 scripts\check_utf8_clean.py --root . --json`: PASS

## Residual Risks

- This pass records rule ownership for existing detector/selftest work but intentionally does not modify scripts.
- Full suite runtime may remain longer than a single command budget; targeted detector cases are the expected proof for this documentation-only consolidation.
- If later workers rename selftest functions, `references/rule-owner-map.json` must be refreshed in the same maintenance turn.
