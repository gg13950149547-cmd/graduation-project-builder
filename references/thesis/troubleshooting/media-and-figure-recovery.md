# Thesis Troubleshooting: Media And Figure Recovery

Use this file for media-preservation incidents, figure loss, screenshot authenticity, equation recovery, body-copy media damage, and figure clipping incidents.

## Enforcement Status

- Every rule in this file is mandatory when this file is loaded for the current recovery subtask.
- Apply this file together with `references/thesis/thesis-troubleshooting-log.md`.

## Existing DOCX Media Preservation Rule

- If a user restores an existing thesis `.docx` because images or screenshots disappeared, treat that as a media-preservation incident, not just a formatting bug.
- Common root cause:
  - repeated script-based paragraph deletion and insertion on the authoritative `.docx`
  - broad non-`officecli` whole-paragraph rewrites on field-bearing or media-bearing regions
  - rebuilding content structure without treating existing media anchors as immutable
  - using unzip or rewrite workflows without an explicit media-preservation constraint
- Correct recovery path:
  - stop using the polluted intermediate artifact
  - re-read the user-restored `.docx` as the new source of truth
  - preserve all existing images and media relationships
  - only apply conservative in-place text/style edits, preferably through targeted `officecli` operations
  - if new figures are needed, append them; do not replace existing images unless the user explicitly asks

## Existing-Image Replacement Failure Rule

- Replacing an already-embedded thesis image through a generic document edit API can silently rewrite `word/_rels/document.xml.rels`, drop `word/media/*` assets, or remap image targets incorrectly.
- If the thesis has an existing figure block that already works, do not use `officecli set ... --prop path=...` or any equivalent high-level image-replacement mutation as the default replacement path.
- Treat direct replacement of existing embedded images as a media-relationship risk surface, not as a normal formatting edit.
- Required safe replacement order:
  1. preserve the current `.docx` as the source of truth
  2. identify the existing image relationship id and target media part
  3. replace only the media binary while preserving the original relationship id and `Target`
  4. if size changes are needed, adjust only the drawing extent in `document.xml`
  5. verify that media count and image relationship count did not drop after replacement
- If image replacement causes media count reduction, new random relationship ids, leading-slash image targets such as `/media/imageX.png`, or Word/WPS display corruption, the replacement path is invalid and must not be reused.
- In short: for existing thesis figures, preserve relationships first, replace media second, and never let a convenience API rewrite image bindings blindly.

## Figure Validation Rule

- Missing figures are an unfinished state when chapter semantics imply figures should exist.
- Do not mark figure work complete when style visibly deviates from the template or approved sample.
- Do not use runtime screenshots where a design diagram is required.
- Do not use design diagrams where runtime evidence is required.

## Formula Validation Rule

- A visual text approximation is not a completed formula task when the requirement is a real equation object.
- A centered plain-text paragraph such as `F(P)=...`, `max J(P)=...`, or `R_local=...` does not become acceptable merely because it looks math-like in the rendered page.
- If Word or WPS automation inserts equations into the wrong location, stop batch insertion and switch to one-by-one verified insertion on a disposable copy.
- Only merge formula changes back after confirming:
  - the equation is a real object
  - the equation persisted after save
  - the position is correct
  - the style matches the template or approved sample

## Pseudo-Formula Recovery Rule

- If a manuscript contains text paragraphs pretending to be formulas, do not keep them as a temporary compromise once an equation-object path is available.
- Correct recovery order:
  1. identify every pseudo-formula paragraph by exact path or exact text
  2. insert a real equation object at the intended position
  3. verify the equation object is discoverable through equation-aware tooling
  4. remove the original text paragraph that was masquerading as the formula
  5. rerender the affected pages and confirm spacing did not collapse
- Do not stop after insertion if the old plain-text formula still remains in the manuscript; that state is still a failed recovery.


## Screenshot Authenticity Rule

- If thesis text says a figure is a screenshot, the figure must come from the real running program or a user-provided screenshot folder.
- If the program or screenshot asset is missing, stop and report the gap.
- Do not replace a required screenshot with a generated diagram or mock image and still call it a screenshot.

## Damaged Screenshot Rule

- A screenshot is not acceptable if it shows a loading skeleton, blank placeholders, broken component paint, clipped viewport fragments, or missing main content.
- Headless-browser export is not automatically trustworthy. If the captured image shows skeleton-state blocks or obviously incomplete rendering, treat the screenshot path as failed.
- In that case, do not keep inserting later screenshots from the same broken capture path just because files are being produced successfully.
- Correct recovery path:
  - stop the current screenshot automation path
  - for browser-based runtime pages, switch first to Google Chrome full-page capture through Chrome DevTools Protocol with explicit readiness checks
  - only fall back to another path if the Chrome DevTools route is genuinely unavailable
  - re-check the replacement screenshot visually before insertion

