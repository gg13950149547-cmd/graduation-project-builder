# Thesis Format Rules

Use this file as the routing layer for thesis-formatting work only.

## 0. Enforcement Status

- Every routed rule under this file is mandatory when the relevant child file is loaded for the current subtask.
- Treat the child files below as must-follow thesis-format rules, not as optional guidance.
- Use `references/rule-owner-map.json` as the canonical owner manifest for durable thesis-format rule ids routed through this file.
- If another source overrides a routed rule here, the override must come from a higher-precedence source such as an official template or an explicit current-user instruction.

## Child Files

- `references/thesis/format-rules/protected-surface-evidence-contract.md`: protected surface ids, evidence record shape, effective font-chain proof, TOC visual-geometry proof, TOC paragraph-and-typography proof, and multi-agent audit handoff contract
- `references/thesis/format-rules/general-and-docx-safety.md`: general principles, safe DOCX editing, and detection scope
- `references/thesis/format-rules/front-matter-and-toc.md`: front-matter and TOC repair rules
- `references/thesis/format-rules/headings-and-figures.md`: heading repair and figure-format repair rules
- `references/thesis/format-rules/tables-abstracts-citations-references.md`: table, abstract, Chinese abstract mixed-script font inspection, keyword label/content run separation, citation, and references rules
- `references/thesis/format-rules/repair-logging-and-technical-notes.md`: repair logging, technical notes, and escalation behavior
- `references/thesis/thesis-format-class-review.md`: mandatory surface inventory and class-by-class final review

## Loading Rule

- Load only the child files relevant to the current format-repair subtask instead of bulk-loading every thesis-format child file.
- For a normal thesis format-repair run, the default load set is the six format-rule child files above plus `references/thesis/thesis-format-class-review.md`.
- For thesis generation, thesis revision, format repair, whole-thesis format audit, or any user-reported format problem involving abstract, keywords, TOC, fonts, citations, references, page numbers, headers, footers, or end matter, always load `references/thesis/format-rules/protected-surface-evidence-contract.md`.
- For any user-reported or detected keyword-line issue, load `references/thesis/format-rules/tables-abstracts-citations-references.md` and enforce `FMT-ABSTRACT-001` with direct DOCX run-structure inspection; a keyword-line evidence record that only self-reports `run split confirmed: yes` is not sufficient.
- For any user-reported or detected Chinese abstract font issue, load `references/thesis/format-rules/tables-abstracts-citations-references.md` and enforce `FMT-ABSTRACT-002` with direct DOCX mixed-script font inspection; checking only the first abstract content run or a prose font-chain summary is not sufficient.
- For any user-reported or detected body-text font issue, especially Chinese text drifting into `Times New Roman` or mixed Chinese/English body paragraphs losing run boundaries, load `references/thesis/format-rules/general-and-docx-safety.md` and `references/thesis/format-rules/protected-surface-evidence-contract.md` and require direct DOCX run-level inspection for the touched body paragraphs; a body-style-only audit is not sufficient.
- If the task narrows to one surface such as TOC, headings, abstracts, citations, or references, load the matching child files first and add others only if the fix expands outward.
- A narrow surface run still loads the protected-surface evidence contract when the surface is protected or when the result will be used in final acceptance.
- TOC format audit is not complete until `front-matter-and-toc.md` and the protected-surface evidence contract both agree that per-level style binding, paragraph-dialog metrics, typography metrics, and rendered visual geometry have all passed against the locked template.
- Do not skip `references/thesis/thesis-format-class-review.md` for thesis generation, thesis revision, or thesis format repair, because it owns the mandatory surface inventory.

## Parent Boundary

- Keep this parent file short and routing-oriented.
- Do not duplicate full format-rule bodies here once they have been moved into child files.
- If a child file becomes too heavy, split it further and update `SKILL.md`, `FILE-ROLE-INDEX.md`, and validation logic in the same turn.
