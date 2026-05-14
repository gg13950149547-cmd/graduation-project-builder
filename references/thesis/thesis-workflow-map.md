# Thesis Workflow Map

Use this file as the single workflow router for thesis writing, whole-thesis revision, and local thesis repair.

## Enforcement Status

- Every thesis run must choose exactly one primary workflow from this file before mutation: `new-thesis-production`, `whole-thesis-revision`, `local-surface-repair`, `content-only-paragraph-revision`, or `audit-only`.
- The chosen workflow must be recorded in the active checklist, agent run manifest, task cards, and final acceptance record.
- This file owns workflow order. Format rule files own surface rules; scripts own executable checks; acceptance templates own evidence fields.
- If a run touches surfaces from multiple workflows, choose the broader workflow and record the narrower lanes as stage owners instead of improvising a mixed sequence.
- Every DOCX-writing workflow must also load `references/thesis/thesis-mutation-transaction.md` and pass the transaction validator before handoff. This workflow map selects the lane; the mutation transaction owns write locks, freeze/diff/render/regression evidence, and final DOCX SHA binding.

## Workflow Selection

### CORE-WFLOW-001. New Thesis Production Workflow Is Mandatory For Blank Or Rebuilt Manuscripts (Mandatory)

Choose `new-thesis-production` when the task asks to write a new thesis, rebuild a thesis from a template, regenerate a failed sample, or create a full manuscript from project facts.

Hard gates:

- lock the active school template or approved sample before any DOCX assembly
- generate or load a template profile before writing the manuscript
- use canonical skill scripts for generic DOCX assembly, figures, references, rendering, and acceptance
- project-local files may only provide adapter/profile/content/asset manifest data or thin wrappers
- do not hand off a new manuscript until DOCX, rendered PDF/page images, template profile, asset manifest, self-check, font/body/citation audits, and acceptance record all target the exact final output path

### CORE-WFLOW-002. Whole-Thesis Revision Workflow Is Mandatory For Broad Edits (Mandatory)

Choose `whole-thesis-revision` when the task changes many sections, claims whole-paper template alignment, repairs repeated formatting failures, updates references after content changes, or the user reports that multiple surfaces are wrong.

Also choose `whole-thesis-revision` for full-paper or comment-driven revision unless a preflight proves the target is a bounded local surface and no figure, table, citation, reference, TOC, pagination, review-artifact, or template-owned sibling surface is affected.

Repeated-defect feedback, "fix one thing and break another" feedback, or any body style / Normal / docDefaults / TOC / table / caption / heading / reference / acknowledgement / appendix / pagination style change is not an ordinary local repair. It must be routed as `whole-thesis-revision` or as a `local-surface-repair` transaction with explicit style-blast-radius evidence from `thesis-mutation-transaction.md`.

Hard gates:

- clone the current manuscript into one locked review-copy path before mutation
- lock the active template path, template fingerprint, template profile, source manuscript, review copy, and final deliverable path
- build a surface ownership map before editing, covering cover, title/front matter, abstracts, TOC, headings, body, body citation superscripts, review comments and change marks, figures, tables, citations, references, acknowledgement, appendix, header, footer, page numbers, and `whole_document_pagination`
- run staged repair in the order in `Whole-Thesis Revision Order`
- after each stage, render the affected page set and rerun stale audits for any surface whose evidence was invalidated by the stage
- final acceptance requires a page-class coverage matrix and surface-face parity rows for every present or user-reported surface
- if the source manuscript or comment-carrier DOCX contains comments or tracked changes, build a source-to-final review-artifact inventory before mutation and rerun it after mutation; a final copy may not silently lose comments, anchors, or tracked-change marks without an explicit user request and a separate clean preview artifact
- if comments, captions, prose, or generated assets mention figure/screenshot/chart/diagram work, activate the figure lane, load `references/thesis/thesis-figure-generation-rules.md`, and create per-figure inventory rows and task cards before mutation

### CORE-WFLOW-003. Local Surface Repair Workflow Is Mandatory For Narrow Fixes (Mandatory)

