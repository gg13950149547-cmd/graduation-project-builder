# Thesis Mutation Transaction

Use this file as the canonical workflow owner for every thesis DOCX write under this skill.

## Enforcement Status

- Every thesis DOCX mutation must enter one mutation transaction before any helper writes to the DOCX package.
- A single surface helper, Word/WPS automation step, canonical builder, field refresh, image replacement, table repair, or paragraph rewrite is not allowed to write directly unless this transaction record already exists.
- The transaction record is a gate artifact. If it is missing, stale, internally inconsistent, or fails validation, the run is `audit-only` or blocked and must not be handed off as fixed.
- The transaction validator is `scripts/validate_thesis_mutation_transaction.py`.

## CORE-TRANS-001. Thesis DOCX Mutation Must Be Transactional (Mandatory)

Before mutation, choose exactly one transaction workflow:

- `local-surface-repair`
- `whole-thesis-revision`
- `audit-only`

`new-thesis-production` and `content-only-paragraph-revision` from `thesis-workflow-map.md` still route through this transaction layer when they write a DOCX. The transaction record may store those as the selected thesis workflow, but it must also declare whether the write behaves as a local, whole-thesis, or audit-only transaction.

Required pre-mutation transaction locks:

- source manuscript path and SHA256
- active template path and SHA256
- review-copy path and pre-mutation SHA256
- planned final DOCX path
- target surface ids
- protected sibling surface ids
- review-artifact source inventory path
- source body-citation run inventory path
- one write owner for the mutation cycle
- audit owner or sequential audit fallback id

`protected_sibling_surfaces` is a freeze and regression scope, not a mutation-intent field. Listing `figure_table_captions_and_holders`, `toc_entries`, `header`, `footer`, or other protected siblings does not by itself authorize or imply a mutation to those surfaces, and it must not force the figure-manifest gate unless the actual target/operation fields or source-to-final DOCX package diff indicate an image mutation.

Required post-mutation bindings:

- final DOCX path and final SHA256
- evidence `final_docx_path` and `final_docx_sha256` values matching the exact handed-off DOCX
- final validator command and verdict bound to the exact acceptance record
- comment-resolution ledger path, audit report path, and verdict when the source or final DOCX carries teacher/user comments and the run responds to those comments

Do not invent a final SHA256 before the write. Do not delay transaction creation
until after the write just to fill post-mutation values. The transaction starts
with pre-mutation locks and closes only after post-mutation bindings pass.

## Required Evidence Schemas

Every mutating transaction record must include these named evidence records. Each record must bind to exact paths and SHA256 values for the DOCX or rendered artifact it claims to prove.

- `protected_surface_freeze_manifest`
- `post_mutation_surface_diff`
- `target_surface_render_review`
- `blast_radius_render_review`
- `cross_surface_regression_report`
- `review_artifact_preservation_report`
- `body_citation_run_preservation_report`
- `chapter_format_preservation_report` when any body chapter is touched or when the run carries a format-preservation promise

Local front-matter or keyword-only repairs may mark the chapter format detector as
`not-applicable-*` only when the transaction targets no body/chapter surface and
makes no whole-thesis or chapter format-preservation promise. This exception does
not remove the base transaction evidence requirements: freeze manifest, post
mutation diff, target render review, blast-radius review, and cross-surface
regression report are still mandatory.

Each named record must expose:

- `path`
- `sha256` when the artifact is a file
- `verdict`
- `final_docx_path`
- `final_docx_sha256`

The final transaction verdict can pass only when all named evidence verdicts pass and the `final_docx_sha256` matches the exact DOCX being handed off.

## Write Ownership

- Only one write owner may mutate the target surface during a transaction cycle.
- A local repair may not run a broad body style, Normal, docDefaults, TOC, table, caption, bibliography, pagination, or image cleanup pass unless the transaction is reclassified as whole-thesis or as a style-blast-radius local repair with explicit protected-surface freeze evidence.
- If another helper, renderer refresh, field update, or manual pass changes a non-target protected surface, the transaction fails unless the change is explicitly authorized in the transaction record and covered by post-mutation diff plus rendered regression evidence.
- If the run promises to preserve formatting, the transaction must record `format_preservation_promise_verdict`, `chapter_format_preservation_detector_verdict`, and `non_target_format_preservation_verdict`. Each must pass before the transaction can pass.

## Image Mutation Gate

An image mutation is any requested, inferred, or detected change to embedded DOCX media relationships, drawing bodies, picture holders, figure captions, screenshots, or generated figure assets.

A transaction must be routed as an image mutation when any of these are true:

- operation text contains English image terms such as `figure`, `image`, `picture`, `drawing`, `screenshot`, `insert image`, `replace image`, or `figure insertion`
- operation text contains Chinese image terms such as `图片`, `图像`, `截图`, `插图`, `绘图`, `图表`, `替换图片`, `替换图像`, `替换截图`, `插入图片`, `插入图像`, or `插入截图`
- the source and final DOCX image relationship manifests differ by relationship part, rid, target, or media SHA256, even if the task text says only `format repair`, `content cleanup`, `front matter repair`, or similar non-image wording
- the source and final DOCX drawing-object manifests differ by `wp:inline`/`wp:anchor`, `wp:extent` size, relationship id set, media signature, or adjacent caption/paragraph text, even when the embedded media bytes and relationship hash did not change

