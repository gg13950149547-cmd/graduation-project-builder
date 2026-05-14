# Skill Maintenance Case: Local Keyword Transaction And Source-Relative Citation Diff

## Scope

- Date: 2026-05-09
- Mode: skill-maintenance
- User authorization: multi-agent collaboration authorized in the current session
- Changed scope: canonical `graduation-project-builder` skill only; thesis DOCX content is not promoted by this case record

## Problem

- A local keyword/front-matter run-structure repair can be falsely blocked by chapter-level format-preservation requirements even when no body chapter is targeted and no whole-thesis format-preservation claim is made.
- A citation source-to-final diff can falsely report `lost hyperlink host` when the source citation marker was already a plain superscript marker without a hyperlink/bookmark host.

## Rule Decision

- Base transaction evidence remains mandatory for every mutating local repair: protected-surface freeze, post-mutation diff, target render review, blast-radius render review, cross-surface regression report, final DOCX path binding, and final DOCX SHA256 binding.
- `chapter_format_preservation_report` and `chapter.format-preservation-contract` are required when a body/chapter surface is touched or when the transaction makes a real format-preservation promise.
- A keyword/front-matter-only local repair may use a concrete `not-applicable-*` chapter detector verdict when no body/chapter surface is targeted and no format-preservation promise is made.
- Citation hyperlink preservation is source-relative. Final citation markers must keep hyperlink/bookmark hosts only when the corresponding source marker had one.

## Changed Files

- `scripts/validate_thesis_mutation_transaction.py`
- `scripts/audit_docx_review_artifacts.py`
- `scripts/selftest_skill_flow.py`
- `references/thesis/thesis-mutation-transaction.md`
- `references/thesis/format-rules/protected-surface-evidence-contract.md`
- `references/user-feedback/maintenance-and-structure.md`
- `references/rule-owner-map.json`
- `FILE-ROLE-INDEX.md`
- `DURABLE-RULE-PROMOTION-AUDIT.md`

## Regression Coverage

- `transaction_local_keyword_no_chapter_format_claim_valid`
- `transaction_body_touch_requires_chapter_format_report_rejected`
- `body_citation_diff_source_without_hyperlinks_valid`
- `body_citation_diff_source_hyperlink_removed_rejected`

## Verification

- `py -3 -m py_compile scripts/validate_thesis_mutation_transaction.py scripts/audit_docx_review_artifacts.py scripts/selftest_skill_flow.py`
- `py -3 scripts/selftest_skill_flow.py --case transaction_local_keyword_no_chapter_format_claim_valid --case transaction_body_touch_requires_chapter_format_report_rejected --case body_citation_diff_source_without_hyperlinks_valid --case body_citation_diff_source_hyperlink_removed_rejected --quiet`

## Remaining Risk

- This case does not claim the current thesis manuscript is final. A real thesis handoff still needs completed transaction evidence records, rendered target/blast/cross-surface review, and final acceptance validation against the exact DOCX path and SHA256.
