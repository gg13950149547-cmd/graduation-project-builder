# Thesis Troubleshooting: Recovery Basics

Use this file for baseline failure-recovery behavior, numbering collisions, style-name false positives, anchor targeting, and console-encoding recovery.

## Enforcement Status

- Every rule in this file is mandatory when this file is loaded for the current recovery subtask.
- Apply this file together with `references/thesis/thesis-troubleshooting-log.md`.

## Stable Recovery Rules

- Thesis content and deployment manuals are separate deliverables.
- Keep one authoritative manuscript source and rebuild from clean sources when output drifts.
- Use Unicode-safe scripts for Chinese-heavy Word generation.
- Verify image embedding directly instead of assuming insertion succeeded.
- Prefer rebuilding over repeated patching when a DOCX becomes visibly polluted.
- Match figure insertion by stable heading or numbering anchors, not fragile paragraph positions.
- Prefer real system screenshots when the program can run.
- Insert only real core code excerpts from the actual codebase.
- Re-check against the latest accepted artifact after each major thesis-edit batch.
- If a paragraph-level content repair later exposes a pagination problem, treat that as a workflow miss rather than as a harmless late-format detail; tighten the active SOP before the next pass instead of merely patching the current page.

## Numbering Collision Rule

- If a thesis rebuild shows duplicated heading numbers such as `2.4 4.4 ...`, first check whether numbering is being applied twice:
  - once in the literal heading text
  - and again by template heading styles or numbering definitions
- Fix by letting exactly one layer own numbering.
- In template-following work, prefer pure heading text plus template numbering, rather than hardcoded numbered text plus heading styles.

## Style-Name False Positive Rule

- A paragraph having the expected style name is not sufficient proof that its final format matches the template.
- Common failure pattern:
  - the paragraph style definition looks correct
  - but the real approved sample paragraph still differs because of direct formatting, page-level positioning, header/footer behavior, or paragraph-instance overrides
- Correct recovery path:
  - extract the approved sample's real paragraph instance
  - compare the rendered result rather than only the style name
  - rewrite the target paragraph from the sample instance when needed
- Apply this especially to:
  - first-level chapter titles
  - second-level headings
  - figure captions
  - table captions
  - headers and footers

## Anchor-Targeting Rule For Continuing DOCX Revisions

- Once a manuscript has gone through several expansion and trimming rounds, fixed paragraph indices are no longer safe for production edits.
- Use `officecli query` / `get` on heading text, style, and nearby structure before falling back to index diagnostics.
- Preferred targeting order:
  1. exact section heading text such as `结束语`, `致  谢`, `参考文献`
  2. unique leading sentence of the target paragraph block
  3. only then temporary index-based diagnostics
- Do not treat broad prefix probes such as `7.3` or other partially matching heading prefixes as sufficient figure-insertion anchors when the document also contains TOC entries, stale subsection text, or earlier copied blocks.
- When a body-targeting script says it is searching `正文段落`, verify that it truly excludes TOC content-control paragraphs such as `w:sdt` / `InToc=True` rather than only excluding a few visible TOC style names.
- Do not trust `Paragraph.Next()` / `Paragraph.Previous()` immediately after a mutating insert as proof that the next COM paragraph is still the intended image-holder, caption, or explanation paragraph.
- Correct recovery path for figure-block insertion:
  - reacquire the target block from a verified heading-scoped sentinel on the reopened document
  - verify that the intended caption-adjacent local block actually contains an image object
  - if the image object drifted elsewhere, rebuild that local figure block from the clean source instead of continuing to patch later paragraphs around it
- If a content script still depends on fixed indices, treat it as a fragile one-off and refactor it before the next revision round.

## Pagination-Miss Recovery Rule

- A thesis run has failed its execution discipline if it rewrites body paragraphs, confirms local text content, but does not explicitly verify whether nearby page flow changed.
- Typical failure pattern:
  - the rewritten paragraph itself looks correct
  - but the extra lines push a nearby heading, figure, caption, or table onto another page
  - the run notices the issue only in a later human review
- another failure pattern is chapter-boundary blindness:
  - local page-neighborhood review was performed
  - but the page before a touched chapter opener and the chapter opener page itself were never reviewed as a pair
  - the result is a visually broken chapter transition that should have been caught by chapter-start review
- Correct recovery path:
  - record the miss as a workflow failure, not just as a document defect
  - identify the first edited paragraph that changed page flow
  - rerender the edited page plus its immediate page neighbor
  - inspect whether headings, figures, captions, tables, or chapter openers moved
  - if a chapter boundary is involved, rerender the prior page and the chapter opener page together and record a chapter-start verdict
  - if local reflow is now part of the active risk surface, promote the remaining pass into a pagination-sensitive lane before making more content edits

## Console Encoding Rule For Chinese Thesis Repair

- Shell or console text injection is not encoding-safe enough for Chinese DOCX repair by default.
- Typical failure sign:
  - Chinese text written into the document as a string of question marks
- Correct recovery path:
  - repair the corrupted line immediately
  - move the text source into a UTF-8 Python script or use Unicode-escaped strings
  - do not continue adding content through raw terminal literals after the first corruption signal

## Style Id Collision Recovery Rule

- A DOCX may already contain a style id that matches the template style id but belongs to the wrong style type, such as a target `a2` table style colliding with the template `a2` paragraph style.
- Do not treat "style id exists" as proof that a template paragraph style has been imported.
- Correct recovery path:
  - inspect `word/styles.xml` for both `w:styleId` and `w:type`
  - when a template-owned paragraph surface needs that id, replace the wrong-type target style definition with the approved template definition inside the repair copy
  - rerun a paragraph-style audit on real body paragraphs, not only on the style catalog
- Apply this especially to imported body styles, abstract styles, TOC styles, and heading styles.

## Citation Anchor Drift Rule

- Fixed paragraph-index citation insertion becomes unsafe after cover, declaration, abstract, or TOC pages are inserted, removed, or rebuilt.
- If front matter is changed before citation insertion, recompute citation targets from verified body paragraph style and content anchors.
- Citation insertion must explicitly exclude:
  - TOC entries
  - headings
  - figure and table captions
  - blank paragraphs and image-holder paragraphs
- After insertion, rerender the TOC and confirm no citation markers leaked into visible TOC labels.
