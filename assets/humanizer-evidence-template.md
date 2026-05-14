# Humanizer Evidence Template

Use this template for every non-`none` humanizer evidence path referenced by `assets/final-acceptance-template.md`.

Each record covers one processed paragraph or abstract block. If a run processes multiple paragraphs, create one record per paragraph or separate multiple evidence files with `;` in the acceptance record.

## Humanizer Evidence Record

## Required Fields
- evidence id:
- target language:
- skill name:
- skill file path:
- skill loaded before rewrite?:
- route application method:
- paragraph id:
- before text:
- after text:
- rewrite changed?:
- preservation verdict:
- AI-pattern cleanup verdict:
- blocker summary:

## Field Rules
- `target language` must be `zh` / `Chinese` for `humanizer-zh`, or `en` / `English` for `humanizer`.
- `skill name` must be exactly `humanizer-zh` or `humanizer`.
- `skill file path` must point to the exact UTF-8 `SKILL.md` loaded for the pass; the file must exist, its frontmatter `name` must match `skill name`, and mojibake-corrupted skill text is not valid evidence.
- `skill loaded before rewrite?` must be `yes`; a generated evidence file cannot stand in for skill invocation.
- `route application method` must identify the actual content-edit route, not only a validator or acceptance-generator step.
- `route application method` must not be an acceptance-record generator, validator, smoke checker, or report synthesizer. Evidence created by `generate_thesis_acceptance_record.py` or another post-hoc acceptance tool is invalid.
- `paragraph id` must identify the concrete thesis paragraph, abstract block, or keyword line that was processed.
- `before text` and `after text` must contain the actual text before and after the humanizer pass, not only a path, summary, or screenshot reference.
- `rewrite changed?` must be `yes` unless the evidence gives a concrete no-change reason in `AI-pattern cleanup verdict`; identical before/after text with a generic pass verdict is not evidence.
- `preservation verdict` must state whether facts, citations, terminology, and claim scope were preserved.
- `AI-pattern cleanup verdict` must state what AI-sounding pattern was removed or why no language change was needed.
- `AI-pattern cleanup verdict` must explicitly cover meta-evaluation voice and thesis-native wording when the text is Chinese thesis body prose.
- `blocker summary` must be `none` only when the pass is complete and non-blocking.
