# Thesis Format SOP

Use this file for thesis formatting execution order, tool routing, and high-risk repair workflow.

## 0. Enforcement Status

- Highest-priority format-repair rule: every paragraph-level thesis modification must be followed immediately by a rendered-page machine-vision review of that exact paragraph region before any later paragraph is touched.
- That immediate paragraph review must confirm:
  - local format compliance against the active template or sample
  - local content correctness, including that the paragraph still matches the real project and the subsection it belongs to
- The local format review must explicitly include:
  - font family
  - font size
  - font color
  - unexpected bold, italic, underline, highlight, or shading
  - abnormal blank lines
  - abnormal extra spaces, including stray ASCII spaces, full-width spaces, tabs, and mixed-spacing artifacts
- Do not queue multiple paragraph edits and review them later. Paragraph review is part of the edit itself.
- Every rule in this file is mandatory when this file is loaded for the current task.
- Treat the execution order, protected surfaces, and tool-routing constraints here as must-follow workflow rules.

## 1. Scope

This SOP applies when the task mode is:

- `thesis-only`
- `format-repair-only`
- `program-plus-thesis` after the program is already delivery-ready

## 2. Execution Order

Do not collapse format repair into one mixed pass. Use this order:

1. Baseline extraction
2. Structure repair
3. Pagination and field refresh
4. Style unification
5. Final review

Paragraph-edit execution rule inside this order:

- whenever a thesis paragraph is written, rewritten, reformatted, split, merged, or moved, insert an immediate local rendered-page check before proceeding
- the next repair action may begin only after that paragraph passes the machine-vision check for both format and content
- if a paragraph edit changes nearby page flow, review the changed paragraph and its immediate neighbors in the same local rendered pass
- if the paragraph edit increases or decreases local text volume enough to risk page-boundary movement, the same local rendered pass must also confirm whether a next-page spill, orphan heading, detached caption, or figure/table displacement has appeared
- if the changed flow occurs near a chapter transition, the same local rendered pass must also confirm whether the next chapter still opens cleanly on its own chapter-start page rather than being visually pulled into the prior chapter tail
- if the edit touches citation-bearing body paragraphs, superscript markers, bibliography numbering, or bibliography order, rerun `scripts/audit_thesis_citations.py` on the current review copy before the run can enter final review

## 2A. Format-Repair Preflight Lock

Before format repair starts, explicitly lock all of the following:

- active references for this run
- active checklist names for this run
- true current master manuscript path
- exact review-copy path for the next pass
- whether content is frozen
- paragraph-level rendered review path
- where rendered review evidence record files for touched pages will be stored
- where touched-page review evidence record files for blast-radius review will be stored
- which exact DOCX renderer executable has been verified for this run when rendered export is required
- when figures or captions are in scope, the figure inventory path, per-figure task-card directory, asset/source manifest path, and rendered figure-page evidence directory

Mandatory interpretation:

- if one of these is unknown, the format-repair run is not ready
- do not allow implicit skips for protected surfaces, rendering review, or review-copy management
- finding a school specification, thesis sample, or template-like DOCX in the project tree does not satisfy the baseline lock by itself
- the run must record the template discovery report, selected template path, selected template SHA256, generated template profile path, and the exact command or equivalent step that produced the profile
- if the active template profile was not generated before mutation, the lane is audit-only
- if any locked path in the checklist, task card, or acceptance record is visibly mojibake-corrupted, the path lock is invalid and the lane is audit-only until the record is regenerated with correct UTF-8 text
- a bad intermediate manuscript created by a failed format lane is never an approved baseline source unless the user explicitly approves it as content-only reference and the format lane records that it will not inherit its styles
- if figures or captions are in scope and the current DOCX has not been inventoried for body drawings, visible captions, media relationships, figure-name completeness, and rendered figure-block pagination, the lane is audit-only

Renderer-preflight rule:

- Do not mark `paragraph-level rendered review path` as unavailable until the run has completed renderer detection and one real export check.
- Renderer detection must distinguish:
  - Word COM failure
  - WPS availability
  - LibreOffice availability
  - total renderer absence