Every non-audit image mutation transaction must include and validate a figure asset manifest. The validator must pass the transaction source DOCX, final DOCX, and manifest path into `scripts/thesis_figure_contract.py::validate_figure_manifest`.

The figure asset manifest must bind the compared documents at top level with `source_docx_path`, `source_docx_sha256`, `final_docx_path`, and `final_docx_sha256`. A transaction field, task card, or acceptance summary cannot substitute for these manifest fields.

Every image mutation must record `target_anchor_not_protected_surface_verdict: pass` unless the transaction separately proves an official-template protected-image authorization. This proof is required for insertions, replacements, redraws, recaptures, and media changes inferred only from package diff.

If the source DOCX has media and the final DOCX removes, changes, or adds media without complete manifest authorization for the exact owner part, rid, target, and SHA256 on both original and final sides, the transaction fails.
If the source DOCX has drawing objects and the final DOCX changes their size, inline/anchor mode, relationship set, or caption adjacency without complete manifest authorization for the exact owner part and original/final drawing SHA256, the transaction fails.

## Review Artifacts And Citation Runs

Comments, tracked changes, bookmarks, hyperlinks, fields, and body citation superscripts must be frozen before mutation and diffed after mutation.

Comment preservation is separate from semantic comment closure. A comment-driven transaction must also include `comment_resolution_ledger_path` and validate it with `scripts/audit_thesis_comment_resolution.py` when it changes done states, claims comment completion, or responds to teacher/user comments.

A transaction fails when:

- a source comment part or body comment anchor disappears from the final DOCX without explicit user approval
- a comment done/resolved state changes without a fixed ledger row and explicit done-state authorization
- a transaction claims all comments are resolved while any ledger row is open, partial, blocked, missing, unknown, orphaned, or evidence-free
- a figure/comment row is marked fixed from size-only evidence while the source comment also requested crop, provenance, redraw, model structure, content correction, explanation, readability, or bibliography support
- tracked-change marks are accepted, removed, or rewritten without a recorded user request
- a bookmark, hyperlink anchor, field host, footnote/endnote anchor, or citation bookmark is lost as a collateral side effect
- a body citation marker that was superscript before mutation becomes plain body text, merged into a sentence run, underlined or blue hyperlink text, or otherwise style-damaged
- a citation audit report is reused after the final DOCX was overwritten and the report does not bind to the final DOCX SHA256

Citation hyperlink preservation is source-relative: if the source citation
marker has an internal hyperlink/bookmark host, the final marker must keep one.
If the source marker is already a plain superscript marker with no hyperlink
host, the diff must record that source condition and must not report the absence
as a newly lost hyperlink.

If the requested output is a clean no-comment copy, the transaction must record both outputs: the review-artifact-preserving copy and the no-comment preview copy. The no-comment preview cannot be promoted as the only final thesis artifact unless the user explicitly requested that promotion.

## Local Versus Whole-Thesis Claims

A `local-surface-repair` transaction may claim only local pass for the named target and protected siblings. It must not claim whole-thesis pass, full template alignment, `1:1`, ready-to-submit, or submission-ready status.

If a local repair needs to make or verify whole-document claims, reclassify the workflow as `whole-thesis-revision` before mutation.

A `content-only-paragraph-revision` or body-chapter rewrite is not allowed to claim format preservation unless the `chapter.format-preservation-contract` detector passes for the exact final DOCX and the transaction carries chapter-level diff plus rendered evidence.

## Style-Blast-Radius Escalation

Any change touching body style, Normal, docDefaults, TOC styles, table styles, caption styles, heading styles, references, acknowledgement, appendix, header/footer, or pagination must record a style blast radius.

The blast radius must include detector closure for:

- Chinese and English abstract plus keyword lines
- TOC title, entries, dotted leaders, and page-number column
- body heading levels and heading indentation
- body paragraph style binding and Normal/docDefaults preservation
- table titles, table cells, and rendered table family
- figure and algorithm-result provenance when figures are in scope
- references title and entries
- acknowledgement title and body
- appendix title and body when present
- whole-document pagination, blank pages, and near-empty pages

## TOC Page-Number Column Evidence

TOC page-number-column checks must use rendered page-number right-edge or right-boundary measurements. A detector or transaction record that uses dotted-leader start, leader x0, text-row start, or indentation as a proxy for the page-number column fails.

## Audit-Only

Use `audit-only` when a required lock, renderer, template, source manuscript, freeze manifest, or evidence route cannot be created. An audit-only transaction may diagnose and list blockers, but it must not write DOCX/PDF/page-image artifacts or claim a fixed manuscript.
