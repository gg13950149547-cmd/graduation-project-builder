from __future__ import annotations

import argparse
import hashlib
import json
import re
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET


W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
W = f"{{{W_NS}}}"
FONT_ATTRS = ("ascii", "hAnsi", "eastAsia", "cs")
PREFERRED_ALIAS_MAP = {
    "simsun": "\u5b8b\u4f53",
    "simhei": "\u9ed1\u4f53",
    "kaiti": "\u6977\u4f53",
    "fangsong": "\u4eff\u5b8b",
    "\u5b8b\u4f53": "\u5b8b\u4f53",
    "\u9ed1\u4f53": "\u9ed1\u4f53",
    "\u6977\u4f53": "\u6977\u4f53",
    "\u4eff\u5b8b": "\u4eff\u5b8b",
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def preferred_font(value: str) -> str:
    parts = [part.strip() for part in str(value or "").split(";") if part.strip()]
    if not parts:
        return value
    for part in parts:
        mapped = PREFERRED_ALIAS_MAP.get(part.lower()) or PREFERRED_ALIAS_MAP.get(part)
        if mapped:
            return mapped
    for part in parts:
        if any(ord(ch) > 127 for ch in part):
            return part
    return parts[0]


def xml_font_alias_issues(xml_bytes: bytes, part_name: str) -> tuple[bytes, list[dict[str, str]], bool]:
    try:
        root = ET.fromstring(xml_bytes)
    except ET.ParseError:
        return xml_bytes, [], False
    issues: list[dict[str, str]] = []
    changed = False
    for rfonts in root.iter(W + "rFonts"):
        for attr_name in FONT_ATTRS:
            qname = W + attr_name
            value = rfonts.attrib.get(qname)
            if value is None or ";" not in value:
                continue
            replacement = preferred_font(value)
            issues.append(
                {
                    "part": part_name,
                    "attribute": attr_name,
                    "value": value,
                    "replacement": replacement,
                }
            )
            rfonts.set(qname, replacement)
            changed = True
    if not changed:
        return xml_bytes, issues, False
    return ET.tostring(root, encoding="utf-8", xml_declaration=True), issues, True


def repair_docx_font_alias_slots(input_docx: Path, output_docx: Path | None = None) -> dict[str, object]:
    input_docx = Path(input_docx).resolve()
    output_docx = Path(output_docx).resolve() if output_docx else None
    if output_docx is not None and output_docx == input_docx:
        raise RuntimeError("output DOCX must be a new review-copy path")
    all_issues: list[dict[str, str]] = []
    changed_parts: list[str] = []
    if output_docx is None:
        with zipfile.ZipFile(input_docx, "r") as zf:
            for name in zf.namelist():
                if name.startswith("word/") and name.endswith(".xml"):
                    _data, issues, _changed = xml_font_alias_issues(zf.read(name), name)
                    all_issues.extend(issues)
        return {
            "schema": "graduation-project-builder.font-alias-slots.v1",
            "input_docx_path": str(input_docx),
            "input_docx_sha256": sha256(input_docx),
            "output_docx_path": None,
            "output_docx_sha256": None,
            "alias_issue_count": len(all_issues),
            "changed_parts": [],
            "issues": all_issues,
            "verdict": "pass" if not all_issues else "fail",
        }

    output_docx.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(input_docx, "r") as zin, zipfile.ZipFile(output_docx, "w", compression=zipfile.ZIP_DEFLATED) as zout:
        for info in zin.infolist():
            data = zin.read(info.filename)
            if info.filename.startswith("word/") and info.filename.endswith(".xml"):
                data, issues, changed = xml_font_alias_issues(data, info.filename)
                all_issues.extend(issues)
                if changed:
                    changed_parts.append(info.filename)
            zout.writestr(info, data)
    return {
        "schema": "graduation-project-builder.font-alias-slots.v1",
        "input_docx_path": str(input_docx),
        "input_docx_sha256": sha256(input_docx),
        "output_docx_path": str(output_docx),
        "output_docx_sha256": sha256(output_docx),
        "alias_issue_count": len(all_issues),
        "changed_parts": sorted(changed_parts),
        "issues": all_issues,
        "verdict": "pass",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output")
    parser.add_argument("--report-json")
    parser.add_argument("--fail-on-alias", action="store_true")
    args = parser.parse_args()
    report = repair_docx_font_alias_slots(
        Path(args.input),
        Path(args.output) if args.output else None,
    )
    if args.report_json:
        report_path = Path(args.report_json).resolve()
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"verdict": report["verdict"], "alias_issue_count": report["alias_issue_count"]}, ensure_ascii=False))
    if args.fail_on_alias and int(report["alias_issue_count"]) > 0:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