- Required detection order:
  1. inspect registry `App Paths`
  2. inspect uninstall entries and user-scope install locations
  3. inspect standard executable locations
  4. attempt one real export on a review copy with an available renderer
- If Word COM fails but WPS or LibreOffice succeeds, the run must treat rendered review as available and must not report a no-renderer environment.
- If no renderer succeeds after the full detection order above, only then may the run classify rendered export as unavailable.
- A successful `officecli view html` preview does not satisfy renderer preflight. The preflight is complete only after one real DOCX-to-PDF or equivalent renderer export succeeds and yields a page-image inspection path.

Header/footer and chapter-start lock:

- if the current repair touches header, footer, section boundaries, chapter-start pagination, or tail-block first pages, also lock all of the following before editing:
  - exact touched header/footer surfaces
  - the intended body-header strategy, such as section-local fixed text or heading-driven field
  - the intended tail-block strategy for conclusion, references, acknowledgement, and similar end matter
  - the exact tail-block title baseline paragraph instance for each touched tail block
  - the intended fresh-page owner for each touched tail block, such as a section boundary, a page-break-before title paragraph, or another approved template-owned owner
  - the physical rendered pages or the sentinel-text method that will be used to find them after export
  - whether the current document has visible numbering that differs from physical PDF page order
- if those header/footer lane locks are missing, the run is not ready even when the general preflight lock is complete

## 2C. Helper-Script Target Lock And Surface Ownership

Before any helper script, automation batch, or bulk mutation is allowed to write into a thesis DOCX, explicitly lock all of the following:

- exact helper-script target DOCX path
- expected output DOCX path after the script returns
- which protected surfaces the script is allowed to touch
- which protected surfaces the script must not touch
- whether any already-tuned custom-layout result tables must be excluded from the script
- whether heading / TOC / chapter-start surfaces are in scope for that script

Ownership rule:

- one protected surface family may have only one active write owner in the same pass
- do not let a later generic script rewrite a surface already owned by a narrower custom repair script
- if a generic script would overlap a custom surface owner, stop and split the pass instead of continuing

Target-path rule:

- do not let helper scripts resolve the target DOCX through `latest modified file`, wildcard review-copy matches, or temporary repair filenames unless that exact path has already been locked for the pass
- if multiple similarly named review copies exist, the run must choose one explicit canonical target path before any write step begins

## 2D. Post-Script Smoke Audit

After every helper script or bulk DOCX mutation, run an immediate smoke audit on the exact target path before the next edit step.

Minimum required smoke-audit checks:

- the DOCX opens successfully in the document toolchain
- the expected table count still matches the pre-script expectation
- the touched heading family still uses real heading styles where required
- TOC and bookmark-linked heading text did not silently drift
- touched table captions are still attached to the intended tables
- custom-layout result tables did not lose their width/font tuning to a later generic restyle

If any smoke-audit item fails:

- do not continue to pagination repair, style unification, TOC refresh, or handoff
- record the failure in the troubleshooting layer
- revert to one narrower repair surface before the next script pass

Front-matter sequencing rule:

- treat front matter, TOC, and main body as separate repair zones
- complete front-matter structure and pagination repair before body-style normalization
- do not let body cleanup scripts run across the cover, abstracts, or TOC block
- before any body-style normalization pass, explicitly lock the non-body exclusion set for that pass:
  - cover/title-page lines
  - declaration / commitment rows
  - figure-holder paragraphs
  - figure-caption paragraphs
  - table-caption paragraphs
  - cross-page continuation-title paragraphs for continued tables
  - table-cell paragraphs
- if a body-style pass changes one of those excluded surfaces anyway, stop the pass, restore that surface from its locked sample instance, and split the workflow before continuing
- rendered pagination inspection must start from the cover page and continue forward in page order; do not begin pagination review from the first body chapter while front matter is still unchecked

## 2B. Header/Footer And Review-Copy Workflow

Use this workflow when the repair touches:

