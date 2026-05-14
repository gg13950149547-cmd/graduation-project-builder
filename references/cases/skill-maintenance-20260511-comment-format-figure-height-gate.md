# Skill Maintenance Case: Comment Format And Figure Height Gate

- Date: 2026-05-11
- Scope: canonical graduation-project-builder skill maintenance plus the current project repair lane.
- Authorization: user authorized multi-agent collaboration in this conversation; read-only explorer agents reviewed DOCX issues, skill gaps, and script workflow while the controller made serialized skill edits.
- Root cause fixed: body figure paragraphs recorded width extents but not `max_extent_cy_emu`, so safe page-height occupancy checks could miss over-tall pictures. Comment-resolution rows also needed a regression case that treats missing detector binding as a successful rejection, not a failing selftest.
- Files changed: `scripts/thesis_figure_contract.py`, `scripts/selftest_skill_flow.py`, `FILE-ROLE-INDEX.md`, `DURABLE-RULE-PROMOTION-AUDIT.md`, this case record.
- Validation: `py -3 -m py_compile scripts/thesis_figure_contract.py scripts/selftest_skill_flow.py`; targeted selftests `comment_fixed_without_detector_binding_rejected`, `comment_anchor_restoration_authorized_valid`, `figure_manifest_inserted_extent_exceeds_page_height_rejected`, `figure_manifest_inserted_extent_exceeds_text_width_rejected`, `figure_manifest_vml_pict_extent_exceeds_text_width_rejected`, and `figure_manifest_header_footer_media_replacement_rejected`.
- Remaining risk: the current thesis DOCX still requires exact-output audits and a source/final-bound transaction before any repaired copy can be called final.
