# Skill Maintenance Case: Ordinary Screenshot Readability Gate

Date: 2026-05-12

## Scope

- Mode: `skill-maintenance` plus bounded project thesis repair continuation.
- User authorization: current session explicitly authorizes multi-agent collaboration; existing live agents were reused for read-only review and the controller applied the canonical skill changes.
- Changed skill surfaces: figure display-size audit defaults, figure selftest coverage, owner-map coverage, focused rule references, and file-role index.
- Thesis mutation scope: no original thesis overwrite; repaired review copies must be generated as new DOCX outputs.

## Defect

The previous figure display-size gate allowed ordinary runtime/UI screenshots to pass at the old technical floor of `3.0 cm x 2.5 cm`. In the campus abnormal-behavior thesis, several pop-up or landscape screenshots were visibly too small while still passing default audit settings.

## Durable Rule

Ordinary runtime screenshots, UI screenshots, result screenshots, and pop-up screenshots are unreadable by default when their final DOCX display size is below `8.0 cm` width or `4.0 cm` height. Structural figures keep the stricter structural width floor of `9.0 cm`.

## Validation Target

- `py -3 -m py_compile scripts/audit_docx_figure_extents.py scripts/selftest_skill_flow.py`
- `py -3 scripts/selftest_skill_flow.py --case audit_figure_extents_runtime_screenshot_narrow_rejected --quiet`
- `py -3 -m json.tool references/rule-owner-map.json`
- `py -3 scripts/validate_skill_gate.py --skill-root .`
- `py -3 scripts/check_utf8_clean.py --root . --json`

## Remaining Risk

Final thesis handoff still requires exact-DOCX render evidence after the resized review copy is produced. The display-size gate proves geometry, not full page readability or pagination continuity.
