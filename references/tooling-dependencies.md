# Tooling Dependencies

Use this file to decide which tools and capabilities the skill should rely on for each subtask.

## 1. Program Verification

Minimum live checks should prefer the narrowest meaningful path first:
- startup command
- main route or main page
- one core business flow
- one admin flow when applicable
- one analytics/reporting flow when applicable

Always record checks as passed / skipped / failed.

## 2. Diagram And Figure Tooling

Preferred diagram toolchain for thesis structural figures:
1. draw.io source
2. `scripts/export_thesis_drawio_figure.py` width-capped draw.io export
3. insert exported asset into thesis

Local environment facts:
- draw.io executable: `C:\Program Files\draw.io\draw.io.exe`
- preferred wrappers:
  - `C:\Users\Administrator\bin\drawio.cmd`
  - `C:\Users\Administrator\bin\drawio-export.cmd`

Do not default to ad hoc Pillow or fixed-coordinate scripts for final thesis structural figures unless draw.io is genuinely unsuitable.
- Before a draw.io-exported SVG is inserted into the thesis, strip any fallback notice such as `Text is not SVG - cannot display` and reject the export if that text still survives.
- For thesis structural figures, cap the exported figure width before DOCX insertion so the rendered page does not clip the figure body or push internal labels into line/box overlap.

## 3. DOCX Tooling

Preferred path for thesis `.docx` work:
1. officecli / officecli-docx high-level inspection and targeted edits
2. officecli raw or XML-level repair only when high-level operations cannot safely preserve TOC, style binding, field behavior, or pagination
3. use application-render verification for final judgement

Execution-layer source of truth:
- `references/thesis/thesis-execution-contract.md`

Gate split:
- `scripts/validate_skill_gate.py` is the text gate for bundle completeness and evidence-record structure
- `scripts/run_integration_gate.py` is the integration gate for real DOCX / Office / lock / render behavior

Do not treat raw DOCX structure as sufficient proof of final correctness.
Do not treat `officecli view html` as application-render verification. It is a preview aid only and may not replace real renderer export plus page-image review.

### DOCX Renderer Detection And Verification

- Do not conclude that the machine lacks a usable DOCX rendering path merely because one Word COM automation attempt fails.
- Distinguish these states explicitly:
  - Word COM automation failed
  - no usable renderer exists
  - a non-COM renderer such as WPS or LibreOffice is available
- Before reporting that rendering is unavailable, check all of the following:
  - registry `App Paths`
  - uninstall entries
  - user-scope installs
  - standard install paths such as `Program Files`
- Treat WPS and LibreOffice as valid DOCX render/export candidates when they are installed and callable.
- Before relying on a detected renderer, verify it by performing one real export on a review copy instead of only checking that an executable path exists.
- Record the exact executable path that succeeded and reuse that path consistently for later DOCX-to-PDF verification in the same run.
- If Word COM fails but another renderer succeeds, classify the issue as a COM-path failure rather than a no-renderer environment.
- For front-matter numbering and live TOC repair, distinguish renderer success from numbering-authority success:
  - a renderer may export PDF correctly
  - but the office application used to compute adjusted page numbers may still need to be Word COM or WPS COM
- If Word COM is unstable but WPS COM is available, prefer WPS COM for front-matter page-number chain verification and TOC field refresh instead of guessing visible roman numerals from PDF pages alone.

### DOCX TOC-Safe Merge Rule

- For TOC-sensitive thesis runs, do not treat a Word/WPS/LibreOffice-generated TOC block as the final formatting source for the official manuscript.
- If a renderer must be used to refresh TOC content or page numbers, do that refresh on a review copy first.
- After the review-copy refresh, verify the TOC content and page numbers there, then return to the official manuscript and restore the TOC using the locked local baseline for:
  - TOC title
  - TOC level 1
  - TOC level 2
  - TOC level 3
- Do not transplant the whole refreshed TOC `sdt` block from the review copy back into the official manuscript.
- Treat any drift from approved custom TOC styles into generic renderer-generated styles such as `TOC1/TOC2/TOC3` as a failed TOC merge, not as an acceptable refresh result.
- Treat any front-matter page-display drift introduced by a renderer refresh as a failed TOC merge until the official manuscript is restored to the approved local baseline.
- After renderer verification, also lock one rasterizer path for PDF-to-page-image conversion and reuse it consistently for the same run.
- TOC-safe merge acceptance also requires:
  - no visible TOC placeholder or helper text remains
  - no mixed static-plus-field TOC state remains
  - no front-matter page-display mismatch remains between office-application adjusted page numbers and rendered TOC strings

