# Thesis Troubleshooting: Template And TOC Rebuild

Use this file for legacy template integration failures, annotation cleanup, TOC disappearance, and unstable foreground automation during rebuilds.

## Enforcement Status

- Every rule in this file is mandatory when this file is loaded for the current recovery subtask.
- Apply this file together with `references/thesis/thesis-troubleshooting-log.md`.

## Template Integration Rule For `.doc` School Files

- If the school provides a legacy `.doc` thesis template, convert it to `.docx` first and inspect the actual structure before writing content.
- Do not assume the template is only a cover page; many school templates contain:
  - cover/title pages
  - task book
  - proposal pages
  - midterm pages
  - qualification review pages
  - originality statements
  - abstract / TOC placeholders
- When integrating a finished manuscript into such a template, preserve the front administrative pages and replace only the thesis-body placeholder region.
- After rebuilding the template version, export to PDF and visually inspect pages. Structural validity in `officecli validate`, `python-docx`, or raw XML inspection alone is not enough.

## Template Annotation Cleanup Rule

- Many school templates contain instructional red annotations or callout shapes.
- After filling the template, remove instructional floating shapes from a working copy before delivery.
- Do not remove teacher-signature lines or form fields that must remain for later manual completion.

## TOC Survival Rule

- A thesis template rebuild is incomplete if the TOC disappears, even when all body chapters are present.
- Do not treat a manually typed fake TOC as equivalent to a real maintained TOC block.
- Use the canonical TOC rules in `references/thesis/format-rules/front-matter-and-toc.md` first, then use this section only for TOC-loss recovery and rebuild-specific incidents.
- After each template rebuild, explicitly verify:
  - the TOC title exists
  - the TOC body exists
  - the TOC appears before the abstract/body transition
- If a built-in TOC refresh changes the visible TOC typography or indentation, do not treat the refresh as complete.
- Restore the TOC title and every used TOC level from the locked local baseline in the same pass, then rerender and review the TOC pages again.
- If the rerendered TOC still differs from the school template, inspect whether the locked baseline was taken from the wrong source, especially the current draft's already-drifted TOC instead of the approved template/sample.
- Before any heading repair around the TOC, use `officecli get` / `query` to confirm the TOC block boundaries so heading logic does not spill into it.
- If the rebuild process trims placeholder body ranges, ensure the TOC page is reinserted after front matter and before the thesis body every time.
- If Word or WPS field automation is unstable in the current environment, prefer a stable template-conformant TOC reconstruction over a broken or missing auto field.
- The priority order is:
  1. visible TOC that matches template style and section order
  2. then automatic field behavior if the environment supports it reliably

## Legacy `.doc` TOC Baseline Rule

- When the school source arrives as `.doc`, convert it to `.docx` and inspect the template TOC before using any current thesis draft as a style reference.
- Do not assume the converted template TOC will expose a neat modern `sdt` block or rich `TOC 1/2/3` style definitions.
- Explicitly inspect:
  - TOC title paragraph class
  - TOC level 1/2/3 visible indentation
  - dotted-leader tab position
  - right-aligned page-number column
  - whether those metrics live in styles, direct paragraph formatting, or both
- If the template TOC depends on direct paragraph formatting, preserve and replay those direct metrics during restoration instead of only copying style names.

## Root-Cause Note Recorded For 2026-04-17 TOC Drift

- Incident:
  - the TOC content refreshed correctly, but the visible TOC still failed template alignment
- Root cause:
  - the restoration baseline was extracted from the current thesis draft's existing TOC, which was already visually non-template-aligned
  - the actual school template used a legacy `.doc` TOC whose visible look depended on paragraph-level direct formatting and a different right-tab position
- Corrective rule:
  - when the user reports TOC style mismatch, disqualify the current draft as the baseline source and re-extract TOC metrics from the school template or teacher-approved sample before the next pass

## Root-Cause Note Requirement For TOC And Pagination Incidents

- If a repair run breaks pagination, leaves TOC page numbers stale, or lets front matter drift into body formatting, write a short root-cause note before the next mutation pass.
- The note must identify:
  - the mutation class that triggered drift such as bulk paragraph rewrite, image insertion, or template merge
- whether section boundaries were rechecked afterward
- whether fields were actually refreshed or only marked dirty
- Do not treat "will refresh later" as an acceptable substitute for this note.

## Root-Cause Note Recorded For 2026-04-19 Sample-Clone Rewrite Pollution

- Incident:
  - a reference thesis was copied over the target manuscript to inherit layout
  - later bulk paragraph-string rewrites pushed target content into the borrowed sample shell
  - the visible TOC collapsed into one plain-text paragraph, sample footer literals survived, and front matter / body page separation drifted