Choose `local-surface-repair` only when the user asks for one bounded surface family such as TOC font, reference entries, one table family, one figure block, one abstract page, header/footer, or one chapter-start pagination issue.

Hard gates:

- name the target surface, sibling surfaces, blast radius, donor source, and one write owner before mutation
- create and validate a transaction record before the first helper write
- use a fresh review copy; do not run whole-document style cleanup unless the local repair explicitly escalates to `whole-thesis-revision`
- render the exact touched page plus adjacent pages that can be affected by pagination, captions, fields, citations, or section breaks
- rerun the surface-specific audit and any stale global audit after the edit
- record the user-reported issue ledger row when the local repair responds to a user complaint
- if the local repair touches body style, Normal, docDefaults, TOC styles, table styles, caption styles, heading styles, references, acknowledgement, appendix, header/footer, or pagination, treat it as a style-blast-radius local repair and include TOC, table, reference, acknowledgement, appendix, pagination, and body-style regression detectors in the transaction evidence

### CORE-WFLOW-004. Content-Only Paragraph Revision Must Stay Run-Preserving (Mandatory)

Choose `content-only-paragraph-revision` only when the edit changes wording but does not intentionally touch layout, TOC, section breaks, citations, references, tables, figures, headers, footers, or pagination, and the comment/request/caption scan proves no figure-related work is present.

Hard gates:

- inspect each target paragraph for protected runs before editing
- scan DOCX comments, user feedback, figure captions, and nearby prose for figure/screenshot/chart/diagram tokens before entering this lane
- if the paragraph contains citations, keyword labels, mixed labels/content runs, inline figure/table references, or other protected runs, switch to the relevant local-surface workflow first
- if the scan finds figure, screenshot, chart, diagram, flowchart, ER/database, architecture/module, use-case, sequence, readability, wrong-image, image-order, caption-mismatch, redraw, or replacement signals, switch to `whole-thesis-revision` or a figure-focused `local-surface-repair` before editing
- use the paragraph-level rendered review cycle after every paragraph edit
- if line count or block height changes enough to affect pagination, temporarily switch to local pagination review before continuing

### CORE-WFLOW-005. Audit-Only Workflow Blocks Mutation (Mandatory)

Choose `audit-only` when the template is missing, risky project-local thick thesis scripts contaminate the lane, renderer output is unavailable, the active manuscript path is ambiguous, or a required workflow gate cannot be locked.

Hard gates:

- do not mutate the DOCX, PDF, TOC, page numbering, or helper scripts
- produce only diagnosis, evidence records, and next-step blockers
- do not describe the thesis as fixed, aligned, or ready

## Common Preflight

Every workflow except pure program-only work starts with this preflight:

1. classify the thesis workflow from `Workflow Selection`
2. load the required workflow, mutation transaction, format, user-feedback, agent, and execution references
3. create the agent run manifest; the audit lane alias is always `审核`
4. create the active checklist or task card for the chosen workflow
5. lock template/source/review/final paths, transaction record path, and expected evidence output paths
6. run project-local helper risk scan when a project directory is involved
7. build or load the template profile
8. build the surface ownership map
9. create the protected-surface freeze manifest before mutation
10. create the source review-artifact manifest and source body-citation run inventory before mutation
11. decide which audits will become stale after each planned stage

If any item cannot be completed, switch to `audit-only`.

Template-lock proof rule:

- File discovery is not template learning. A discovered specification/sample must be fingerprinted and profiled before mutation.
- The template discovery report, active template path, active template SHA256, and generated profile path must agree across the active checklist, format task record, role task card, and final acceptance record.
- If an existing repaired manuscript is already known to have lost format surfaces, use it only as a content reference. Do not inherit its styles, sections, TOC, page setup, or table geometry.
- If a user asks why a local format specification was missed, the next thesis run must start in `audit-only` until the template-lock proof above is recorded.

## New Thesis Production Order