### Content-Only Thesis Rewrite Path

For thesis wording-only or argument-only revisions on an accepted manuscript:
1. inspect target paragraphs and runs with `officecli`
2. apply a run-preserving edit first
3. if run-preserving mutation is not viable, patch `word/document.xml` only
4. render the review copy and verify the touched local page region
5. only run office-application refresh/export steps when the task explicitly includes TOC, pagination, or section repair

Content-only default gate:
- expected package drift is `word/document.xml` only
- if `styles`, `settings`, `fontTable`, `numbering`, `header`, `footer`, `rels`, or `[Content_Types]` drift unexpectedly, fail the pass and restart from the accepted baseline
- if an unchanged citation paragraph loses superscript formatting, fail the pass
- if an untouched table changes visually after a non-table pass, fail the pass
- if a newly inserted body paragraph does not inherit the approved body metrics, fail the pass

### Existing Figure Replacement Constraint

- For already-embedded thesis figures, do not default to `officecli set ... --prop path=...` image replacement.
- Default safe path:
  1. use `officecli` for text, tables, captions, and paragraph formatting
  2. for replacing an existing image, preserve `word/_rels/document.xml.rels` and overwrite only the referenced `word/media/*` binary
  3. adjust drawing extents separately if resizing is required
- Real multi-document DOCX tests on 2026-04-19 showed that `officecli set <picture-run> --prop path=...` can be state-dependent across review-copy lifecycles:
  - it may succeed in one live pass
  - fail after a later close / reopen boundary with `UNSUPPORTED props`
  - or leave stale picture metadata such as old `name` / `alt` values even when the rendered image body has changed
- Treat `rendered image changed` and `picture metadata stayed coherent` as two separate verification surfaces after figure replacement.
- After any existing-image replacement, verify at minimum:
  - media part count did not decrease unexpectedly
  - image relationship count did not decrease unexpectedly
  - no new malformed image targets were introduced
  - the document still opens correctly in Word/WPS
  - the rendered page visibly shows the intended new figure rather than the old figure
  - the picture's stored `name` and `alt` no longer point at the previous asset or previous caption text
- If a high-level image replacement attempt reports unsupported props, behaves differently after a close / reopen boundary, or leaves stale picture metadata, abandon that high-level path for the current pass and switch to the media-binary replacement path on a fresh review copy.
- A local fallback path was verified on 2026-04-19 for one real thesis DOCX:
  - lock the target picture paragraph by stable paragraph identity
  - preserve the existing document relationship id
  - redirect that relationship to a new media target under `word/media/`
  - keep `[Content_Types].xml` consistent with the new image extension
  - sync both `wp:docPr` and `pic:cNvPr` visible metadata such as `name` / `descr`
  - rerender and verify that the new image content and the new visible label both survive export
- Treat that relationship-preserving, metadata-synchronizing path as a preferred narrow fallback before attempting broad image reinsertion or high-risk whole-document rewrites.
- On Windows, do not assume `python` or `py` resolves to a working interpreter for repair scripts.
- Verify the real interpreter path first. If the launcher aliases are broken or point to a store stub, call the installed `python.exe` by absolute path.
- When driving many DOCX mutations on the same file such as table-cell border repair, bulk paragraph pagination repair, or multi-caption normalization, do not rely on hundreds of one-off foreground `officecli set` calls without a lock-aware plan.
- Prefer `officecli open` / `close`, `batch`, or other bounded mutation groups when the write count is large enough to risk timeout or file-handle drift.
- If a bulk mutation run times out, leaves `officecli` or the repair script process alive, or keeps the DOCX file locked, treat the output as uncertain until the file can be reopened and re-inspected.
- If `officecli set` returns but a lingering `officecli.exe` process still blocks the DOCX, treat that as a tooling failure and clear the residual process before any copy, staging, or renderer step.
- If package-level XML parts such as `[Content_Types].xml` or `word/_rels/*.rels` are rewritten directly, preserve the original namespace model including default namespaces, and reopen the resulting DOCX immediately before continuing to later mutations.
- During iterative thesis QA, do not keep overwriting a DOCX path that may already be open in Word, WPS, or a live preview. Write the next repair pass to a fresh review-copy filename instead.
- Use the ASCII staging-copy handoff defined in `references/thesis/thesis-execution-contract.md` when exporting through a real office renderer.