- Root cause:
  - the run mixed content rewrite, front-matter repair, TOC rebuild, pagination repair, and footer-numbering repair inside one generic whole-document script
  - protected surfaces were not split into separate write owners
  - paragraph-structure-sensitive surfaces were rewritten as plain text instead of preserving paragraph boundaries, fields, tabs, and per-entry formatting
- Corrective rule:
  - do not start a sample-following rewrite by replacing the target manuscript file with a full reference-thesis clone unless the run is in an explicitly locked template-integration lane
  - keep TOC, front matter, pagination, and footer numbering read-only during body-content rewrite lanes
  - if a borrowed sample is used, extract paragraph metrics or explicitly locked regions from it, then write them back onto the target manuscript one protected surface family at a time
  - after any pass that touches TOC, front matter, or page numbering, rerender immediately and reject the pass if the TOC becomes one paragraph, if the first body chapter shares a TOC page, or if sample page-number/date literals remain visible

## Comment Cleanup Completion Rule

- Comment cleanup is not the default thesis-revision behavior. Review comments and tracked changes are preserved review artifacts unless the current user explicitly asks for a clean no-comment copy.
- A thesis comment-cleanup pass is incomplete if it only makes `officecli query <file> comment` return zero while leaving comment anchors or comment package parts behind.
- For a no-comments preview copy, verify all of the following on the same target file:
  - no visible review comments remain
  - no `w:commentRangeStart`, `w:commentRangeEnd`, or `w:commentReference` anchors remain in the body XML
  - no live `word/comments.xml`, `word/commentsExtended.xml`, or `word/people.xml` package parts remain
- The review-artifact-preserving source or deliverable copy must still be retained and audited unless the user explicitly requested that the comment-free copy replace all review copies.
- If the user screenshot still shows comments after an internal zero-comment check, first verify that the screenshot came from the same review-copy path before diagnosing the cleanup logic.

## Package Namespace Preservation Rule

- If a recovery pass rewrites package-level XML such as `[Content_Types].xml` or `word/_rels/document.xml.rels`, preserve the original namespace model including required default namespaces.
- Do not accept a rebuild pass that serializes those parts into a form that Word/WPS can no longer parse cleanly.
- After any package-level XML rewrite, reopen the DOCX with the active DOCX toolchain before proceeding to later repairs.

## Recurrent Thesis Failure Triage Order

When a user reports that the thesis still has multiple broad quality problems such as figure-style mismatch, abnormal global formatting, unexpected font colors, or insufficient manuscript length, do not diagnose randomly.

Use this troubleshooting order first:

1. figure-style compliance
2. global formatting surfaces
3. run-level color drift
4. thesis-length compliance

### Triage Step 1: Figure-Style Compliance

Check first whether structural figures and screenshots actually follow the approved sample, template, and figure-family rules.

Typical failure indicators:

- figures use a presentation style instead of the thesis sample style
- white-background academic figure rules were not followed
- internal text, borders, fills, or connector styles visibly drift from the accepted sample

If this step fails, do not continue into general formatting repair first. Fix the figure workflow and rerun figure review gates.

### Triage Step 2: Global Formatting Surfaces

If figures are acceptable, then inspect global formatting surfaces:

- front matter
- TOC
- chapter headings
- body text
- references
- acknowledgements

Treat this as a formatting-surface failure, not as a figure problem.

### Triage Step 3: Run-Level Color Drift

If the user reports abnormal font colors, do not stop at paragraph style names.

Explicitly inspect:

- heading runs
- body runs
- abstract runs
- TOC runs
- caption runs
- reference runs
- acknowledgement runs

If black-text thesis requirements are violated at the run level, treat that as a formatting failure even if paragraph styles look correct.

### Triage Step 4: Thesis-Length Compliance

If figure style, formatting surfaces, and run-level colors are acceptable, then verify manuscript length against the active thesis-length rule.

Do not treat a visually complete manuscript as acceptable when the body length still falls below the active minimum.

If thesis length fails, return to content production rather than trying to solve it with formatting-only work.

## Silent COM Validation Rule

- If template repair requires repeated format validation, do not keep opening the user's live document in the foreground.
- Use a fresh temporary ASCII-named copy, open it in background automation, and validate/export that copy.
- If the environment cannot provide stable background export, report that limitation explicitly rather than repeatedly hijacking the foreground WPS session.

## Rebuild Automation Stability Rule

- If a thesis rebuild script exits successfully but the official DOCX timestamp does not change, treat that run as failed even when no exception was raised.
- Before diagnosing TOC or pagination output, confirm that the generator script actually has an execution entry such as `main()` / `if __name__ == "__main__": ...` and that the official deliverable file was rewritten.
- For thesis front matter, do not use a continuous section break at the first body chapter when the TOC must stay on separate rendered pages from Chapter 1. Prefer a next-page section boundary or an equivalent structure-safe split.
- If WPS or Word post-processing reintroduces schema-breaking nodes such as `w:uiPriority` into `word/styles.xml`, add an explicit final package sanitation step and rerun structural validation before handoff.