- body headers
- body footers
- section-local header/footer linkage
- chapter-start page breaks that can change which header appears
- tail-block title pages such as conclusion, references, acknowledgement, appendix

Mandatory workflow:

1. extract the real accepted header/footer baseline from the local sample or approved manuscript
2. inspect section boundaries, header references, footer references, and chapter-start paragraphs before mutation
3. choose one body-header ownership strategy and keep it singular for the lane:
   - section-local fixed chapter headers
   - or heading-driven dynamic field headers
4. choose one tail-block ownership strategy and keep it singular for the lane:
   - dedicated tail-block sections with explicit visible headers
   - or an approved template-owned mechanism that is already proven on rendered pages
   - for each touched tail block, keep exactly one verified opener owner rather than a duplicate or implicit mix
5. perform the repair on a review-copy path first
6. export the review copy to a rendered format such as PDF
7. review the rendered page tops for:
   - the first touched body chapter page
   - at least one later touched body chapter page when the body header should vary by chapter
   - the page immediately before every touched tail-block first page
   - every touched tail-block first page
   - the continuation page for a touched references block when that block spans more than one page
8. only after those rendered pages pass may the run promote the review copy back to the master manuscript path

Header strategy safety rule:

- do not prefer a dynamic field strategy such as `STYLEREF` only because it looks cleaner in XML
- if the current renderer or local template may not resolve that field safely, prove it on rendered pages before relying on it
- if a field-based header renders as stale text, blank text, or `Error! Bookmark not defined.`, reject that strategy for the current repair lane and switch to a safer section-local strategy

Logical-versus-physical page rule:

- when the document has cover pages, front matter, roman prelim pages, or restarted arabic numbering, do not assume thesis-visible page `N` equals exported PDF physical page `N`
- map the rendered review targets by sentinel text or another explicit physical-page method before reviewing page images
- if the selected review image does not first prove it contains the expected sentinel text, the rendered-page review is invalid and must be redone
- Do not describe a review as machine-vision-complete if it inspected only HTML snapshots, DOM text, or XML state without page images from the rendered export.

## 3. Baseline Extraction

Before editing, read the real template or approved sample and extract the baseline for:

- cover
- front matter pagination
- TOC title and TOC entries
- heading levels 1 to 4 when those levels appear
- Chinese body text
- Chinese abstract title/body/keywords
- English abstract title/body/keywords
- figure caption
- table caption
- references
- acknowledgements

Mandatory sample-instance extraction set for template-driven repair:

- the first true body chapter title paragraph instance
- the first true body second-level heading paragraph instance
- one real figure-caption paragraph instance
- one real table-caption paragraph instance when tables exist
- one real continuation-title paragraph instance when the approved sample contains explicit cross-page continuation labeling
- the real body header paragraph instance
- the real body footer / page-number presentation instance when visible
- one real TOC title paragraph instance when a TOC exists
- one real TOC level-1 paragraph instance when a TOC exists
- one real TOC level-2 paragraph instance when a TOC exists
- one real TOC level-3 paragraph instance when a TOC exists

TOC baseline-source lock:

- when the current task includes TOC repair, record where each TOC sample instance came from:
  - school template
  - approved sample manuscript
  - accepted prior thesis copy
  - current working draft
- if the user has reported that the current draft TOC is visually wrong, the current working draft cannot be used as the TOC restoration baseline for that run

For each extracted paragraph instance, record at least:

- alignment
- line-spacing rule and actual line spacing
- space-before and space-after
- indentation
- font family
- font size
- font weight
- paragraph borders or other visible paragraph-level decorations when present
- for Chinese body paragraphs that contain inline English identifiers, API paths, formulas, or code-like tokens, also record:
  - the accepted run-level font pattern for Chinese text versus inline English text
  - whether the accepted sample keeps such paragraphs left-aligned or fully justified without visible stretching
  - one rendered sample page showing that this paragraph class does not produce abnormal word spacing

Do not begin heading, caption, or body-first-page repair until these real sample instances are extracted.

