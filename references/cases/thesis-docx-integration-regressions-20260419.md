# Thesis DOCX Integration Regressions (2026-04-19)

Use this file as the incident fixture map for the 2026-04-19 thesis-lane instability review.

## Regression Fixtures

### RG-20260419-01

- visible failure: Chinese abstract title is partially missing, clipped, or compressed into the page-top region
- expected gate owner: integration gate
- minimum artifact set:
  - input DOCX
  - rendered PDF
  - page image for the Chinese abstract page
  - assertion record that the title text is still visible and centered

### RG-20260419-02

- visible failure: English abstract title or keyword styling drifts after later DOCX passes
- expected gate owner: integration gate
- minimum artifact set:
  - input DOCX
  - rendered PDF
  - page image for the English abstract page
  - assertion record that `Abstract` remains visible and that `Keywords:` is label-bold rather than whole-line corruption

### RG-20260419-03

- visible failure: TOC / Roman-Arabic page-number chain drifts across front matter and body
- expected gate owner: integration gate
- minimum artifact set:
  - input DOCX
  - rendered PDF
  - page images for Chinese abstract, English abstract, TOC, and first body page
  - assertion record for `I / II / III / 1`

### RG-20260419-04

- visible failure: references or acknowledgement title collides with the header zone, or a near-empty / blank page appears around the tail blocks
- expected gate owner: integration gate
- minimum artifact set:
  - input DOCX
  - rendered PDF
  - page images for references opener, references continuation, and acknowledgement opener
  - assertion record that the title block is visible, below the header line, and not accompanied by an abnormal blank page

## Coverage Rule

- text-gate coverage alone is not sufficient for these fixtures
- dummy zip DOCX fixtures are not sufficient for these fixtures
- a fixture is not closed until a real DOCX roundtrip with a real renderer reproduces it or proves it absent
