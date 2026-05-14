# Thesis Format Rules: Repair Logging And Technical Notes

Use this file for repair logging, DOCX technical notes, and escalation behavior.

## Enforcement Status

- Every rule in this file is mandatory when this file is loaded for the current format-repair subtask.
- Apply this file together with `references/thesis/thesis-format-rules.md`.

## 12. Repair Logging And Automation Boundaries

- When automated repair is substantial, keep structured repair records with:
  - location
  - check item
  - original value
  - new value
  - severity
- Prefer generating or preserving a user-facing repair summary when many formatting fixes were applied.
- Treat these as common manual-confirmation items unless the toolchain proves otherwise:
  - header rule lines
  - TOC refresh
  - exact figure or formula positioning
  - footnote formatting
- When the trigger incident is pagination drift, stale TOC page numbers, or front-matter pollution, write a root-cause note before the next repair pass begins.

## 13. DOCX Technical Notes

- When unsure about property names, value formats, or command syntax, run `officecli docx view`, `get`, `query`, `set`, or `add` help instead of guessing.
- For multi-step thesis `.docx` work, keep the file in one controlled session with `officecli open` / `close`.
- After each repair batch, use `officecli validate` as structural QA, but do not treat it as a substitute for rendered-page sign-off.
- Prefer character-based first-line indentation over fixed-distance indentation for thesis body text when the target style is "2 characters".
- If paragraph indent must be cleared, explicitly set it to zero rather than assuming style inheritance will disappear.
- When mixed Chinese and Latin fonts appear in headers or similar constrained regions, verify both East Asian and ASCII font assignments instead of setting only one side.
- After any helper script, XML patch, or PowerShell automation that touched visible text or font-bearing surfaces, run a DOCX-internal mojibake/font audit on the exact target path before continuing.
- That audit must inspect visible `w:t` text plus font-bearing nodes such as `w:rFonts`, `w:font`, and related font-name attributes in `document.xml`, `styles.xml`, `fontTable.xml`, and any touched header/footer parts.
- Before any TOC refresh or TOC rebuild, verify that the document still has the required section boundary between front matter and the first main-body chapter.
- The minimum accepted pagination setup is:
  - all pages before the abstract/TOC block display no visible page number by default
  - cover and declaration pages not treated as main-body arabic numbering
  - abstract and TOC pages using the required front-matter numbering system
  - the first main-body chapter restarting at arabic page `1`
- If a later DOCX mutation collapses sections or destroys the numbering boundary, rerun pagination repair before delivery.

## 13.1 Recorded Failure Pattern: Front Matter, TOC, And Bulk Script Drift

- Failure pattern:
  - a bulk script rewrites front matter with body-style logic
  - screenshots or diagrams are inserted before field refresh is re-checked
  - TOC fields remain stale and continue showing old `PAGEREF` results
  - repeated save cycles trigger file locking and leave the repair half-applied
- Recovery order:
  1. stop bulk styling
  2. inspect section boundaries and front-matter scope
  3. inspect fields and TOC page references
  4. repair front matter separately
  5. rerun rendered-page review on TOC pages and first body chapter pages
- Prevention rule:
  - after combined screenshot insertion, figure replacement, or paragraph cleanup, do not continue directly to final handoff
  - rerun structure review first, then pagination and field review, then style review

## 13.2 Recorded Failure Pattern: False Acceptance From Under-Specified Evidence

- Failure pattern:
  - the active rules already require same-line far-right formula numbering and six-surface abstract review
  - but the evidence records only generic `formula numbering visible` or only TOC-to-abstract seam repair
  - self-test samples lag behind the current evidence schema
  - gate passes because the evidence text is syntactically valid even though the claimed visual result is weaker than the rules
- Recovery order:
  1. update the evidence template so the missing acceptance surfaces become explicit fields
  2. update the gate validator to reject standalone formula-number paragraphs and abstract claims without six-surface confirmation
  3. update the self-test suite to include both valid and invalid examples for those failure shapes
  4. rerun the thesis repair from the current accepted manuscript and regenerate evidence
- Prevention rule:
  - do not let review evidence stay more generic than the strongest active template rule for the same surface
  - do not accept abstract or TOC pass records that only say `checked`, `format consistent`, `page numbers correct`, `visible`, or `rendered`; the record must include surface row, locked baseline, DOCX internal evidence, rendered evidence, metric-by-metric comparison, and verdict
  - do not accept abstract or TOC evidence paths that point only to a PNG, PDF, officecli validation log, style-name audit, or page-class matrix; the path must resolve to a review evidence record for the exact final deliverable and that record must itself name the protected surface evidence

## 13.3 Recorded Failure Pattern: Mojibake In DOCX Font Names After PowerShell-Oriented Tail-Block Repair

- Failure pattern:
  - a Windows PowerShell helper writes non-ASCII East Asian font names directly into DOCX XML or COM properties
  - the script path or save path is not encoding-safe for those literals
  - touched title paragraphs such as `结论`, `参考文献`, or `致谢` end up with mojibake font-family names in `w:rFonts`
  - WPS or Word shows unreadable font labels or falls back to the wrong visible font
- Recovery order:
  1. stop reusing the unsafe script path
  2. restore the touched paragraph from a real template/sample title baseline
  3. rerun a DOCX-internal font/encoding audit on the exact review copy
  4. only then rerender and recheck the page class
- Prevention rule:
  - do not approve a tail-block repair until both the rendered page and the DOCX-internal font-name audit pass on the same output path

## 13.4 Recorded Failure Pattern: TOC Refresh Keeps Content But Loses The Approved Visual Baseline

- Failure pattern:
  - TOC field refresh succeeds and updates page numbers
  - the refreshed TOC falls back to default app spacing, default font sizing, or a compressed single-page layout
  - the acceptance record keeps only a generic `TOC / bookmark integrity summary`
  - the run passes because the TOC is semantically correct even though its visual baseline was not restored
- Recovery order:
  1. extract the accepted TOC title and TOC level baselines from the template or approved sample
  2. record the visible TOC metrics and rendered page-occupancy baseline
  3. refresh the TOC
  4. restore the TOC title and each TOC level to the locked baseline in the same pass
  5. rerender the TOC pages and compare them against the locked occupancy rhythm before handoff
- Prevention rule:
  - do not accept a TOC repair with only `entries correct` or `page numbers correct`
  - require explicit restoration evidence for the TOC title, TOC levels, dotted leaders, right-tab column, and rendered page occupancy

## 13.5 Recorded Failure Pattern: Skill Registry Drift After Adding New Thesis Surfaces

- Failure pattern:
  - new thesis-surface fields are added to templates or policy maps but not to the final acceptance schema
  - the generated acceptance record contains the new fields, yet the validator does not parse them into the canonical gate value map
  - mandatory verdict checks then fail positive cases, or future fields can become policy-only text without enforcement
  - stale sample self-check or broad review evidence can appear sufficient because the schema, validator, and selftests were not advanced together
- Recovery order:
  1. add the new field to the final acceptance schema, field policy map, template, generator output, and required path map when applicable
  2. add or update both positive and negative selftests for the exact surface and stale-evidence failure shape
  3. regenerate validator registries and run the registry roundtrip selftest
  4. run the narrow affected cases first, then the relevant fast suite
- Prevention rule:
  - treat a new thesis protected surface as incomplete until schema, generator, validator, evidence template, selftest fixture, and fast-suite coverage all agree on the same field names and exact output binding

## 14. Escalation Rule

- If rendered pages still differ materially from the sample in title layout, TOC rhythm, figure visibility, table appearance, header/footer behavior, or page numbering, continue repairing until the mismatch is materially reduced.
