# Thesis Execution Contract

Use this file as the canonical execution-layer contract for thesis DOCX work.

Policy files define what a thesis run must satisfy.
This file defines how the run is allowed to touch a live manuscript.

## 1. Incident Freeze Override

- If a root-level file matching `INCIDENT-*-THESIS-LANE-FREEZE.md` exists and its status is `ACTIVE`, thesis lanes are audit-only.
- During that freeze, do not mutate thesis DOCX, thesis PDF, TOC fields, page numbering, headers, footers, or thesis helper scripts.
- During that freeze, do not promote new durable rules unless the current task is the skill-audit task itself.

## 2. Layer Split

Treat thesis execution as two layers:
- `policy layer`: formatting rules, evidence rules, acceptance rules, and routing files
- `execution layer`: document-path locks, tool ordering, serialized access, staging copies, and recovery behavior

Policy files must not override the execution-layer safety rules in this file.

## 3. Single-Document Access Rules

- one thesis manuscript path may have only one active write owner at a time
- do not run parallel `officecli`, Word COM, WPS, LibreOffice, PowerShell helper, or XML patch activity against the same DOCX path
- do not alternate between `officecli`, helper scripts, and office-application export on the same file path without an explicit close / reopen boundary
- if a tool may still hold the file open, treat the path as unavailable until a fresh reopen succeeds
- after any bounded `officecli` mutation group, verify that no lingering `officecli.exe` process still owns or blocks the DOCX before the next copy/export step
- do not build figure or screenshot insertion around mutating Word COM paragraph-chain guesses such as `InsertParagraphAfter(...).Next()` / `.Previous()` to find the image paragraph, caption paragraph, or explanation paragraph after each insert
- after a paragraph-creating mutation, treat nearby `Paragraph.Next()` / `Paragraph.Previous()` traversal as untrusted until the exact target paragraph has been re-identified by stable text, style, or heading-scoped structure on the reopened document
- when a helper script inserts a figure block, the block anchor must be locked by one verified local heading or other stable structural sentinel; do not anchor by broad prefix matches such as `7.3` across the full manuscript when multiple subsection paragraphs, TOC entries, or stale content can also match
- when a helper script locates body paragraphs, it must explicitly exclude TOC content-control paragraphs such as `w:sdt` / `InToc=True` zones; filtering only by a non-TOC style name or by loose heading text is not sufficient
- do not accept a figure insertion pass merely because the caption text and explanatory paragraphs were written; also verify that the intended local figure block still owns the image object itself on the exact target path
- minimum post-insert figure-block ownership check:
  - the image-holder paragraph exists immediately before the intended caption paragraph unless the approved sample uses another explicitly locked order
  - the intended local figure block contains an actual image object rather than only caption/explanation text
  - no newly inserted image object is stranded onto a later paragraph, later page, or unrelated block without its intended caption

## 3A. Multi-Document Parallel Runs

- Different thesis DOCX paths may be prepared in parallel only when each document has its own locked:
  - source manuscript path
  - review-copy path
  - staging DOCX path
  - rendered PDF path
  - page-image directory
  - evidence-record tree
- Do not let two different thesis documents share one implicit staging DOCX path, one rendered PDF path, or one acceptance/evidence sink just because they belong to the same higher-level run.
- Treat these as shared global tool surfaces even when the DOCX paths differ:
  - `officecli` resident open / close transitions
  - already-embedded image replacement
  - Word COM / WPS / LibreOffice export
- Unless the exact local toolchain has already been proven stable under parallel load, default those shared global tool surfaces to serialized execution across documents.
- If one document in a parallel batch hits a lock, unsupported mutation path, or residual-handle failure, quarantine that document's lane first:
  - release or recover its lock owner
  - reopen or rebuild that document from the last known-good review copy
  - do not let a failing document silently contaminate the acceptance state of the other documents
- After a parallel batch, rerun per-document audits on the exact final outputs rather than assuming that one document's success proves the others are safe.

## 4. Review-Copy Naming Contract

Every thesis mutation pass must lock all of the following:
- source manuscript path
- current review-copy path
- ASCII staging DOCX path for renderer handoff
- rendered PDF path
- page-image artifact directory

Naming rule:
- do not keep rewriting one long-lived review copy across many passes
- use a fresh review-copy filename for each mutation pass
- keep the renderer staging DOCX on an ASCII-only path

Minimum path pattern:
- review copy: `<run-root>\\review-pass-<timestamp>.docx`
- renderer stage: `<run-root>\\stage\\stage.docx`
- rendered PDF: `<run-root>\\stage\\rendered.pdf`
- page images: `<run-root>\\stage\\pages\\page-XXX.png`

## 5. Renderer Handoff Contract

- mutate only the review-copy path
- before renderer export, copy the review copy to the locked ASCII staging DOCX path
- renderer export must read the staging DOCX path, not the live review-copy path
- rendered-page review must be based on the staging PDF and page images from the same pass
- if a renderer export fails, do not keep reusing the same staging path blindly; create a fresh pass and record the failure

## 6. Lock And Recovery Rules

- if a copy into the staging DOCX path fails because the source DOCX is locked, stop and diagnose the lock owner first
- if a tool leaves the DOCX open after a failed mutation or export, do not continue with later steps on the same path
- after any failed pass, either:
  - reopen and re-inspect the review copy cleanly
  - or create a fresh review-copy file from the last known-good source
- do not classify a pass as successful merely because later copies or exports succeed on a different file

## 7. Integration Gate Requirement

Before a thesis DOCX workflow may be described as trustworthy, run the real integration gate:
- `scripts/run_integration_gate.py`

That integration gate must check at minimum:
- Chinese-path DOCX roundtrip
- serialized `officecli` mutation on a real DOCX
- renderer export through an ASCII staging copy
- page-image generation from the rendered PDF
- file-lock competition and recovery
- visible heading / keyword / page-number chain assertions on rendered output
- when the formula lane is in scope, equation-object survival plus rendered numbering-surface assertions on the exact output
- when tables are in scope, table-title adjacency, keep-with-next binding, and absence of table-title list/numbering residue
- when figures/images are in scope, image-holder safety plus actual DOCX image extent staying inside the page text area
- when references are in scope, bibliography entry count retention in addition to bibliography formatting and citation audit
