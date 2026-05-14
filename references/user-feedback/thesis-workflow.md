# User Feedback Persistence: Thesis Workflow

Use this file for durable thesis-workflow corrections learned through repeated thesis production and repair work.

## Enforcement Status

- Every numbered rule in this file is mandatory when this file is loaded for the current subtask.
- Apply these rules together with `references/user-feedback-persistence.md`.

## Thesis Workflow Rules

### FB-THESIS-001 (legacy 6). User-Facing Thesis Review Should Wait Until Content-Complete Draft (Mandatory)

- While producing a thesis under this skill, do not stop at an intermediate partial draft and ask for review by default.
- Continue writing until the manuscript is fully written to the current best content-complete state and only template formatting remains, then notify the user.
- This rule only delays user-facing handoff review. It does not weaken the mandatory paragraph-level rendered machine review and same-paragraph repair cycle during drafting or formatting.

### FB-THESIS-002 (legacy 7). Thesis Needs Real Screenshots And Clean Final Formatting (Mandatory)

- If the system can run, capture real page screenshots for the implementation chapter instead of relying only on schematic substitutes.
- Treat visibly mixed or chaotic final formatting as unfinished work, not as a handoff-ready state.
- For teacher-comment-driven revision rounds, convert the current comment document into an explicit execution checklist before editing.
- When one implementation subsection contains multiple runtime screenshots, convert that subsection into an explicit paragraph-to-screenshot pairing checklist before editing.
- For each paired item, verify the current manuscript uses:
  - the relevant explanatory paragraph block
  - the matching screenshot directly after that block
  - the matching caption directly after that screenshot
- Treat `all screenshots grouped at the subsection tail` as a workflow failure, not as a minor layout preference.
- Before handoff, re-verify each requested change against the current manuscript instead of assuming earlier rounds still satisfy the same issue.

### FB-THESIS-003 (legacy 8). Thesis Figure Generation Must Preserve Template Style (Mandatory)

- When revising or generating thesis figures, do not allow the DOCX formatting pass to destroy existing paper layout.
- Generated figure bodies must not include figure titles inside the image canvas.
- Figure captions must be placed as normal thesis caption text in a separate paragraph below the image.
- A formal figure caption only counts as a caption when it is bound to the immediate preceding image-holder paragraph. Prose that begins with a figure number, such as an explanatory sentence, must not be accepted as a caption surrogate.
- Structural figures must stay readable after DOCX insertion. A process chain, architecture diagram, rule logic diagram, or evidence-chain figure that is compressed below the structural minimum readable height is a figure-generation failure, even when it is not oversized.
- Before generating a new thesis figure, check the skill's stored figure-style references and follow that style instead of inventing a presentation-like style.
- If the user provides new figure samples, persist the learned style back into the skill in the same turn.

### FB-THESIS-004 (legacy 9). Unqualified Thesis Output Must Trigger Full Workflow Restart (Mandatory)

- If the user says the thesis output is still substantially wrong, do not continue with local DOCX patching only.
- Restart from the full graduation-project workflow:
- read the real project again
- verify the runnable system path
- run and debug the program if possible
- capture real system screenshots for thesis implementation chapters where possible
- rebuild the thesis from the original source document or template baseline
- perform stronger visual verification before returning the result
- Treat the absence of real code reading, runtime verification, or screenshot capture as an incomplete workflow when the project is runnable.

### FB-THESIS-005 (legacy 10). Repeated Table-Fix Complaints Must Escalate To Exact-Page Visual Review (Mandatory)

- If the user reports that a thesis table is still visually wrong after one repair round, do not continue with DOM-only inspection or property-level assumptions.
- Restart the table-fix workflow from the exact review-copy path:
- identify the exact table pages in the current manuscript copy
- export or render those exact pages
- inspect the rendered pages with machine vision before making the next edit
- treat any mismatch between DOM inspection and rendered-page appearance as a rendered-page truth override
- Do not hand off a second-round table repair unless the exact touched table pages have been visually rechecked after the latest edit.

### FB-THESIS-006 (legacy 11). Thesis Figure Readability Must Be Repaired Inside The Figure Before Any Manuscript-Level Page Change (Mandatory)

- If a thesis figure becomes unreadable after insertion, do not use Word page-size enlargement, page-orientation changes, or other manuscript-level layout changes as the default first fix.
- Default repair order:
  - enlarge the figure-internal font size
  - enlarge the relevant nodes, ellipses, diamonds, or actor labels
  - reduce local density and rebalance the internal layout
  - enlarge the useful content area inside the figure canvas
- Final DOCX display evidence must still keep structural figures at or above the canonical readable-width gate (`9.0 cm` by default) unless the active template or current user instruction explicitly locks a smaller width.
- Final DOCX display evidence must also keep ordinary runtime screenshots and UI/result images at or above the canonical readable gate (`8.0 cm` width and `4.0 cm` height by default) unless the active template/sample explicitly locks a smaller readable size.
- The `8.0 cm` and `9.0 cm` gates are readability floors, not target insertion sizes. By default, final body figures and screenshots must be inserted near the available body text width and align with the paragraph left/right margins; a visibly shrunken figure can still fail even when it exceeds the floor.
- Treat page-layout mutation as a last-resort path that requires one of:
  - an explicit current-user instruction
  - an explicit school-template requirement