If the template shows a concrete pattern, do not replace it with a generic thesis assumption.

## 3.1 Content-Only Rewrite Lane

Use this lane when the task changes thesis wording or argument detail but does not intentionally target:

- TOC
- pagination
- section breaks
- tables
- figure placement
- figure internal style, figure replacement, screenshots, charts, diagrams, flowcharts, ER/database diagrams, architecture/module diagrams, use-case diagrams, sequence diagrams, image readability, wrong image, image order, caption mismatch, or redraw requests
- header/footer
- references layout

Before entering this lane, scan DOCX comments, user feedback, existing captions, nearby prose, and planned helper assets. If the scan finds figure/screenshot/chart/diagram signals, leave the content-only lane and route through the figure lane plus `whole-thesis-revision` or figure-focused `local-surface-repair`.

Mandatory content-only rewrite order:

1. clone the accepted manuscript into a fresh review-copy path
2. capture a package baseline for at least:
   - `word/document.xml`
   - `word/styles.xml`
   - `word/settings.xml`
   - `word/fontTable.xml`
   - `word/numbering.xml` when present
   - `word/header*.xml` / `word/footer*.xml` when present
   - `word/_rels/document.xml.rels`
   - `[Content_Types].xml`
3. inspect the target paragraph and identify protected run surfaces such as:
   - superscript citations
   - keyword labels
   - mixed bold/normal labels
   - inline figure/table references that already carry special run formatting
4. if the target paragraph already contains citations, bibliography-linked markers, or the pass would add, renumber, or rebuild any citation marker, stop the generic content-only lane and switch to a citation-aware workflow first
5. before any citation-bearing paragraph is rewritten, load:
   - `references/user-feedback/citations-and-bibliography.md`
   - and the active citation source-policy file such as `references/policy/cnki-citation-policy.md` when applicable
6. in that citation-aware workflow, do not materialize raw `[n]` markers directly into paragraph-source text or paragraph replacement strings; rebuild citations only through a path that also enforces one-sentence-one-source, first-appearance renumbering, and hyperlink-backed superscript behavior
7. apply the smallest run-preserving edit first
8. render the exact changed paragraph region and review both content and format
9. diff the package baseline
10. if the pass changed protected parts outside the expected scope, reject the pass and switch to a safer mutation path before doing more edits

Interpretation note:

- the numbered order above is gating order, not a license to continue with generic step 4 after a citation-bearing paragraph was detected
- if citation-bearing content is detected at step 4, the run must complete the citation-aware workflow before any content-only paragraph mutation continues

Content-only rewrite defaults:

- do not use whole-paragraph text replacement when the paragraph contains protected run surfaces
- if the pass still mutates text on a protected surface, replay the approved baseline instance for that exact surface on the post-edit paragraph or run structure before the run may continue
- after that replay step, rerun the surface-specific audit on the exact post-edit DOCX; any pre-edit audit is stale immediately once the paragraph text changes
- do not run whole-document `Fields.Update`, TOC refresh, repagination, or office-application save as a default content-pass tail step
- only run those global refreshes when the task explicitly includes pagination, TOC, or section-boundary repair
- however, a content-only rewrite lane is not allowed to ignore pagination if the actual paragraph changes alter local page flow
- when a content-only edit causes page-neighborhood drift, the run must temporarily switch into a pagination-sensitive local review lane and record:
  - which rendered page contains the edited paragraph
  - which adjacent page or continuation block was checked
  - whether a nearby heading, figure, table, or caption moved
  - whether the current run still avoids a global TOC/repagination refresh or now requires one
- if the drift occurs at or near a chapter boundary, that same record must also name:
  - the exact prior page before the chapter opener
  - the exact chapter opener page
  - whether the chapter title and the first body block beneath it still satisfy chapter-start expectations
- do not hand off a content-only rewrite pass while local pagination status remains unknown for any touched paragraph that materially changed line count or block height
- do not hand off a thesis pass while any touched chapter still lacks a chapter-start pagination verdict

