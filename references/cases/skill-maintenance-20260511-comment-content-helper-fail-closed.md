# Skill Maintenance Case: Comment Content Helper Fail-Closed

## Scope

- Date: 2026-05-11
- User trigger: repeated thesis/DOCX repair failures where comments, body spacing, English abstract/keyword surfaces, and image-size requests were not closed.
- Skill mode: `skill-maintenance` plus serialized thesis review-copy repair.
- Multi-agent status: prior six read-only agents completed; additional spawn was attempted during continuation and blocked by live-agent limit, so the controller recorded sequential fallback for the new cycle.

## Rule Promoted

`EXEC-MAINT-068` now also covers `scripts/repair_thesis_comment_content_surfaces.py` fail-closed behavior:

- Image/media/display-extent plan keys require `--source-docx`, `--transaction-record`, and `--figure-manifest`.
- Global `all_ascii_runs` English font repair requires a surface allowlist or explicit global authorization.
- Body paragraph format repairs require a unique anchor.
- Body paragraph format repairs must not target abstract, keyword, caption, TOC, references, acknowledgement, or other protected non-body surfaces.
- `scripts/repair_docx_picture_display_extents.py` must validate transaction binding to source DOCX path/SHA, intended output DOCX path, and figure manifest path before any image display-size mutation.

## Changed Files

- `scripts/repair_thesis_comment_content_surfaces.py`
- `scripts/repair_docx_picture_display_extents.py`
- `scripts/selftest_skill_flow.py`
- `references/user-feedback/maintenance-and-structure.md`
- `references/rule-owner-map.json`
- `FILE-ROLE-INDEX.md`

## Validation

- `py -3 -m py_compile scripts/repair_thesis_comment_content_surfaces.py scripts/repair_docx_picture_display_extents.py scripts/selftest_skill_flow.py` -> PASS
- Targeted selftests:
  - `repair_comment_content_media_requires_manifest_transaction_rejected` -> PASS
  - `repair_comment_content_global_ascii_requires_allowlist_rejected` -> PASS
  - `repair_comment_content_body_anchor_nonunique_rejected` -> PASS
  - `repair_comment_content_body_target_caption_rejected` -> PASS
  - `repair_comment_content_body_protected_surfaces_rejected` -> PASS
  - `repair_comment_content_ascii_allowlist_scoped_valid` -> PASS
  - `repair_comment_content_image_transaction_binding_rejected` -> PASS
  - `picture_extent_repair_requires_manifest_source_and_transaction` -> PASS
  - `picture_extent_repair_transaction_binding_rejected` -> PASS
- `py -3 -m json.tool references/rule-owner-map.json` -> PASS
- `py -3 scripts/validate_skill_gate.py --skill-root .` -> PASS
- `py -3 scripts/check_utf8_clean.py --root . --json` -> PASS

## Remaining Risk

This case closes helper bypass behavior. It does not by itself prove a specific thesis DOCX is final; the project run still needs final DOCX SHA-bound comment ledger, body-style audit, front-matter/English abstract evidence, figure/media delta evidence, citation preservation evidence, and acceptance record.
