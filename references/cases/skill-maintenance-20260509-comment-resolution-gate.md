# Skill Maintenance Case: Comment Resolution Gate

## Scope

- Date: 2026-05-09
- Skill root: `C:\Users\Administrator\.agents\skills\graduation-project-builder`
- Trigger: repeated thesis comment-repair failures where local passes and Word/WPS done states were treated as full comment completion.
- User authorization: multi-agent collaboration authorized in the conversation.
- Dispatch notes: existing audit/figure/citation/format agents returned read-only findings; one additional read-only comment-audit agent was spawned. No subagent edited files. Format-lane timeout before its final notification was recorded as sequential fallback until the late result arrived.

## Root Cause

- `commentsExtended.xml` done/resolved state was being confused with semantic completion.
- Local transaction, figure-size, and citation checks could pass while most teacher comments stayed open.
- Figure comments with crop/provenance/redraw/content/readability subissues were being closed from size-only evidence.
- Final acceptance did not require a source/final-DOCX-bound comment-resolution ledger for all-comments-resolved claims.

## Changes

- Added `scripts/audit_thesis_comment_resolution.py` as the semantic comment-closure auditor.
- Updated `scripts/validate_thesis_mutation_transaction.py` to require and validate a comment-resolution ledger for comment-driven transactions.
- Updated `scripts/validate_skill_gate_record_gate.py` so final acceptance rejects comment done-state changes and all-comments-resolved claims without ledger/audit evidence.
- Added final acceptance fields for comment-resolution ledger path, audit report path, and audit verdict.
- Added durable rules `FB-THESIS-011`, `EXEC-MAINT-064`, and `QA-FINAL-055`.
- Updated `references/rule-owner-map.json`, `FILE-ROLE-INDEX.md`, and `assets/user-reported-issue-ledger-template.md`.

## Validation

- `py -3 -m py_compile scripts/audit_thesis_comment_resolution.py scripts/validate_thesis_mutation_transaction.py scripts/validate_skill_gate_record_gate.py scripts/generate_thesis_acceptance_record.py scripts/selftest_skill_flow.py`: PASS
- `py -3 -m json.tool references/rule-owner-map.json`: PASS
- `py -3 scripts/validate_skill_gate.py --skill-root .`: PASS
- `py -3 scripts/check_utf8_clean.py --root . --json`: PASS
- `py -3 scripts/selftest_skill_flow.py --case comment_done_without_evidence_rejected --case figure_comment_size_only_false_pass_rejected --case open_comments_final_acceptance_rejected --case transaction_comment_resolution_ledger_missing_rejected --quiet`: PASS
- `py -3 scripts/selftest_skill_flow.py --case thesis_only_valid --case format_repair_valid --case transaction_comment_fixed_index_rejected --quiet`: PASS

## Remaining Risk

- The full `fast` and `fast-thesis-records` suites were not rerun in this continuation because they are known to approach or exceed single-command timeouts in this environment.
- The next thesis pass must regenerate all evidence after these skill changes; pass019 evidence is stale under the new gate.
