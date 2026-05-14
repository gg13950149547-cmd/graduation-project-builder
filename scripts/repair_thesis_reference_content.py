#!/usr/bin/env python3
"""Bounded thesis reference-content replacement for DOCX packages.

This helper deliberately changes only word/document.xml by exact text matches.
It is for replacing a verified bibliography entry or nearby host sentence
without rebuilding citation markers, bookmarks, comments, relationships, media,
styles, numbering, headers, footers, or the rest of the package.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import zipfile
from pathlib import Path
from typing import Any
from xml.sax.saxutils import escape


SCHEMA = "graduation-project-builder.reference-content-repair.v1"
REPORT_SCHEMA = "graduation-project-builder.reference-content-repair-report.v1"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_plan(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("reference repair plan root must be an object")
    if payload.get("schema") not in {None, SCHEMA}:
        raise ValueError(f"reference repair plan schema must be {SCHEMA}")
    replacements = payload.get("replacements")
    if not isinstance(replacements, list) or not replacements:
        raise ValueError("reference repair plan requires a non-empty replacements list")
    for index, item in enumerate(replacements):
        if not isinstance(item, dict):
            raise ValueError(f"replacement row {index} must be an object")
        if not isinstance(item.get("old"), str) or not item.get("old"):
            raise ValueError(f"replacement row {index} requires non-empty old text")
        if not isinstance(item.get("new"), str) or not item.get("new"):
            raise ValueError(f"replacement row {index} requires non-empty new text")
    return payload


def read_package_entry(docx_path: Path, name: str) -> bytes:
    with zipfile.ZipFile(docx_path, "r") as archive:
        return archive.read(name)


def package_bytes_by_name(docx_path: Path) -> dict[str, bytes]:
    with zipfile.ZipFile(docx_path, "r") as archive:
        return {info.filename: archive.read(info.filename) for info in archive.infolist()}


def write_package_with_document_xml(source_docx: Path, output_docx: Path, document_xml: bytes) -> None:
    output_docx.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(source_docx, "r") as source, zipfile.ZipFile(output_docx, "w") as target:
        for info in source.infolist():
            data = document_xml if info.filename == "word/document.xml" else source.read(info.filename)
            target.writestr(info, data)


def apply_replacements(document_xml: str, plan: dict[str, Any]) -> tuple[str, list[dict[str, Any]], list[str]]:
    issues: list[str] = []
    results: list[dict[str, Any]] = []
    current = document_xml
    for index, item in enumerate(plan["replacements"]):
        name = str(item.get("name") or f"replacement_{index + 1}")
        old_text = item["old"]
        new_text = item["new"]
        expected_count = int(item.get("expected_count", 1))
        old_xml = escape(old_text)
        new_xml = escape(new_text)
        count = current.count(old_xml)
        if count != expected_count:
            issues.append(f"{name}: expected {expected_count} XML text match(es), found {count}")
            results.append(
                {
                    "name": name,
                    "expected_count": expected_count,
                    "actual_count": count,
                    "status": "failed",
                }
            )
            continue
        required_new_contains = item.get("required_new_contains") or []
        if isinstance(required_new_contains, str):
            required_new_contains = [required_new_contains]
        missing_tokens = [str(token) for token in required_new_contains if str(token) not in new_text]
        if missing_tokens:
            issues.append(f"{name}: new text missing required token(s): {', '.join(missing_tokens)}")
            results.append(
                {
                    "name": name,
                    "expected_count": expected_count,
                    "actual_count": count,
                    "status": "failed",
                    "missing_required_new_tokens": missing_tokens,
                }
            )
            continue
        current = current.replace(old_xml, new_xml, expected_count)
        results.append(
            {
                "name": name,
                "expected_count": expected_count,
                "actual_count": count,
                "old_text_sha256": hashlib.sha256(old_text.encode("utf-8")).hexdigest(),
                "new_text_sha256": hashlib.sha256(new_text.encode("utf-8")).hexdigest(),
                "status": "replaced",
            }
        )
    return current, results, issues


def compare_package_scope(source_docx: Path, final_docx: Path) -> dict[str, Any]:
    source_bytes = package_bytes_by_name(source_docx)
    final_bytes = package_bytes_by_name(final_docx)
    source_names = set(source_bytes)
    final_names = set(final_bytes)
    changed = sorted(
        name
        for name in source_names & final_names
        if source_bytes[name] != final_bytes[name]
    )
    return {
        "added_parts": sorted(final_names - source_names),
        "removed_parts": sorted(source_names - final_names),
        "changed_parts": changed,
        "only_document_xml_changed": not (source_names ^ final_names) and changed == ["word/document.xml"],
    }


def repair_reference_content(input_docx: Path, output_docx: Path, plan_path: Path, report_output: Path | None = None) -> tuple[int, dict[str, Any]]:
    input_docx = input_docx.resolve()
    output_docx = output_docx.resolve()
    plan_path = plan_path.resolve()
    issues: list[str] = []
    if not input_docx.exists():
        issues.append(f"input DOCX does not exist: {input_docx}")
    if input_docx == output_docx:
        issues.append("input and output DOCX paths must differ")
    if not plan_path.exists():
        issues.append(f"reference repair plan does not exist: {plan_path}")
    if issues:
        report = {
            "schema": REPORT_SCHEMA,
            "source_docx_path": str(input_docx),
            "final_docx_path": str(output_docx),
            "plan_path": str(plan_path),
            "verdict": "fail",
            "issues": issues,
        }
        if report_output:
            report_output.parent.mkdir(parents=True, exist_ok=True)
            report_output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return 1, report
    try:
        plan = load_plan(plan_path)
        document_xml_bytes = read_package_entry(input_docx, "word/document.xml")
        document_xml = document_xml_bytes.decode("utf-8")
        repaired_xml, replacements, replacement_issues = apply_replacements(document_xml, plan)
        issues.extend(replacement_issues)
        final_contains = plan.get("final_must_contain") or []
        if isinstance(final_contains, str):
            final_contains = [final_contains]
        for token in final_contains:
            if escape(str(token)) not in repaired_xml:
                issues.append(f"final document.xml missing required text: {token}")
        if not issues:
            write_package_with_document_xml(input_docx, output_docx, repaired_xml.encode("utf-8"))
            package_scope = compare_package_scope(input_docx, output_docx)
            if not package_scope["only_document_xml_changed"]:
                issues.append("reference repair changed package parts outside word/document.xml")
        else:
            package_scope = {
                "added_parts": [],
                "removed_parts": [],
                "changed_parts": [],
                "only_document_xml_changed": False,
            }
    except Exception as exc:  # pragma: no cover - CLI defensive path
        issues.append(f"reference content repair failed: {exc}")
        replacements = []
        package_scope = {
            "added_parts": [],
            "removed_parts": [],
            "changed_parts": [],
            "only_document_xml_changed": False,
        }
    final_exists = output_docx.exists()
    report = {
        "schema": REPORT_SCHEMA,
        "source_docx_path": str(input_docx),
        "source_docx_sha256": sha256_file(input_docx) if input_docx.exists() else "",
        "final_docx_path": str(output_docx),
        "final_docx_sha256": sha256_file(output_docx) if final_exists else "",
        "plan_path": str(plan_path),
        "plan_sha256": sha256_file(plan_path) if plan_path.exists() else "",
        "replacements": replacements,
        "package_scope": package_scope,
        "verdict": "pass" if not issues else "fail",
        "issues": issues,
    }
    if report_output:
        report_output.parent.mkdir(parents=True, exist_ok=True)
        report_output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return (0 if not issues else 1), report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Bounded thesis reference-content replacement for DOCX packages.")
    parser.add_argument("--input-docx", required=True)
    parser.add_argument("--output-docx", required=True)
    parser.add_argument("--plan", required=True)
    parser.add_argument("--report-output")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    status, report = repair_reference_content(
        Path(args.input_docx),
        Path(args.output_docx),
        Path(args.plan),
        Path(args.report_output) if args.report_output else None,
    )
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    elif status == 0:
        print("reference content repair passed")
    else:
        for issue in report.get("issues", []):
            print(issue, file=sys.stderr)
    return status


if __name__ == "__main__":
    raise SystemExit(main())
