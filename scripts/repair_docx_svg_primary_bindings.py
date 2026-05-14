#!/usr/bin/env python3
"""Repair DOCX SVG-primary bindings that point at empty placeholder SVGs.

The helper is intentionally narrow: it rewrites only ``word/document.xml``.
When an ``asvg:svgBlip`` points to a renderer-unsafe ``*-2.svg`` placeholder
and a same-stem real SVG relationship already exists in the package, the helper
rebinds the SVG primary relationship to the real SVG while preserving the PNG
fallback relationship and all media files.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
import posixpath
import re
import shutil
import tempfile
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

from thesis_figure_contract import A_NS, ASVG_NS, PR_NS, R_NS

MC_NS = "http://schemas.openxmlformats.org/markup-compatibility/2006"
W14_NS = "http://schemas.microsoft.com/office/word/2010/wordml"
W15_NS = "http://schemas.microsoft.com/office/word/2012/wordml"
WP14_NS = "http://schemas.microsoft.com/office/word/2010/wordprocessingDrawing"
WPS_NS = "http://schemas.microsoft.com/office/word/2010/wordprocessingShape"
IGNORABLE_PREFIX_URIS = {
    "w14": W14_NS,
    "w15": W15_NS,
    "wp14": WP14_NS,
    "wps": WPS_NS,
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest().upper()


def target_to_package_name(target: str) -> str:
    target = (target or "").lstrip("/")
    if target.startswith("word/"):
        return target
    if target.startswith("media/"):
        return "word/" + target
    return posixpath.normpath("word/" + target)


def renderer_safe_svg(payload: bytes) -> tuple[bool, str]:
    if len(payload) < 512:
        return False, "svg payload is too small to contain a rendered diagram"
    text = payload.decode("utf-8", errors="replace").lower()
    if "text is not svg - cannot display" in text:
        return False, "svg contains draw.io fallback notice"
    try:
        root = ET.fromstring(payload)
    except ET.ParseError as exc:
        return False, f"svg parse error: {exc}"
    graphic_children = [
        child
        for child in root.iter()
        if child is not root
        and child.tag.rsplit("}", 1)[-1].lower()
        in {"path", "rect", "circle", "ellipse", "line", "polyline", "polygon", "text", "image", "g"}
    ]
    if not graphic_children:
        return False, "svg contains no drawable child elements"
    return True, "pass"


def remove_dash_two(target: str) -> str | None:
    suffix = "-2.svg"
    if target.lower().endswith(suffix):
        return target[: -len(suffix)] + ".svg"
    return None


def inject_missing_ignorable_namespaces(xml_text: str, root: ET.Element) -> str:
    value = root.attrib.get(f"{{{MC_NS}}}Ignorable", "")
    prefixes = {token for token in re.split(r"\s+", value.strip()) if token}
    missing = [prefix for prefix in sorted(prefixes) if prefix in IGNORABLE_PREFIX_URIS and f"xmlns:{prefix}=" not in xml_text]
    if not missing:
        return xml_text
    match = re.search(r"<(?!\?)(?!!--)([A-Za-z_][\w.-]*:)?[A-Za-z_][\w.-]*(?:\s[^<>]*)?>", xml_text)
    if not match:
        return xml_text
    insertion = "".join(f' xmlns:{prefix}="{IGNORABLE_PREFIX_URIS[prefix]}"' for prefix in missing)
    insert_at = match.end() - (2 if xml_text[match.end() - 2 : match.end()] == "/>" else 1)
    return xml_text[:insert_at] + insertion + xml_text[insert_at:]


def repair_docx(source: Path, output: Path) -> dict[str, object]:
    if source.resolve() == output.resolve():
        raise ValueError("input and output DOCX paths must be different")
    output.parent.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(source, "r") as zin:
        rel_root = ET.fromstring(zin.read("word/_rels/document.xml.rels"))
        doc_root = ET.fromstring(zin.read("word/document.xml"))
        package_names = set(zin.namelist())
        rel_by_id = {rel.attrib.get("Id", ""): rel for rel in rel_root.findall(f"{{{PR_NS}}}Relationship")}
        rel_by_target = {rel.attrib.get("Target", ""): rel for rel in rel_root.findall(f"{{{PR_NS}}}Relationship")}
        svg_payload_by_target: dict[str, bytes] = {}
        for rel in rel_by_id.values():
            target = rel.attrib.get("Target", "")
            if not target.lower().endswith(".svg"):
                continue
            package_name = target_to_package_name(target)
            if package_name in package_names:
                svg_payload_by_target[target] = zin.read(package_name)

        changes: list[dict[str, str]] = []
        for blip in doc_root.findall(f".//{{{A_NS}}}blip"):
            svg_blip = blip.find(f".//{{{ASVG_NS}}}svgBlip")
            if svg_blip is None:
                continue
            svg_rid = svg_blip.attrib.get(f"{{{R_NS}}}embed", "")
            svg_rel = rel_by_id.get(svg_rid)
            if svg_rel is None:
                continue
            svg_target = svg_rel.attrib.get("Target", "")
            payload = svg_payload_by_target.get(svg_target, b"")
            safe, issue = renderer_safe_svg(payload)
            if safe:
                continue
            preferred_target = remove_dash_two(svg_target)
            if not preferred_target:
                continue
            preferred_rel = rel_by_target.get(preferred_target)
            preferred_payload = svg_payload_by_target.get(preferred_target, b"")
            preferred_safe, preferred_issue = renderer_safe_svg(preferred_payload)
            if preferred_rel is None or not preferred_safe:
                continue
            svg_blip.attrib[f"{{{R_NS}}}embed"] = preferred_rel.attrib["Id"]
            changes.append(
                {
                    "old_svg_rid": svg_rid,
                    "old_svg_target": svg_target,
                    "old_svg_sha256": sha256_bytes(payload) if payload else "",
                    "old_svg_issue": issue,
                    "new_svg_rid": preferred_rel.attrib["Id"],
                    "new_svg_target": preferred_target,
                    "new_svg_sha256": sha256_bytes(preferred_payload),
                    "new_svg_issue": preferred_issue,
                }
            )

        ET.register_namespace("a", A_NS)
        ET.register_namespace("asvg", ASVG_NS)
        ET.register_namespace("r", R_NS)
        document_xml = ET.tostring(doc_root, encoding="unicode", xml_declaration=True)
        document_xml = inject_missing_ignorable_namespaces(document_xml, doc_root)
        document_payload = document_xml.encode("utf-8")

        fd, tmp_name = tempfile.mkstemp(prefix=f".{output.name}.", suffix=".tmp", dir=str(output.parent))
        os.close(fd)
        Path(tmp_name).unlink(missing_ok=True)
        try:
            with zipfile.ZipFile(source, "r") as zin2, zipfile.ZipFile(tmp_name, "w", zipfile.ZIP_DEFLATED) as zout:
                for item in zin2.infolist():
                    if item.filename == "word/document.xml" and changes:
                        payload = document_payload
                    else:
                        payload = zin2.read(item.filename)
                    info = zipfile.ZipInfo(item.filename, item.date_time)
                    info.comment = item.comment
                    info.extra = item.extra
                    info.internal_attr = item.internal_attr
                    info.external_attr = item.external_attr
                    info.create_system = item.create_system
                    info.compress_type = item.compress_type
                    zout.writestr(info, payload)
            os.replace(tmp_name, output)
        finally:
            Path(tmp_name).unlink(missing_ok=True)

    return {
        "schema": "graduation-project-builder.docx-svg-primary-binding-repair.v1",
        "generator": "scripts/repair_docx_svg_primary_bindings.py",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_docx_path": str(source),
        "source_docx_sha256": sha256_file(source),
        "final_docx_path": str(output),
        "final_docx_sha256": sha256_file(output),
        "changed_part": "word/document.xml" if changes else "",
        "rebound_svg_primary_count": len(changes),
        "bindings": changes,
        "verdict": "pass" if changes else "pass-noop",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-docx", required=True, type=Path)
    parser.add_argument("--output-docx", required=True, type=Path)
    parser.add_argument("--report-json", type=Path)
    args = parser.parse_args()

    report = repair_docx(args.input_docx, args.output_docx)
    if args.report_json:
        args.report_json.parent.mkdir(parents=True, exist_ok=True)
        args.report_json.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