## 4. Structure Repair

Repair structure first:

- chapter order
- section breaks
- page breaks
- TOC field presence
- caption and figure pairing
- table block order
- references / acknowledgements separation

Implementation-chapter screenshot reflow rule:

- if a subsection in the implementation chapter discusses multiple pages or modules with multiple screenshots, the stable repair order is:
  1. subsection lead-in paragraph
  2. page or module explanatory paragraph
  3. matching screenshot paragraph
  4. matching caption paragraph
  5. next page or module explanatory paragraph
- treat `all explanatory paragraphs first, all screenshots grouped later` as a structure failure even when every screenshot and caption exists
- when repairing this failure, move the explanatory paragraph block, screenshot paragraph, and caption paragraph as one local narrative unit instead of treating the screenshots as a later gallery block
- after each local reflow, run the required rendered-page review on the changed paragraph region and its adjacent screenshot/caption region before continuing

Treat front matter as a protected surface:

- cover
- Chinese abstract
- English abstract
- TOC

Do not mix front-matter repair with main-body repair in one pass.

## 5. Pagination And Field Refresh

After structure is stable, repair:

- front matter page numbering
- main-text page numbering
- chapter new-page starts
- TOC refresh
- field refresh
- rendered-page blank-page scan

Mandatory pagination gate:

- verify that front matter and the main body are separated by the required section boundary before refreshing the TOC
- verify that all pages before the abstract/TOC block remain unnumbered when the template treats them as cover/front-cover pages
- verify that the front matter uses the template-required numbering system, such as roman numerals when the sample shows roman numerals
- verify that the first main-body chapter restarts at arabic page `1`
- verify that the TOC displays those adjusted page numbers rather than raw physical page counts
- if the current pagination repair request is limited to chapter-level page breaks, explicitly lock whether the scope is:
  - first-level headings only
  - or first-level plus selected lower levels
- when the scope is first-level headings only, do not insert new page breaks before second-level headings during the same pass
- verify rendered page order from the beginning of the document:
  - cover page
  - Chinese abstract page(s)
  - English abstract page(s)
  - TOC page(s)
  - first main-body chapter page
- rerender and recheck every touched chapter opener page, not only the first main-body chapter page
- for every touched chapter opener page, also inspect the page immediately before it so the run can verify that the prior chapter tail does not leave an abnormal blank area, a stranded summary paragraph, or a visually collapsed chapter transition
- rerender and recheck every touched tail-block opener page and the page immediately before it
- for every touched tail block, verify both:
  - the rendered opener page still starts cleanly on a fresh page
  - the DOCX or office-application state still shows one intended opener owner rather than a lucky rendered coincidence with no durable owner
- if a tail-block title shares a page with the prior block, loses its verified opener owner, or depends on duplicate owners, treat pagination as failing even when later exported pages happen to separate the blocks
- when repairing the boundary from the English abstract into the first body chapter, inspect both the section break owner and the chapter-title paragraph itself:
  - if the chapter-title paragraph still contains an inline page-break run such as `w:br w:type="page"` or another forced chapter-start control after the body section restart has been moved, treat that as duplicated break ownership
  - keep exactly one verified chapter-start owner for that boundary before accepting the pagination pass
- if later body chapters are being split by page-break carrier paragraphs with attached `sectPr`, do not leave the first body chapter without its own verified page-start carrier:
  - otherwise a renderer may keep the first body opener on the English-abstract tail page even while later chapters render correctly
  - repair that case by restoring one explicit first-body page-start carrier before the first chapter title and rerun rendered review
- if the cover page already contains abstract text, or the abstract/TOC pages already contain body content, treat pagination as failing before checking later body chapters

If pagination changes later, re-check TOC and caption page references again.
If the blank-page scan finds abnormal blank pages, return to structure repair instead of continuing to style unification.

Mandatory TOC workflow inside the structure/pagination stages:

