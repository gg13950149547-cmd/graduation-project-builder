# 2026-04-19 Conflict Matrix

## Summary

This matrix records the thesis-lane failures that can survive the current text-only acceptance gate.

The goal is to separate:
- real rule conflicts
- execution-path ambiguity
- validator / selftest coverage gaps

## Matrix

| Area | Primary Sources | Failure Type | Current Coverage | Real Office Required | Cross-Session Persistence Risk | Current Finding |
|---|---|---|---|---|---|---|
| Durable rule promotion | `references/user-feedback-persistence.md`, `SKILL.md`, `DURABLE-RULE-PROMOTION-AUDIT.md` | real conflict with incident safety | validator + audit note | no | medium | project-local direct promotion is now explicitly blocked by the routing rule and promotion audit note; remaining risk is manual bypass outside the canonical workflow |
| Paragraph-level rendered review | `SKILL.md`, `references/thesis/thesis-format-sop.md` | execution ambiguity | integration gate + text gate | yes | medium | a two-step paragraph microcycle is now proven on a real review-copy -> staging export chain, but generalized paragraph-region image review and broader thesis edit families remain open |
| Canonical target path vs fresh review-copy path | `SKILL.md`, `references/tooling-dependencies.md`, `references/thesis/thesis-format-sop.md` | execution ambiguity | integration gate + partial text gate | yes | high | single-document staging-copy isolation plus explicit multi-pass review-copy governance are now proven through real export, but broader canonical-target workflows remain open |
| Surface ownership and bulk mutation | `SKILL.md`, `references/user-feedback/maintenance-and-structure.md`, `references/tooling-dependencies.md` | execution ambiguity | integration gate + text gate | yes | medium | serialized `officecli -> picture helper -> staging export` and `officecli -> formula helper -> staging export` chains are now proven, and integration additionally guards figure-block locality, image-holder paragraph safety, plus TOC-control body contamination in sample-self-check lanes, but broader helper families and multi-surface ownership conflicts remain open |
| Renderer / rasterizer truth | `references/tooling-dependencies.md`, `references/thesis/thesis-format-sop.md` | coverage gap | integration gate + text gate | yes | medium | Word COM staging export and rendered-PDF inspection are now proven in integration cases; alternate renderer parity is additionally covered when WPS or LibreOffice is available on the current machine |
| Validator / selftest realism | `scripts/validate_skill_gate.py`, `scripts/selftest_skill_flow.py`, `scripts/sample_self_check.py`, `scripts/run_integration_gate.py`, `scripts/audit_docx_body_style.py` | coverage gap | self-referential + integration gate | yes | medium | sample_self_check now has positive and negative integration coverage for heading-family demotion, third-level heading baseline drift, abstract surface baseline drift, code-title formatting, code-block formatting, TOC visible format, header position, footer indent, footer typography baseline drift, table family, table-caption binding, body-style binding, Normal baseline drift, non-body contamination, non-body indent leakage, cross-page table continuation titles, figure-block locality, image-holder paragraph safety, image-size safety, bibliography count retention, and TOC-control body contamination; integration additionally covers a direct-template shortest-manuscript builder smoke path, but broader real Office failure families are still not exhaustively covered |
| Humanizer default route | `RULE-CONFLICT-REVIEW.md`, `references/thesis/thesis-companion.md`, `scripts/selftest_skill_flow.py` | resolved drift / regression-guarded | validator + selftest | no | low | explicit route-by-language handling is now guarded by validator and selftest; remaining risk is future rule drift, not a live autoinfer path |

## Incident Regression Families

| Fixture ID | User-Visible Failure | Intended Gate Owner | Status |
|---|---|---|---|
| `RG-20260419-01` | Chinese abstract title missing, clipped, or visually broken | integration gate | active |
| `RG-20260419-02` | English abstract title or keyword style drift | integration gate | active |
| `RG-20260419-03` | TOC / Roman-Arabic numbering chain drift | integration gate | active |
| `RG-20260419-04` | References / acknowledgement title collides with header zone or produces blank-page side effects | integration gate | active |

## Immediate Conclusions

- `scripts/validate_skill_gate.py` must be treated as a text gate, not as proof that a thesis run is safe.
- `scripts/selftest_skill_flow.py` must retain fast dummy coverage but also delegate to real DOCX integration cases.
- thesis mutation is unsafe until a single execution contract and a real integration gate exist together.