## Additional Finalizer Ordering Note Recorded On 2026-04-13

- A thesis format-repair run is still incomplete if citation hyperlinks are repaired successfully in Word COM but a later COM save reintroduces schema-breaking style nodes such as `w:uiPriority`.
- Correct recovery order for mixed citation and style cleanup incidents:
  1. finish every Word/WPS COM mutation, including citation-hyperlink insertion
  2. run the package-level sanitation step last
  3. rerun structural validation on the official deliverable
- If a builder anchors the first body chapter by literal heading text, the heading regex must accept the project's actual numeric-heading spacing, including full-width ideographic spaces such as `1　绪论`, rather than assuming ASCII spaces only.

## Front-Matter Donor Replacement Rule Recorded On 2026-04-28

- If a cover page mixes a correct school name with a wrong logo, stale image description, or wrong-school metadata, treat it as a cover-format failure even when personal fields are explicitly skipped.
- The user may exclude personal fields such as student id, name, and adviser, but that exclusion does not automatically exclude cover structure, school identity, logo, declaration page, or abstract-page alignment.
- Correct recovery path:
  - replace the pre-abstract front matter from the approved template donor when the cover/declaration structure is contaminated
  - customize only non-personal project fields that are known from the project, such as thesis title, college, and major
  - leave skipped personal fields blank and record them as explicit skips
  - rerender cover, declaration, Chinese abstract, English abstract, and TOC pages after the donor replacement

## Root-Cause Note Recorded For 2026-04-30 Cover Table Field Pollution

- Incident:
  - the cover title content was present but rendered as a narrow vertical-looking wrapped block beside the `题目` label
- Root cause:
  - the canonical builder treated a two-column cover table row as a single label paragraph
  - title text was appended to the left label cell instead of being written into the adjacent value cell that owns the underline region
- Corrective rule:
  - when a cover field appears in a label/value table row, preserve the label cell and write the replacement value into the adjacent value cell
  - add a regression fixture proving the cover label cell stays unchanged while the title enters the value cell

## TOC Tab Extraction Rule Recorded On 2026-04-28

- In OOXML, TOC labels and page numbers may be separated by `w:tab` elements rather than literal tab characters in `w:t` text.
- A TOC audit that reads only `w:t` text can falsely report zero TOC entries or falsely pass the page-number column.
- Correct recovery path:
  - reconstruct visible paragraph text from immediate `w:r` children, preserving `w:tab` as `\t`
  - detect TOC entries by `w:tab` presence and manual TOC style, not only by literal `\t` in text nodes
  - compare the visible page-number column against a rendered PDF heading-page map after every TOC rebuild.

## Root-Cause Note Recorded For 2026-04-30 Static TOC Logical Page Offset

- Incident:
  - a canonical static TOC sync produced correct heading labels but wrong displayed logical page numbers, such as Chapter 1 pointing to page 5 while the rendered body footer showed `-1-`
  - tail blocks such as references and acknowledgement inherited the same offset error
- Root cause:
  - the static TOC updater selected the logical body start from every collected level-1 row
  - the rendered heading map can contain front-matter level-1 rows such as `ABSTRACT`, so the updater used the English abstract page as the body-page origin instead of the first numbered chapter heading
- Corrective rule:
  - compute static TOC logical page offsets from numbered body-heading candidates, not from generic collected level-1 rows
  - add a regression fixture with `ABSTRACT` as a front-matter level-1 row and require Chapter 1, references, and acknowledgement to map to the rendered body-footer sequence

## Root-Cause Note Recorded For 2026-04-30 Blank Pages And Fabricated TOC Geometry

- Incident:
  - rendered front matter contained unexpected blank pages between declaration, Chinese abstract, English abstract, and TOC
  - TOC visual-geometry evidence reported a pass even though the rendered TOC layout and page rhythm did not match the template
- Root cause:
  - the pagination structure parser wrote `blank_near_empty_page_scan_verdict: pass` from page counts only and did not inspect rendered page images for ink
  - the TOC geometry producer generated fixed-proportion row boxes, row counts, leader spans, and page-number columns from the crop rectangle instead of measuring the rendered TOC ink
- Corrective rule:
  - whole-document pagination evidence must include rendered page-image ink metrics, `template_blank_pages`, `actual_blank_pages`, `unexpected_blank_pages`, `actual_near_empty_pages`, and `unexpected_near_empty_pages`
  - TOC visual geometry must be measured from rendered ink-pixel row boxes; fixed-proportion or synthetic TOC geometry cannot support a pass verdict
  - add regression fixtures that reject an unexpected rendered blank page and reject TOC row-count/position drift measured from rendered TOC crops