## Browser Screenshot Default Recovery Rule

- When the thesis requires a real browser screenshot and the current path has produced Streamlit skeleton pages, partial paint, broken charts, or clipped content, the default repair action is not to keep experimenting with blind headless export.
- The default repair action is:
  1. keep the real application running
  2. open the target page in Google Chrome
  3. wait until key text and chart elements are fully rendered
  4. capture a full-page screenshot through Chrome DevTools Protocol
  5. visually inspect the PNG before any thesis insertion
- Once this Chrome path is proven to work for the current project, treat it as the locked screenshot method for subsequent thesis runtime pages in the same run.
- Do not switch back to a previously failed screenshot method later in the same thesis run unless the user explicitly requests it.

## Caption And Explanation Adjacency Rule

- Figure acceptance fails when the image, caption, and required explanation paragraph are not kept together in the intended order on the rendered page.
- The intended default order is:
  1. image
  2. caption
  3. explanatory paragraph
- Table acceptance fails when the table caption and explanatory paragraph are detached from the table block or appear in reversed order.
- If a late edit causes the explanation paragraph to appear before the caption, or the caption to drift away from the image/table, treat that as a figure/table block failure rather than a minor formatting issue.

## Figure Caption Loss Regression Rule

- If user feedback reports missing figure names, detached captions, orphan images, or wrong page breaks after a thesis format pass, treat the previous format pass as a figure-lane regression, not as a local caption typo.
- Correct recovery path:
  1. invalidate any handoff that claimed the affected manuscript had passed figure or pagination review
  2. restart from the original manuscript or another clean approved source, not from the contaminated output
  3. create a fresh figure inventory from the exact DOCX package and reconcile all body drawings, visible figure captions, media relationships, and nearby figure references
  4. mark captions that contain only `图X-X` as incomplete even when the numbering is correct
  5. mark uncaptioned body drawings as blockers until they are either given a caption with a locked renumbering plan or explicitly removed/skipped with user-acceptable reason
  6. rerender every affected figure page and verify image, full caption, and explanation adjacency before the next handoff
- Do not repair this class of failure by broad body-style normalization, whole-document paragraph rebuilding, or a generic caption text search. Those paths can preserve media counts while still leaving the figure set semantically and visually broken.

## DOCX Body Copy Rule

- Copying raw XML blocks from one DOCX into another can lose or break image relationships.
- Prefer `officecli add`, `set`, `move`, `remove`, and targeted media-aware reconstruction before copying raw XML blocks between documents.
- If the target thesis must preserve inserted figures, rebuild body content by iterating paragraphs, tables, and images and reinsert images through the target document API.
- If image captions appear but images do not, suspect broken media relationships before suspecting the rendering tool.
- When rebuilding body content, empty-looking paragraphs may still carry semantic layout controls such as page breaks.
- Do not skip blank source paragraphs blindly; first check whether they contain page-break markers or other structural controls.


## Figure Clipped By Paragraph Line-Height Rule

- A figure can be embedded correctly in the DOCX and still fail visually because the image paragraph inherits body-text line-height constraints.
- Typical failure signs:
  - only a thin strip of the image is visible
  - only a corner of the figure appears
  - the caption is present but the figure body looks missing
- Correct recovery path:
  - inspect the paragraph that directly holds the inline image
  - remove body-text first-line indent and fixed line-height constraints from that paragraph
  - rerender the affected page immediately
  - keep the figure only after full-image visibility is confirmed

## Figure And Caption Indent Drift Rule

- A figure can remain visible while still failing layout review because the image-holder paragraph or caption paragraph keeps direct indentation or list residues from a former body/list paragraph.
- Typical failure signs:
  - the image block appears slightly shifted right although it is centered
  - the caption line looks centered but starts from an abnormal offset
  - the caption paragraph silently carries bullet or numbering metadata
- Correct recovery path:
  - inspect the real paragraph instance that holds the image
  - inspect the real caption paragraph instance
  - clear first-line indent, left indent, hanging indent, and list metadata explicitly instead of relying on style reassignment alone
  - rerender a representative figure block immediately after the cleanup

## Cover Stray Media Object Rule

- If the cover shows a mysterious image, selectable floating object, or non-template line object, inspect the first few front-matter paragraphs for `wp:inline` and `wp:anchor` objects instead of assuming the visible banner is the only media on the page.
- Distinguish legitimate institutional banner or logo media from accidental body screenshots or leftover floating objects before deleting anything.
- Prefer removing only the single stray media relationship while preserving the original namespace structure and all legitimate cover-media bindings.
- If the authoritative thesis file is locked by Word or WPS, first generate and validate a repaired copy, then overwrite the original only after the locking processes are closed.
