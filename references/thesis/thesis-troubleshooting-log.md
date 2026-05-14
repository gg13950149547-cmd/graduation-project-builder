# Thesis Troubleshooting Log

Use this file as the routing layer for thesis-production failures and recovery-only work.

## Routing Note

- Treat this file as a failure-recovery supplement, not as the primary source for normal thesis formatting defaults.
- For canonical thesis formatting and DOCX toolchain behavior, use:
  - `references/tooling-dependencies.md`
  - `references/thesis/thesis-format-sop.md`
  - `references/thesis/thesis-format-rules.md`
- Use this file when the normal workflow has already encountered drift, corruption, disappearance, duplication, or unreliable environment behavior.

## Child Files

- `references/thesis/troubleshooting/recovery-basics.md`: baseline recovery behavior, numbering collisions, style-name false positives, anchor targeting, and console-encoding repair
- `references/thesis/troubleshooting/media-and-figure-recovery.md`: media preservation, screenshot authenticity, equation recovery, body-copy media damage, and figure clipping incidents
- `references/thesis/troubleshooting/template-and-toc-rebuild.md`: legacy template integration, annotation cleanup, TOC-loss recovery, and unstable rebuild automation
- `references/thesis/troubleshooting/blank-pages-and-end-matter.md`: blank-page root causes, reference boundary drift, and late-stage conclusion or end-matter cleanup

## Loading Rule

- Load only the child files relevant to the current recovery incident instead of bulk-loading every troubleshooting child file.
- For a broad thesis rebuild failure, start with `recovery-basics.md`, then add the incident-specific child files that match the observed failure mode.

## Parent Boundary

- Keep this parent file short and routing-oriented.
- Do not duplicate the full recovery rule bodies here once they have been moved into child files.
- If a troubleshooting child file becomes too heavy, split it further and update `SKILL.md`, `FILE-ROLE-INDEX.md`, and validation logic in the same turn.
