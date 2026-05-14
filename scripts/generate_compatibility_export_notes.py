#!/usr/bin/env python3
"""Regenerate compatibility export notes from validator registry metadata."""

from __future__ import annotations

from pathlib import Path

try:
    from .validate_skill_gate_bundle import (
        build_expected_compatibility_note_lines,
        build_expected_external_audit_record_lines,
        build_expected_external_audit_record_preamble_lines,
        build_expected_external_audit_note_preamble_lines,
        build_expected_external_audit_note_lines,
    )
    from .validate_skill_gate_registry_bundle import (
        COMPATIBILITY_EXTERNAL_AUDIT_RECORD,
        COMPATIBILITY_EXTERNAL_AUDIT_NOTE,
        COMPATIBILITY_ONLY_EXPORTS,
        COMPATIBILITY_RETIREMENT_NOTE,
    )
except ImportError:
    from validate_skill_gate_bundle import (
        build_expected_compatibility_note_lines,
        build_expected_external_audit_record_lines,
        build_expected_external_audit_record_preamble_lines,
        build_expected_external_audit_note_preamble_lines,
        build_expected_external_audit_note_lines,
    )
    from validate_skill_gate_registry_bundle import (
        COMPATIBILITY_EXTERNAL_AUDIT_RECORD,
        COMPATIBILITY_EXTERNAL_AUDIT_NOTE,
        COMPATIBILITY_ONLY_EXPORTS,
        COMPATIBILITY_RETIREMENT_NOTE,
    )


SKILL_ROOT = Path(__file__).resolve().parents[1]


def build_note_text(
    *,
    title: str,
    section_heading: str,
    line_builder,
    preamble_lines: list[str] | None = None,
) -> str:
    lines = [
        title,
        "",
    ]
    if preamble_lines:
        lines.extend(preamble_lines)
        lines.append("")
    lines.extend(
        [
        section_heading,
        "",
        ]
    )
    for export_name, metadata in COMPATIBILITY_ONLY_EXPORTS.items():
        lines.extend(line_builder(export_name, metadata))
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def build_external_audit_record_text() -> str:
    lines = [
        "# Compatibility Export External Audit Record",
        "",
        "## Audit Meta",
        "",
        *build_expected_external_audit_record_preamble_lines(),
        "",
        "## Export Results",
        "",
    ]
    for export_name, metadata in COMPATIBILITY_ONLY_EXPORTS.items():
        lines.extend(build_expected_external_audit_record_lines(SKILL_ROOT, export_name, metadata))
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def write_note(rel_path: str, text: str) -> None:
    (SKILL_ROOT / rel_path).write_text(text, encoding="utf-8")


def regenerate_notes() -> None:
    retirement_text = build_note_text(
        title="# Compatibility Export Retirement Note",
        section_heading="## Export Inventory",
        line_builder=build_expected_compatibility_note_lines,
    )
    write_note(COMPATIBILITY_RETIREMENT_NOTE, retirement_text)

    external_audit_text = build_note_text(
        title="# Compatibility Export External Audit",
        section_heading="## Export Audit Inventory",
        line_builder=build_expected_external_audit_note_lines,
        preamble_lines=["## Audit Meta", *build_expected_external_audit_note_preamble_lines()],
    )
    write_note(COMPATIBILITY_EXTERNAL_AUDIT_NOTE, external_audit_text)

    external_audit_record_text = build_external_audit_record_text()
    write_note(COMPATIBILITY_EXTERNAL_AUDIT_RECORD, external_audit_record_text)


def main() -> int:
    regenerate_notes()
    print("compatibility export notes regenerated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