- generate or refresh the TOC first
- verify that the TOC contains only valid heading entries and no pulled-in body text or other pollution
- only after the TOC content is verified clean may the builder apply sample-derived TOC level formatting
- before any WPS/Word built-in TOC refresh, extract and lock the real local baseline for:
  - TOC title
  - TOC level 1
  - TOC level 2
  - TOC level 3
- also lock the visible TOC restoration metrics that will be restored after refresh:
  - title font / size / spacing
  - per-level indentation and line spacing
  - right-tab position and dotted-leader behavior
  - expected TOC rendered page count or occupancy rhythm
- do not assume a built-in TOC refresh will preserve those visible styles
- after every successful TOC refresh, restore the visible TOC formatting from the locked local baseline in the same pass
- this restoration must explicitly cover:
  - TOC title font, size, weight, alignment, and spacing
  - TOC level indentation
  - dotted leaders
  - right-aligned page numbers
  - level-specific font and spacing differences
- treat the office renderer's refreshed TOC as a content-and-page-number source only, not as a style baseline for the official manuscript
- do not transplant or replace the entire TOC `w:sdt` block from a Word/WPS/LibreOffice review copy into the official manuscript
- if TOC refresh is performed on a review copy, the official manuscript may inherit only the verified TOC content result and must still restore TOC title and TOC level styling from the locked local baseline inside the official manuscript
- do not accept review-copy TOC style ids such as application-generated `TOC1/TOC2/TOC3` as proof that the official manuscript now matches the local template when the approved baseline used different visible formatting
- do not allow front-matter page display drift from the approved local baseline during TOC refresh, including cases where an approved preliminary-page display is replaced by an application-generated fallback form
- if a TOC refresh leaves the TOC in default application styling, the refresh pass is still failing even when the heading text and page numbers are correct
- if the TOC content is dirty, return to structure repair instead of continuing into TOC visual tuning
- if the TOC content is correct but the restored TOC still shows compressed page occupancy, default app spacing, or the wrong rendered page count relative to the locked baseline, treat the TOC pass as failing and return to TOC restoration rather than handoff
- after any figure replacement, bulk paragraph rewrite, or combined screenshot insertion, re-check section boundaries, field state, and TOC page references before continuing
- if a script performs large content insertion or replacement, stop after structure repair and run a diff-style review before any TOC refresh or final pagination step

## 6. Style Unification

Only after structure and pagination are stable, unify:

- heading styles
- body text
- formula paragraphs and formula numbering surfaces
- figure paragraphs
- figure captions
- tables
- table captions
- references
- acknowledgements

Heading cleanup rule:

- when a body paragraph is promoted into a heading during restructuring, clear direct paragraph residues such as first-line indent, character-unit first-line indent, and body-text justification before finalizing the heading block

Formula-layout rule:

- when the active manuscript family uses chapter-based numbered formulas, treat the formula line as two coordinated surfaces:
  - centered equation object
  - far-right numbering surface
- do not stop after inserting or recovering the equation object if the number still sits only near the equation body
- if rendered review shows the number stopping short of the line end, repair the formula paragraph mechanics directly, such as restoring the template's center and right tab stops, before moving on
- do not allow generic body-paragraph insertion helpers, markdown replacement helpers, or `python-docx` plain-text paragraph builders to write displayed formulas into the official manuscript
- if an automation path still emits centered plain-text formulas such as `L = ...` or `N_t^c = ...`, treat that path as formula-unsafe and block it from thesis delivery until a real equation-object path replaces it

Mandatory full-table audit rule:

- when one or more real thesis tables exist, do not limit table review to `recently touched tables`, `recently edited tables`, or pages that were sampled for other surfaces
- before handoff, enumerate every body table in the exact review-copy path and record the total table count for the current run
- audit each table's border family against the active table sample or the active table-memory rule before relying on any rendered-page spot check
- treat `Word default full-grid borders with the same visible geometry on top, bottom, left, right, insideH, and insideV` as a hard failure when the target family is a thesis three-line table or a sample-derived border hierarchy
- generic issue scanners such as `officecli view issues` do not satisfy this table audit by themselves, because they may miss project-specific border-family failures
- after the border-family audit, render every page that contains a table and verify the visible border result on those exact pages before handoff
- when a table spans multiple rendered pages and the active sample/template uses explicit continuation titles for continued tables, render every continuation page and verify:
  - the continuation-title paragraph exists above the continued table fragment
  - the continuation title stays outside the grid
  - the continuation title keeps zero first-line indent instead of inheriting body-text indent