### Windows PowerShell Invocation Default

- On Windows, when automation touches Chinese paths, Chinese comments, or Chinese document content, do not default to long inline `powershell -Command` strings.
- Preferred invocation order:
  1. write a dedicated `.ps1` helper file
  2. save that helper as UTF-8 with BOM
  3. execute it with `powershell -NoProfile -ExecutionPolicy Bypass -File <script.ps1>`
- Use `-LiteralPath` for filesystem targets whenever possible.
- If an inline PowerShell command is unavoidable, prefer `-EncodedCommand` over a raw inline string.
- Treat BOM/encoding corruption, parser drift on Chinese text, and broken quoting in inline commands as tooling failures, not as document-format failures.

### OfficeCLI Inspection Fallback

- `officecli view outline` and `officecli view text` remain preferred quick inspection aids, but do not treat exit code `0` with empty stdout as proof that the DOCX is empty or healthy.
- If automation receives an empty `view outline` / `view text` payload, treat that result as indeterminate and fall back to:
  - `officecli get`
  - `officecli query`
  - or rendered-page review
- Do not build acceptance logic that interprets `empty stdout` from those commands as a clean structural verdict without a second inspection path.

### WPS Built-In Table Authority

- If the current user or locked manuscript sample explicitly requires a WPS built-in table preset such as a WPS table-assistant three-line-table style, do not treat a generic `officecli` table style such as `TableGrid` as satisfying that requirement.
- In that case, the safe tool order is:
  1. apply or clone the intended WPS built-in preset through WPS-aware tooling
  2. export or capture an unselected rendered page
  3. verify the printed border family against the locked WPS authority
- If that WPS-aware path is unavailable for the current pass, record the table lane as blocked or failing rather than silently substituting a generic grid table and continuing as if the style requirement were satisfied.
- Real local tests on 2026-04-19 showed a split behavior in this environment:
  - WPS COM can read thesis DOCX state such as table count, current table style, and `OMaths` presence
  - but WPS COM write attempts on the same class of documents can hang on operations such as table autoformat, table-style reassignment, or formula-numbering edits
- Therefore, do not classify `Kwps.Application` as a generally safe write path merely because it can open the document and report object-model state.
- Before using WPS COM as the active mutation tool for:
  - WPS built-in table-style application
  - formula numbering / numbering-surface repair
  - other fine-grained layout edits
  run one exact-document write probe first.
- If that probe hangs, fails to return, or leaves the DOCX uncertain, mark the WPS COM write lane as blocked for that pass and do not silently replace it with `TableGrid`, a plain grid-table fallback, or an unnumbered formula line.

### DOCX Font-Name And Mojibake Safety

- If a helper script, XML patch, or COM automation path may write non-ASCII font-family names such as `黑体`, `宋体`, `楷体`, or `楷体_GB2312`, do not trust raw shell-source literals by default.
- Preferred repair order for touched title, caption, TOC, reference, and acknowledgement font surfaces:
  1. clone the real template or approved-sample paragraph instance
  2. replace only the intended visible text payload
  3. if a direct XML or automation write is still required, feed the non-ASCII payload through a verified UTF-8-safe path
- After any such write, run a DOCX-internal audit on the exact target path before rendered-page review.
- That audit must inspect at minimum:
  - `word/document.xml`
  - `word/styles.xml`
  - `word/fontTable.xml`
  - touched `word/header*.xml` / `word/footer*.xml`
  - `w:rFonts`, `w:font`, and visible `w:t` payloads for mojibake or unreadable font-family names
- If the office app shows unreadable font labels, fallback-font drift, or mojibake in a touched surface, classify the run as a tooling failure and reject the mutation path before handoff.

## 4. Screenshot Evidence

For implementation chapters and runtime evidence:
- prefer real screenshots from the running system
- do not fabricate screenshots
- if the system is runnable, screenshot capture is part of believable thesis delivery

## 5. Figure Acceptance

Figure work must include both:
- pre-insertion figure review
- post-insertion rendered-page review

A correct source figure alone does not prove the final thesis page is correct.
