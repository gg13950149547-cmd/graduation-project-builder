# Thesis Layout Visual Memory

This file stores durable rules for thesis layout surfaces that must be validated by visual comparison with templates or accepted sample pages.

## Routing Note

- This file is the visual-comparison supplement for layout surfaces.
- It does not replace the canonical rule sources for thesis formatting, TOC structure, or front-matter repair.
- For canonical non-visual rules, use:
  - `references/thesis/thesis-format-sop.md`
  - `references/thesis/thesis-format-rules.md`
  - `references/user-feedback/template-and-layout.md`

## Covered surfaces

- cover
- title pages
- commitment letters / declarations / similar front matter
- TOC
- body text layout
- heading levels
- headers
- footers
- page numbers
- formula formatting
- acknowledgement formatting
- bibliography formatting
- table formatting
- figure formatting
- chapter and block order

## Core rule

- When the user provides a thesis template, sample thesis, screenshot, or accepted output page, use rendered visual comparison as the primary validation method for these layout surfaces.
- For cover pages, title pages, declarations, commitment letters, and similar front matter, judge the final result by visual comparison against the template page after the canonical front-matter repair rules have been applied.
- For formula formatting, use visual matching against user-provided formula samples or the template. If neither is explicit, use the stored default formula style memory.

## TOC rule

- If the template or accepted sample shows dotted leaders, they are mandatory.
- TOC completion requires all of the following:
  - correct heading coverage
  - correct indentation by level
  - dotted leaders when shown in the sample
  - right-aligned page numbers
  - visual distinction from ordinary body paragraphs
- Match the visual rhythm of accepted TOC samples, including title placement, hierarchy spacing, indentation, dotted leader density, and right-edge page number alignment.

## Learned TOC sample style

- The TOC title is centered and visually separated from the body.
- Top-level entries use larger visual weight than lower-level entries.
- Lower levels are indented clearly by hierarchy.
- Dotted leaders run continuously from entry text to right-aligned page numbers.
- Page numbers are aligned on the far right edge of the TOC block.
- The TOC should look clean, sparse, and highly regular rather than compressed.
- Chapter-level lines and subsection lines should preserve a clear hierarchy through indentation and font size rhythm.

## Additional required visual checks

- Verify that acknowledgement and bibliography visually match the template as independent blocks.
- Verify that the thesis block order matches the template or accepted sample before final delivery.
- If the template uses numeric superscript citations, check that citation numbers are visually superscript and avoid leaving multiple separate citation numbers attached to one sentence unit by default.
- If the template does not define a fixed TOC or layout style clearly, use the stored TOC sample and related layout samples as the fallback visual baseline after the canonical TOC rules have been satisfied.
- If the template or formatting-rules document does not define a surface clearly enough, compare against stored sample images for that surface before closing.
- Stored sample images should be treated as fallback visual authority, not as replacements for an explicit template.

## Validation rule

- Do not consider the job complete only because fields updated successfully or styles appear correct in DOCX internals.
- Compare the rendered pages against the template or accepted sample for spacing, alignment, font impression, line density, header/footer placement, and page number appearance.
- Validate TOC, body text, heading levels, tables, and figures as independent surfaces before the final pass.
- After independent checks are complete, perform one final visual comparison against both the template and the formatting-rules document.
- If the visual mismatch is still obvious, continue repairing.