- if any one table fails the structural border audit or the rendered-page border audit, the thesis-format run is incomplete
- before bulk table repair, lock the active table sample source explicitly in this order:
  1. current user-provided table sample
  2. real local template table example
  3. accepted local manuscript sample
  4. stored fallback sample
- if a real local template table example exists, do not skip directly to a stored fallback sample
- when the active table family is still uncertain, repair one pilot table first, render it, compare it against the locked sample, and only then apply the same border family to the remaining tables

Prefer style-driven normalization first, and only use direct formatting for narrow exceptions.

Style-unification exclusion rule:

- do not let one global body-text normalization pass rewrite cover text, table-cell paragraphs, figure captions, table captions, code titles, code blocks, or continuation titles into the body baseline
- if those surfaces need repair in the same run, repair them as separate class-owned surfaces after the body family has already been stabilized
- after any global body-text normalization, run a surface-instance baseline check for every touched protected surface instead of relying on style names or border checks alone

## 7. DOCX Toolchain Default

Use `references/tooling-dependencies.md` as the canonical toolchain source for thesis `.docx` work.

Execution rule:

1. follow the high-level `officecli` path first
2. escalate to `officecli raw` or XML-level repair only when high-level operations cannot safely preserve the target structure
3. use application-render verification for final judgement

Do not default to `python-docx` when `officecli` can express the required mutation safely.

Renderer fallback rule:

- When rendered-page verification, TOC refresh, or DOCX-to-PDF export is needed, do not bind the workflow to Word COM alone.
- After a COM-path failure, continue through the verified renderer candidates for the current machine, including WPS and LibreOffice when installed.
- Do not report `no usable renderer` until the run has attempted the full renderer detection and verification sequence from `references/tooling-dependencies.md`.
- When a non-COM renderer succeeds, record that renderer as the active render path for the rest of the run and continue verification instead of downgrading the run to structure-only inspection.

For content-only thesis rewrite:

- default to run-preserving `officecli` edits first
- if high-level edits cannot preserve the target run structure, patch `word/document.xml` only
- treat office-application open/save as a verification or export step, not as the primary mutation path

## 8. OfficeCLI Routing

Use this default inspection set before repair:

- `officecli view <file> outline`
- `officecli view <file> text`
- `officecli validate <file>`
- targeted `officecli get` / `query`

Use XML-level mutation only after verifying that style- or DOM-level edits are insufficient, and keep that escalation aligned with `references/tooling-dependencies.md`.

## 9. Citation, Figure, And Table Routing

Load extra references by subtask:

- citations: `references/user-feedback/citations-and-bibliography.md`
- citations under source-policy constraints such as CNKI-only requirements: `references/policy/cnki-citation-policy.md`
- figures or screenshots: `references/thesis/thesis-figure-generation-rules.md`
- tables or borders: `references/thesis-table-style-memory.md`
- template-specific format behavior: `references/thesis/thesis-template-learning.md`
- troubleshooting: `references/thesis/thesis-troubleshooting-log.md`

## 10. High-Risk Defaults

- Cover must come directly from the approved template page, not from approximation.
- Front matter must be repaired separately from the body.
- Pages before the abstract/TOC block must stay unnumbered by default when they belong to the cover/front-cover area.
- Front matter and the main body must not share one final page-numbering section when the sample requires different numbering systems.
- Every major chapter should start on a new page unless the template explicitly says otherwise.
- Figure captions and table captions must remain standalone paragraphs outside the figure or table.
- Three-line tables should follow the stored table-memory rule unless the template explicitly overrides it.
- Final acceptance requires both document-internal verification and rendered-page verification.
