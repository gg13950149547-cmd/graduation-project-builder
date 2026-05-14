# Graduation Project Builder Memory

Only store durable, cross-project rules here.

## Stable Delivery Rules

- Default to autonomous execution once the task direction is clear.
- Before changing a graduation-project artifact, first check whether an existing focused reference already governs the task. Do not improvise a new path while an applicable stable rule already exists.
- For graduation-project web systems, Chinese should be the primary UI language unless the user explicitly requests another language.
- For graduation-project business pages, the first visible copy should answer what the user wants to see or do now, not introduce the platform itself.
- For graduation-project business pages, write as if the product is being used by its real domain operator, not by a student explaining the project.
- For graduation-project web systems, authentication is part of the minimum believable delivery when protected roles or management functions exist.
- For graduation-project web systems, frontend-backend separation is the default expected architecture unless the user explicitly requires another structure.
- Split role-specific experiences when roles materially differ.
- Admin analytics should include at least one line chart by default for management, data-analysis, or visualization-oriented systems unless the user explicitly overrides it.
- Project directory structure should remain clear and easy to navigate.
- Do not stop at a demo-only prototype when persistence, admin operations, analytics, packaging, or verification are still missing.
- After each meaningful batch, verify by actually starting the application or running the narrowest relevant live check.
- Before claiming a local web system is accessible, verify process alive, port listening, and HTTP 200.
- When a project includes both the program and the thesis, finish the real system before final thesis polishing unless the user explicitly requests thesis-only work.
- If the user provides a manually adjusted thesis draft as the new baseline, treat that draft as the only active manuscript source.
- If a thesis revision branch becomes visibly corrupted, mixed, or layout-broken, restart from the last clean baseline instead of layering more patches onto the damaged branch.
- Before reporting any thesis artifact, verify that the exact output file exists on disk.
- When a thesis still differs materially from the active school template in protected surfaces such as cover, abstracts, TOC, heading classes, references, or end matter, do not describe it as complete just because structural validators pass.
- Treat cover, abstract, TOC, and other front matter as protected surfaces rather than ordinary body text.
- When the user says content is accepted and only format remains, freeze content and do format-only work.
- Use UTF-8-safe automation and preserve UTF-8 without BOM for skill markdown files.
- Any substantial run must pass a self-check before handoff: confirm current user requirements are addressed, output files exist, and the relevant pages, chapters, or flows were reviewed with evidence; spot-checks are acceptable only for intermediate status, never for `ready to submit` or equivalent claims.
- Exact-final-artifact review must be performed on the same artifact path named in the acceptance record; a clean review copy does not close a different submission file automatically.
- For thesis `.docx` files with existing figures, never use a replacement path that rewrites image relationships blindly; preserve media relationships and replace only image binaries.
- Do not execute from a project-local mirrored skill bundle until that exact mirror has passed `scripts/selftest_skill_flow.py` and `scripts/validate_skill_gate.py`; if it fails, resync from the canonical skill root before continuing.
- For thesis DOCX work, lock one canonical write target path before any helper script or bulk mutation; do not let scripts guess by newest file or wildcard review-copy names.
- For thesis DOCX work, one protected surface may have only one active write owner per pass, and every bulk script run must be followed by a smoke audit before the next step.

## Memory Boundary

Do not write these into this file:

- school-specific template patch details
- detailed thesis formatting classes
- detailed TOC, heading, figure, table, or formula micro-rules
- thesis toolchain step lists that already belong in focused references
- one-off project debugging notes
- transient environment incidents
- narrow visual sample details

Write detailed durable rules into focused references instead:

- workflow or user-correction defaults: `references/user-feedback-persistence.md`
- thesis formatting rules: `references/thesis/thesis-format-rules.md`
- thesis execution order and tool routing: `references/thesis/thesis-format-sop.md`
- thesis content-production rules: `references/thesis/thesis-production-workflow.md`
- thesis figure generation rules: `references/thesis/thesis-figure-generation-rules.md`
- thesis figure review checks: `references/review-figure-style-checklist.md`

## Memory Maintenance Rules

- Whenever adding new rules, consolidate memory instead of appending blindly.
- If a new lesson overlaps with an existing focused reference, merge it into that reference instead of creating a competing copy in memory.
- If a new lesson is only about file ownership or active-vs-archive routing, update `FILE-ROLE-INDEX.md` in the same turn.
- Keep `memory.md` short enough to remain a reliable first-stop summary rather than a second full rulebook.