- If a figure becomes legible only because the manuscript page was enlarged while the figure source itself remains too dense or too small, the figure task is still failing.

### FB-THESIS-007 (legacy 12). Structural Figure Review Must Include Dense-Zone Crop Inspection (Mandatory)

- For use-case diagrams, ER diagrams, flowcharts, and other connector-dense thesis figures, do not rely only on a full-figure zoomed-out inspection before insertion.
- After export and before DOCX insertion, crop and inspect every dense local zone that could hide:
  - actor-to-trunk junction errors
  - near-touching but unconnected shared lanes
  - local attribute overlap
  - connector-to-border penetration
- If a local crop reveals a defect that was not obvious in the full figure, treat the figure as failing and redraw the source before insertion.

### FB-THESIS-008 (legacy 12A). Do Not Call A Thesis Submit-Ready Based On Intermediate Artifacts (Mandatory)

- If the run produced multiple artifacts such as:
  - structure draft
  - review copy
  - final-format candidate
  - user-facing submission filename
  then the submission verdict must be tied only to the exact final named deliverable.
- Do not claim `可提交` from:
  - a structure-improved draft
  - a sampled PDF review
  - a DOCX that is not the final named submission file
- If only part of the final review is complete, report the artifact as:
  - intermediate
  - near-final
  - or still under review
  rather than as submit-ready.

### FB-THESIS-009. Teacher/User Figure Comments Must Become Figure Task Cards (Mandatory)

- During teacher-comment-driven or user-feedback-driven thesis revision, treat every comment that mentions figures, screenshots, charts, diagrams, flowcharts, ER/database diagrams, architecture/module diagrams, use-case diagrams, sequence diagrams, figure readability, wrong image, image order, caption mismatch, or redraw/replacement as a figure-lane trigger.
- Before manuscript mutation, convert each triggered item into:
  - one user-reported issue ledger row
  - one figure inventory row
  - one filled `assets/figure-task-template.md` task card
- The task card must carry the original comment id or source anchor, target caption/location, inferred family, selected sample/style source, required asset source, manifest entry id, pre-insertion evidence path, post-insertion rendered evidence path, and final verdict.
- A broad thesis rewrite, format repair, or chapter regeneration may not collapse these comments into a prose checklist item such as `redraw figures`. Each affected figure needs its own resolved pass/fail/skipped status.
- Final acceptance is blocked when a figure-related comment exists but the figure task-card path, figure plan path, asset manifest path, or per-figure review evidence path is missing or blank.

### FB-THESIS-010. Whole-Set Figure Defects Require Full Figure Redraw Closure (Mandatory)

- When user feedback says all figures, a figure class, or a figure set does not meet requirements, treat the feedback as a whole-set figure defect rather than a representative-sample issue.
- Before manuscript mutation, inventory every figure in the active thesis copy, including figure number, caption, chapter/location, embedded media relationship, current asset evidence, inferred family, replacement plan, task-card path, and final status.
- Every affected figure must be replaced, recaptured, or explicitly marked skipped with a user-acceptable reason. Do not accept old PNG reuse, screenshot existence, caption text, DOCX structural validity, or one representative redraw as proof that the set is fixed.
- Structural figures in the affected set must retain draw.io source, SVG export, PNG fallback, asset-manifest entry, relationship replacement evidence, and rendered-page evidence after DOCX insertion.
- Runtime screenshot figures in the affected set must be captured from the real running system or blocked with a recorded reason; schematic page mockups cannot satisfy screenshot slots.
- Final acceptance is blocked unless the exact final DOCX inventory proves all affected figure relationships point to replacement assets and the rendered output proves the inserted figures are readable, unclipped, and paired with their captions.

### FB-THESIS-011. Teacher/User Comments Require A Semantic Resolution Ledger (Mandatory)

- Before a teacher-comment-driven or user-comment-driven thesis mutation, inventory every `comments.xml` item, its `commentsExtended.xml` done state, anchor state, target surface, subissues, and current blocker status.
- Split multi-intent comments into explicit subissues such as front matter, TOC, pagination, figure size, figure crop/provenance, figure content/redraw, reference count, citation metadata, body rationale, or table/heading format.
- Do not mark a comment fixed merely because a nearby surface was touched, a local transaction passed, or the Word/WPS UI shows done. A fixed row requires evidence for the exact subissues named by the comment.
- Do not close comment rows with generic whole-document, full-format, or broad pass evidence when the comment names a specific intent. The detector evidence must expose intent-specific fields, such as figure extents for image-size complaints, crop evidence for screenshot complaints, explanation evidence for image-content complaints, table-vertical-border evidence for vertical-line complaints, risk-weight rationale evidence for weight complaints, and reference-count/English-count/2026-exclusion fields for bibliography-count complaints.
- Comments such as `same as above`, `ditto`, `同上`, or `同上述图片问题` inherit the immediately preceding concrete comment intent unless the ledger explicitly records a different reviewed intent. They cannot be closed as generic comments.
- If the run claims all comments are resolved, every comment id must have a ledger row with final status `fixed` or explicit user-approved disposal, evidence paths, and final DOCX/SHA binding.
- Comments with missing extension-state binding, orphaned anchors, changed teacher text, or unresolved sibling subissues stay open until the ledger and rendered evidence prove closure.
