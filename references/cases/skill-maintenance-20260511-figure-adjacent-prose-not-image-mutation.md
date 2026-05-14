# Skill Maintenance Case: Figure-Adjacent Prose Is Not Image Mutation

## Trigger

A bounded body-prose repair rewrote explanatory text immediately before an existing figure. The DOCX media relationship, drawing extent, media hash, caption text, and caption adjacency remained unchanged, but the transaction and figure validators treated the changed preceding paragraph as an image/drawing mutation.

## Fix

- `scripts/validate_thesis_mutation_transaction.py` now ignores `previous_text` when deciding whether source-to-final drawing objects changed enough to require image-mutation routing.
- `scripts/thesis_figure_contract.py` now ignores `previous_text` for drawing authorization and source-to-final figure-surface preservation. Caption text and caption adjacency remain protected.
- `scripts/selftest_skill_flow.py` adds `transaction_previous_figure_prose_rewrite_without_image_manifest_valid`.

## Validation

- `python -m py_compile scripts/validate_thesis_mutation_transaction.py scripts/thesis_figure_contract.py scripts/selftest_skill_flow.py`: PASS
- `python scripts/selftest_skill_flow.py --case transaction_previous_figure_prose_rewrite_without_image_manifest_valid --case transaction_drawing_index_shift_without_image_manifest_valid --case transaction_drawing_extent_without_image_words_requires_manifest --case transaction_caption_adjacency_without_image_words_requires_manifest --quiet`: PASS

## Boundary

This does not allow figure edits without a manifest. Drawing extent changes, media changes, and image-caption separation still require image-mutation routing and fail without the required manifest evidence.