1. Project fact intake: read the real project, run or inspect the runnable path, and collect factual evidence for chapters.
2. Template learning: lock the template, fingerprint it, and generate `template_profile.json` with page classes, same-page groups, donor surfaces, TOC structure, and tail-block expectations.
3. Blueprint and content manifest: build the thesis outline, chapter plan, humanizer routing evidence plan, citation plan, figure/table plan, and acceptance evidence plan.
4. Asset manifest: create figure/screenshot/diagram manifests through the canonical figure contract; structural figures must close draw.io/SVG/raster evidence before insertion.
5. Canonical assembly: use skill-owned builders for cover/front matter, abstracts, TOC, body, figures, tables, citations, references, acknowledgement, appendix, headers, footers, and page numbers.
6. Per-stage render review: after each content or surface stage, render the changed page region and run the required paragraph/page review before continuing.
7. Final audit chain: run citation audit, font/encoding plus bibliography font-slot audit, body-style audit, sample self-check, rendered page-class review, and final acceptance generation.
8. Handoff: only the exact final DOCX/PDF paths may be described as passing, and only when every blocking detector passes.

## Whole-Thesis Revision Order

1. Snapshot and review-copy lock.
2. Template and donor extraction.
3. Current-manuscript surface scan from cover through appendix.
4. Front matter structure and pagination repair: cover, title block, declarations, Chinese abstract, English abstract, and TOC separation.
5. Body structure repair: heading levels, chapter order, chapter starts, section boundaries, figure/table/caption adjacency, and body paragraph family.
6. Surface style repair by family: abstracts, keywords, headings, body, figures, tables, citations, references, acknowledgement, appendix, headers, footers, and page numbers.
7. Citation and bibliography finalization: normalize citation order, superscripts, bibliography count, paragraph metrics, mixed-script run font slots, and source policy.
8. TOC and field refresh: only after structure, headings, and pagination owners are stable.
9. Rendered full-page-class review from cover to appendix.
10. Review-artifact preservation review for comments, tracked changes, bookmarks, and citation run integrity.
11. Acceptance record, user-reported issue ledger, and audit lane verdict.

Do not run a later generic body/style pass across a surface already repaired by a narrower owner. If that happens, the run failed and must restart from the last clean review copy.

## Local Surface Repair Order

1. Identify one target surface family and its siblings.
2. Lock the exact source manuscript, review copy, active template/profile, donor instance, transaction record, and evidence paths.
3. Extract current target metrics and compare them to the donor before mutation.
4. Apply the smallest surface-owned edit.
5. Render the target page and blast-radius pages.
6. Run surface-specific detectors:
   - TOC: run/tab/leader/page-number/font checks and logical page sync
   - references: paragraph metrics plus every-run Chinese/Western font-slot checks
   - tables: title binding, table family, cell font, borders, width, and rendered readability
   - figures: asset manifest, source family, SVG-primary evidence, local caption/paragraph grouping, and rendered legibility
   - abstracts: title/body/keyword surfaces, prefix spaces, content runs, and page occupancy
   - headers/footers/page numbers: section links, visible top/bottom page review, and logical/physical page mapping
7. If a global audit becomes stale, rerun it before handoff.
8. Generate the post-mutation surface diff and cross-surface regression report.
9. Validate the transaction record.
10. Record the issue ledger row and acceptance evidence.

If the target repair reveals adjacent broken surfaces, stop the local workflow and reclassify as `whole-thesis-revision` before broadening the edit.

## Failure Loop

- A detector failure returns to the earliest stage that owns the failed surface.
- A missing donor returns to template learning or audit-only, not to guessed formatting.
- A stale audit returns to the stage that invalidated it.
- A rendered-page mismatch overrides XML, style-name, or checklist-only success.
- A multi-agent audit failure blocks handoff even if worker lanes report pass.

## Handoff Requirements

The final response or acceptance record must state:

- selected workflow
- active template/profile path
- source, review copy, final DOCX, final PDF, page images, and report paths
- required lanes and audit lane verdict
- passed/failed/skipped status for each required workflow stage
- exact blocking detector status
- whether the artifact is final, intermediate, or audit-only
