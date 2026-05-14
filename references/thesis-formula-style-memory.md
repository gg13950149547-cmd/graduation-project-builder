# Thesis Formula Style Memory

This file stores durable formula-style rules learned from user-provided thesis samples.

## Current learned style

- Formula blocks should appear centered on the page.
- Formulas should use a restrained academic math style, not presentation styling.
- Variables and metric names should appear in italic math style when the sample shows them that way.
- Fractions should use standard stacked fraction layout with a clear horizontal rule.
- Formula lines should keep generous vertical spacing between blocks to avoid crowding.
- Overall composition should stay clean and monochrome, with no decorative color or boxed background.
- Long formulas should remain visually balanced and centered rather than squeezed to one side.
- Formula numbering should follow the active template or accepted manuscript numbering family rather than an arbitrary automation default.
- When the template already uses chapter-based numbering, keep that numbering family. For this project family, accepted numbering looks like `(2-1) ... (2-7), (5-1)` rather than generic `(1) ... (8)`.
- Formula numbers should remain right-aligned as a dedicated numbering surface rather than being visually fused into the math expression itself.
- Formula numbers must sit at the far right end of the formula line in the rendered page, not merely appear after the equation with a small gap.
- Far-right formula numbering must still remain inside the usable page area. A right tab, formula table, or other numbering surface that extends past the right page margin is a hard layout failure even when the number is visually far to the right.

## Operational rule

- When the user provides a formula sample, treat that visual sample as the primary source for formula appearance.
- If the template does not define formula appearance clearly, use the stored default formula style in this file.
- Validate rendered formula appearance by visual comparison against the sample or template, not only by checking equation objects internally.
- Validate numbering style and numbering scope against the template or accepted sample separately from the equation object's internal correctness.
- If a formula is inserted into an existing thesis DOCX, verify both:
  - the equation is a real equation object or the template-approved equivalent
  - the visible numbering still matches the active template convention

## Hard Constraint

### FMT-FORMULA-001. Formula Authenticity Object Gate (Mandatory)

- Every standalone formula in a thesis DOCX must be a real Word equation object (`m:oMath` / `m:oMathPara`) or an explicitly approved equivalent recorded in the evidence. A paragraph that only looks like a formula through ordinary text, underscores, spacing, `x` multiplication, or right-side numbering is a hard failure.
- Do not invent or apply a generic formula style when an existing thesis template or user-provided formula image is available.
- Template and user-provided formula screenshots take precedence over every default remembered style in this file.
- If a generated formula does not visually match the template or sample, stop and revise; do not continue rolling formula edits through the manuscript.
- Do not use text-based fallback formulas that introduce encoding artifacts into thesis prose when the target document expects template-matching equation presentation.
- Do not silently replace template-style chapter numbering with flat document-wide numbering just because sequential numbering is easier to automate.
- A centered paragraph in Times New Roman or another math-like text font is still a failure if it only visually imitates a formula but is not a real equation object.
- Treat “plain text formula masquerading as equation” as a hard failure even when the visible glyphs look roughly acceptable in PDF export.

## Required default formula surface

- centered academic formula layout with italic math variables and stacked fractions
- template-matching numbering placement and numbering scope

## Additional formula lessons recorded on 2026-04-16

- Formula layout and formula numbering are separate acceptance surfaces; both must match the template.
- If the accepted manuscript already shows chapter-based numbering, preserve that numbering family during later insertions, reformatting, or equation-object recovery.
- A formula pass is still failing if the equations are real objects but the visible numbering changes from chapter-based numbering to generic sequential numbering.
- A formula pass is still failing if the numbering exists but does not reach the line's rightmost numbering position on the rendered page.
- A formula pass is still failing if the numbering reaches a hard-coded right edge outside the active section's usable width. Paragraph-tab layouts must compute the center and right tab stops from the active section page width minus margins, and table layouts must keep their total width inside that same usable width.

## Formula authenticity enforcement chain

- Run `scripts/audit_docx_formula_objects.py` on the exact final DOCX before acceptance generation; the JSON report must use schema `graduation-project-builder.formula-object-audit.v1`, bind to the final DOCX SHA256, and record `math_object_count`, `formula_like_paragraph_count`, and `pseudo_formula_count`.
- Final acceptance must carry `formula object audit evidence path` and `formula object preservation summary` whenever formulas or formula-like paragraphs are present.
- `pseudo_formula_count > 0` is a hard gate failure even if PDF export, screenshots, visible numbering, or centered paragraph styling look acceptable.
- The validator must re-audit the final DOCX instead of trusting the summary text, and selftests must include a fake-pass record where a plain text formula tries to claim formula-object success.

### FMT-FORMULA-002. Formula Lead-In Must Be Followed By A Formula Surface (Mandatory)

- A thesis paragraph ending with a formula lead-in such as `下式`, `公式`, `计算式`, `表示为`, or `定义为` plus a colon must be followed by a real formula object or an explicitly formula-like expression before explanatory prose such as `其中` / `式中`.
- If the next non-empty paragraph starts explanation text but no equation appears, the manuscript has a missing-formula defect, not a harmless wording issue.
- The repair options are: insert the intended formula as a real equation object with template-matching numbering, or rewrite the lead-in so it no longer promises a formula that is not present.
- `scripts/audit_docx_formula_objects.py` must report `missing_formula_after_leadin_count` and fail the exact final DOCX when this pattern is present.

## Additional formula lessons recorded on 2026-04-17

- Formula authenticity and formula appearance are separate acceptance surfaces.
- A formula task is not complete when the manuscript still contains centered text paragraphs such as `F(P)=...` or `R_local=...` in place of real equation objects.
- After repairing a pseudo-formula into a real equation object, verify both:
  - `officecli query ... equation` (or equivalent) can detect the equation object
  - rendered-page review still shows the formula at the intended location with correct spacing

## Additional formula lessons recorded on 2026-04-19

- In this local environment, WPS COM can detect `OMaths` successfully but may hang on fine-grained formula write operations such as numbering-surface edits.
- When that happens, a narrow `word/document.xml` fallback may be used for numbering-surface repair if and only if the run still preserves the real equation object.
- A locally verified fallback on 2026-04-19 converted one formula paragraph into a borderless three-cell table with:
  - left spacer cell
  - middle cell carrying the original equation object
  - right cell carrying the formula number
- This fallback is acceptable only when rendered-page review confirms all of the following together:
  - the equation object still renders as a real formula
  - the formula remains visually centered in the main equation surface
  - the number stays at the far-right numbering surface
  - the table borders remain invisible on the rendered page
- Do not treat this borderless-table fallback as self-proving. Its acceptance still depends on the rendered page rather than only on package structure.

If the template does not define a stronger fixed style, this stored formula sample is the default required formula reference for thesis completion.
