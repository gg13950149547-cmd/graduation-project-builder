#!/usr/bin/env python3
"""Create a clean DOCX preview by removing comment anchors and comment parts.

This is a promotion helper, not a semantic comment-resolution auditor. Use it
only after a separate comment-resolution ledger has already recorded why the
comments may be closed. The helper preserves all non-comment package parts.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
import posixpath
import re
import tempfile
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET


W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
R_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
PR_NS = "http://schemas.openxmlformats.org/package/2006/relationships"
CT_NS = "http://schemas.openxmlformats.org/package/2006/content-types"
MC_NS = "http://schemas.openxmlformats.org/markup-compatibility/2006"
W14_NS = "http://schemas.microsoft.com/office/word/2010/wordml"
W15_NS = "http://schemas.microsoft.com/office/word/2012/wordml"
WP14_NS = "http://schemas.microsoft.com/office/word/2010/wordprocessingDrawing"
WPS_NS = "http://schemas.microsoft.com/office/word/2010/wordprocessingShape"

COMMENT_ELEMENT_NAMES = {"commentRangeStart", "commentRangeEnd", "commentReference"}
COMMENT_PART_PATTERNS = (
    "word/comments.xml",
    "word/commentsExtended.xml",
    "word/commentsIds.xml",
    "word/people.xml",
)
COMMENT_REL_MARKERS = (
    "/comments",
    "/commentsExtended",
    "/commentsIds",
    "/people",
)
IGNORABLE_PREFIX_URIS = {
    "w14": W14_NS,
    "w15": W15_NS,
    "wp14": WP14_NS,
    "wps": WPS_NS,
}


for prefix, uri in {
    "w": W_NS,
    "r": R_NS,
    "mc": MC_NS,
    "w14": W14_NS,
    "w15": W15_NS,
    "wp14": WP14_NS,
}.items():
    ET.register_namespace(prefix, uri)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1] if tag.startswith("{") else tag


def remove_comment_elements(root: ET.Element) -> int:
    removed = 0
    for parent in list(root.iter()):
        for child in list(parent):
            if local_name(child.tag) in COMMENT_ELEMENT_NAMES:
                parent.remove(child)
                removed += 1
    return removed


def strip_empty_comment_runs(root: ET.Element) -> int:
    removed = 0
    for parent in list(root.iter()):
        for child in list(parent):
            if child.tag != f"{{{W_NS}}}r":
                continue
            has_visible_payload = False
            for descendant in child.iter():
                if descendant is child:
                    continue
                if local_name(descendant.tag) not in {"rPr"}:
                    has_visible_payload = True
                    break
            if not has_visible_payload:
                parent.remove(child)
                removed += 1
    return removed


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


def is_comment_part(name: str) -> bool:
    if name in COMMENT_PART_PATTERNS:
        return True
    if name.startswith("word/_rels/comments") and name.endswith(".rels"):
        return True
    return False


def package_target_name(current_part: str, target: str) -> str:
    target = target.replace("\\", "/")
    if target.startswith("/"):
        return target.lstrip("/")
    base = posixpath.dirname(current_part)
    if base.endswith("_rels"):
        base = posixpath.dirname(base)
    return posixpath.normpath(posixpath.join(base, target))


def strip_comment_relationships(payload: bytes, rel_part_name: str) -> tuple[bytes, list[str]]:
    root = ET.fromstring(payload)
    removed: list[str] = []
    for rel in list(root.findall(f"{{{PR_NS}}}Relationship")):
        rel_type = rel.attrib.get("Type", "")
        target = rel.attrib.get("Target", "")
        full_target = package_target_name(rel_part_name.replace("_rels/", ""), target)
        if any(marker in rel_type for marker in COMMENT_REL_MARKERS) or is_comment_part(full_target):
            removed.append(rel.attrib.get("Id", ""))
            root.remove(rel)
    if not removed:
        return payload, []
    ET.register_namespace("", PR_NS)
    return ET.tostring(root, encoding="utf-8", xml_declaration=True), removed


def strip_content_type_overrides(payload: bytes) -> tuple[bytes, list[str]]:
    root = ET.fromstring(payload)
    removed: list[str] = []
    for override in list(root.findall(f"{{{CT_NS}}}Override")):
        part_name = override.attrib.get("PartName", "").lstrip("/")
        if is_comment_part(part_name):
            removed.append(part_name)
            root.remove(override)
    if not removed:
        return payload, []
    ET.register_namespace("", CT_NS)
    return ET.tostring(root, encoding="utf-8", xml_declaration=True), removed


def repair_xml_part(payload: bytes) -> tuple[bytes, dict[str, int]]:
    root = ET.fromstring(payload)
    removed_markers = remove_comment_elements(root)
    removed_runs = strip_empty_comment_runs(root)
    if not removed_markers and not removed_runs:
        return payload, {"removed_comment_markers": 0, "removed_empty_comment_runs": 0}
    xml_text = ET.tostring(root, encoding="unicode", xml_declaration=True)
    xml_text = inject_missing_ignorable_namespaces(xml_text, root)
    return xml_text.encode("utf-8"), {
        "removed_comment_markers": removed_markers,
        "removed_empty_comment_runs": removed_runs,
    }


def strip_docx(source: Path, output: Path) -> dict[str, object]:
    if source.resolve() == output.resolve():
        raise ValueError("input and output DOCX paths must be different")
    output.parent.mkdir(parents=True, exist_ok=True)
    changed_parts: list[str] = []
    removed_parts: list[str] = []
    xml_reports: dict[str, dict[str, int]] = {}
    removed_relationships: dict[str, list[str]] = {}
    removed_content_types: list[str] = []

    fd, tmp_name = tempfile.mkstemp(prefix=f".{output.name}.", suffix=".tmp", dir=str(output.parent))
    os.close(fd)
    Path(tmp_name).unlink(missing_ok=True)
    try:
        with zipfile.ZipFile(source, "r") as zin, zipfile.ZipFile(tmp_name, "w", zipfile.ZIP_DEFLATED) as zout:
            for item in zin.infolist():
                if is_comment_part(item.filename):
                    removed_parts.append(item.filename)
                    continue
                payload = zin.read(item.filename)
                if item.filename == "[Content_Types].xml":
                    payload, removed = strip_content_type_overrides(payload)
                    if removed:
                        changed_parts.append(item.filename)
                        removed_content_types.extend(removed)
                elif item.filename.endswith(".rels"):
                    payload, removed = strip_comment_relationships(payload, item.filename)
                    if removed:
                        changed_parts.append(item.filename)
                        removed_relationships[item.filename] = removed
                elif item.filename.startswith("word/") and item.filename.endswith(".xml"):
                    try:
                        payload, report = repair_xml_part(payload)
                    except ET.ParseError:
                        report = {"removed_comment_markers": 0, "removed_empty_comment_runs": 0}
                    if report["removed_comment_markers"] or report["removed_empty_comment_runs"]:
                        changed_parts.append(item.filename)
                        xml_reports[item.filename] = report
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
        "schema": "graduation-project-builder.docx-comments-clean-preview.v1",
        "generator": "scripts/strip_docx_comments_preview.py",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_docx_path": str(source),
        "source_docx_sha256": sha256_file(source),
        "final_docx_path": str(output),
        "final_docx_sha256": sha256_file(output),
        "changed_parts": sorted(set(changed_parts)),
        "removed_parts": removed_parts,
        "xml_reports": xml_reports,
        "removed_relationships": removed_relationships,
        "removed_content_type_overrides": removed_content_types,
        "verdict": "pass",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-docx", required=True, type=Path)
    parser.add_argument("--output-docx", required=True, type=Path)
    parser.add_argument("--report-json", type=Path)
    args = parser.parse_args()

    report = strip_docx(args.input_docx, args.output_docx)
    if args.report_json:
        args.report_json.parent.mkdir(parents=True, exist_ok=True)
        args.report_json.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
