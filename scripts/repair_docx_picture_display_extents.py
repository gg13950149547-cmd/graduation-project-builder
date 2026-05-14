#!/usr/bin/env python3
"""Apply transaction-owned display extent fixes to selected DOCX pictures.

This helper rewrites only ``word/document.xml``. Each resize row must identify
the existing image relationship id and its adjacent caption so repeated media
uses are not changed accidentally.
"""

from __future__ import annotations

import argparse
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
import os
import re
import tempfile
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

from thesis_figure_contract import (
    A_NS,
    PR_NS,
    R_NS,
    W_NS,
    WP_NS,
    docx_drawing_object_manifest,
    validate_figure_manifest,
)

MC_NS = "http://schemas.openxmlformats.org/markup-compatibility/2006"
W14_NS = "http://schemas.microsoft.com/office/word/2010/wordml"
W15_NS = "http://schemas.microsoft.com/office/word/2012/wordml"
WP14_NS = "http://schemas.microsoft.com/office/word/2010/wordprocessingDrawing"
WPS_NS = "http://schemas.microsoft.com/office/word/2010/wordprocessingShape"
VML_NS = "urn:schemas-microsoft-com:vml"
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


def element_sha256(element: ET.Element) -> str:
    return hashlib.sha256(ET.tostring(element, encoding="utf-8")).hexdigest().upper()


def paragraph_text(paragraph: ET.Element) -> str:
    return "".join(node.text or "" for node in paragraph.findall(f".//{{{W_NS}}}t")).strip()


def next_non_empty_text(paragraphs: list[ET.Element], index: int, search_limit: int = 5) -> str:
    for candidate in paragraphs[index + 1 : index + search_limit]:
        text = paragraph_text(candidate)
        if text:
            return text
    return ""


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


def rel_targets(rels_payload: bytes) -> dict[str, str]:
    root = ET.fromstring(rels_payload)
    return {
        rel.attrib.get("Id", ""): rel.attrib.get("Target", "")
        for rel in root.findall(f"{{{PR_NS}}}Relationship")
        if rel.attrib.get("Id")
    }


def normalized_record_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace").replace("\\", "/").lower()


def path_bound_in_record(record_text: str, path: Path) -> bool:
    normalized = str(path.resolve()).replace("\\", "/").lower()
    return normalized in record_text or path.name.lower() in record_text


def validate_transaction_record_binding(
    transaction_record: Path,
    *,
    source_docx: Path,
    output_docx: Path,
    figure_manifest: Path,
) -> list[str]:
    text = normalized_record_text(transaction_record)
    issues: list[str] = []
    if not path_bound_in_record(text, source_docx) or sha256_file(source_docx).lower() not in text:
        issues.append("transaction record does not bind the source DOCX path and SHA256")
    if not path_bound_in_record(text, output_docx):
        issues.append("transaction record does not bind the intended final/output DOCX path")
    if not path_bound_in_record(text, figure_manifest):
        issues.append("transaction record does not bind the figure manifest path")
    return issues


def _emu_to_points(value: int) -> float:
    return value / 12700.0


def _set_vml_style_length(style_text: str, key: str, emu: int) -> str:
    replacement = f"{key}:{_emu_to_points(emu):.2f}pt"
    parts = [part for part in (style_text or "").split(";") if part != ""]
    updated: list[str] = []
    replaced = False
    for part in parts:
        if ":" not in part:
            updated.append(part)
            continue
        name, _value = part.split(":", 1)
        if name.strip().lower() == key:
            updated.append(replacement)
            replaced = True
        else:
            updated.append(part)
    if not replaced:
        updated.append(replacement)
    return ";".join(updated)


def paragraph_image_rids(paragraph: ET.Element) -> set[str]:
    rids = {
        blip.attrib.get(f"{{{R_NS}}}embed", "")
        for blip in paragraph.findall(f".//{{{A_NS}}}blip")
    }
    rids.update(
        image.attrib.get(f"{{{R_NS}}}id", "") or image.attrib.get(f"{{{R_NS}}}embed", "")
        for image in paragraph.findall(f".//{{{VML_NS}}}imagedata")
    )
    return {rid for rid in rids if rid}


def update_extents(container: ET.Element, cx: int, cy: int) -> int:
    updates = 0
    for extent in container.findall(f".//{{{WP_NS}}}extent"):
        extent.attrib["cx"] = str(cx)
        extent.attrib["cy"] = str(cy)
        updates += 1
    for extent in container.findall(f".//{{{A_NS}}}ext"):
        if "cx" in extent.attrib and "cy" in extent.attrib:
            extent.attrib["cx"] = str(cx)
            extent.attrib["cy"] = str(cy)
            updates += 1
    for shape in container.findall(f".//{{{VML_NS}}}shape") + container.findall(f".//{{{VML_NS}}}rect"):
        if shape.find(f".//{{{VML_NS}}}imagedata") is None:
            continue
        style = shape.attrib.get("style", "")
        style = _set_vml_style_length(style, "width", cx)
        style = _set_vml_style_length(style, "height", cy)
        shape.attrib["style"] = style
        updates += 1
    return updates


def repair_docx(source: Path, output: Path, plan: dict[str, object]) -> dict[str, object]:
    if source.resolve() == output.resolve():
        raise ValueError("input and output DOCX paths must be different")
    rows = plan.get("resizes")
    if not isinstance(rows, list) or not rows:
        raise ValueError("plan.resizes must contain at least one resize row")
    output.parent.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(source, "r") as zin:
        root = ET.fromstring(zin.read("word/document.xml"))
        target_by_rid = rel_targets(zin.read("word/_rels/document.xml.rels"))
        body = root.find(f".//{{{W_NS}}}body")
        if body is None:
            raise ValueError("word/document.xml has no body")
        paragraphs = [child for child in list(body) if child.tag == f"{{{W_NS}}}p"]
        changes: list[dict[str, object]] = []
        for row in rows:
            if not isinstance(row, dict):
                raise ValueError("each resize row must be an object")
            rid = str(row.get("rid") or "")
            caption = str(row.get("caption") or "")
            cx = int(row.get("cx") or 0)
            cy = int(row.get("cy") or 0)
            if not rid or not caption or cx <= 0 or cy <= 0:
                raise ValueError("each resize row requires rid, caption, cx, and cy")
            matches: list[tuple[int, ET.Element, str]] = []
            for index, paragraph in enumerate(paragraphs):
                paragraph_rids = paragraph_image_rids(paragraph)
                if rid not in paragraph_rids:
                    continue
                next_text = next_non_empty_text(paragraphs, index)
                if next_text == caption or next_text.startswith(caption):
                    matches.append((index, paragraph, next_text))
            if len(matches) != 1:
                raise ValueError(f"resize row for {rid} / {caption[:40]} selected {len(matches)} paragraphs")
            index, paragraph, next_text = matches[0]
            before = deepcopy(paragraph)
            before_extents = [
                {"cx": extent.attrib.get("cx", ""), "cy": extent.attrib.get("cy", "")}
                for extent in paragraph.findall(f".//{{{WP_NS}}}extent")
            ]
            updates = update_extents(paragraph, cx, cy)
            if updates == 0:
                raise ValueError(f"resize row for {rid} found no extents to update")
            changes.append(
                {
                    "paragraph_index": index,
                    "rid": rid,
                    "media_target": target_by_rid.get(rid, ""),
                    "caption": next_text,
                    "before_extents": before_extents,
                    "after_extent": {"cx": str(cx), "cy": str(cy)},
                    "before_drawing_sha256": element_sha256(before),
                    "after_drawing_sha256": element_sha256(paragraph),
                    "updated_extent_nodes": updates,
                    "authorization": str(row.get("authorization") or plan.get("authorization") or ""),
                }
            )

        ET.register_namespace("w", W_NS)
        ET.register_namespace("a", A_NS)
        ET.register_namespace("wp", WP_NS)
        ET.register_namespace("r", R_NS)
        document_xml = ET.tostring(root, encoding="unicode", xml_declaration=True)
        document_xml = inject_missing_ignorable_namespaces(document_xml, root)
        document_payload = document_xml.encode("utf-8")

        fd, tmp_name = tempfile.mkstemp(prefix=f".{output.name}.", suffix=".tmp", dir=str(output.parent))
        os.close(fd)
        Path(tmp_name).unlink(missing_ok=True)
        try:
            with zipfile.ZipFile(source, "r") as zin2, zipfile.ZipFile(tmp_name, "w", zipfile.ZIP_DEFLATED) as zout:
                for item in zin2.infolist():
                    payload = document_payload if item.filename == "word/document.xml" else zin2.read(item.filename)
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
        "schema": "graduation-project-builder.docx-picture-display-extents-repair.v1",
        "generator": "scripts/repair_docx_picture_display_extents.py",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_docx_path": str(source),
        "source_docx_sha256": sha256_file(source),
        "final_docx_path": str(output),
        "final_docx_sha256": sha256_file(output),
        "changed_part": "word/document.xml",
        "resize_count": len(changes),
        "resizes": changes,
        "verdict": "pass",
    }


def _normalized_text(value: object) -> str:
    return re.sub(r"\s+", " ", str(value or "").strip())


def _drawing_row_for_change(
    drawing_manifest: dict[str, dict[str, object]],
    *,
    rid: str,
    caption: str,
) -> dict[str, object] | None:
    caption_norm = _normalized_text(caption)
    matches: list[dict[str, object]] = []
    for row in drawing_manifest.values():
        relationship_ids = str(row.get("relationship_ids") or "")
        next_text = _normalized_text(row.get("next_text"))
        if rid not in relationship_ids:
            continue
        if next_text == caption_norm or next_text.startswith(caption_norm):
            matches.append(row)
    if len(matches) == 1:
        return matches[0]
    return None


def _manifest_entry_for_caption(manifest: dict[str, object], caption: str) -> dict[str, object] | None:
    caption_norm = _normalized_text(caption)
    figures = manifest.get("figures")
    if not isinstance(figures, dict):
        return None
    matches: list[dict[str, object]] = []
    for entry in figures.values():
        if not isinstance(entry, dict):
            continue
        entry_caption = _normalized_text(entry.get("caption"))
        if entry_caption == caption_norm or caption_norm.startswith(entry_caption) or entry_caption.startswith(caption_norm):
            matches.append(entry)
    if len(matches) == 1:
        return matches[0]
    return None


def bind_manifest_to_display_extent_repair(
    manifest: dict[str, object],
    *,
    source_docx: Path,
    final_docx: Path,
    report: dict[str, object],
    report_json: Path | None,
    transaction_record: Path,
) -> list[str]:
    """Attach drawing-hash authorization for this bounded display resize."""

    issues: list[str] = []
    source_drawings = docx_drawing_object_manifest(source_docx)
    final_drawings = docx_drawing_object_manifest(final_docx)
    manifest["source_docx_path"] = str(source_docx)
    manifest["source_docx_sha256"] = sha256_file(source_docx)
    manifest["final_docx_path"] = str(final_docx)
    manifest["final_docx_sha256"] = sha256_file(final_docx)
    manifest.setdefault("source_docx_role", "current_manuscript")
    manifest["display_extent_repair_report"] = str(report_json) if report_json else ""
    manifest["display_extent_transaction_record"] = str(transaction_record)

    for change in report.get("resizes", []):
        if not isinstance(change, dict):
            continue
        rid = str(change.get("rid") or "")
        caption = str(change.get("caption") or "")
        entry = _manifest_entry_for_caption(manifest, caption)
        if entry is None:
            issues.append(f"manifest has no unique figure entry for resized caption: {caption}")
            continue
        source_row = _drawing_row_for_change(source_drawings, rid=rid, caption=caption)
        final_row = _drawing_row_for_change(final_drawings, rid=rid, caption=caption)
        if source_row is None or final_row is None:
            issues.append(f"could not bind drawing manifest rows for resized caption: {caption}")
            continue
        entry["display_extent_resize_intent"] = "resize_display_extent"
        entry["resize_authorization_source"] = str(change.get("authorization") or "")
        entry["resize_authorization_scope"] = "display extent only; media relationship and media bytes preserved"
        entry["original_drawing_sha256"] = str(source_row.get("sha256") or "")
        entry["final_drawing_sha256"] = str(final_row.get("sha256") or "")
        entry["original_drawing_owner_part"] = str(source_row.get("story_part") or "word/document.xml")
        entry["final_drawing_owner_part"] = str(final_row.get("story_part") or "word/document.xml")
        entry["original_extent_signature"] = str(source_row.get("extent_signature") or "")
        entry["final_extent_signature"] = str(final_row.get("extent_signature") or "")
        entry["display_extent_resize_verdict"] = "pass"
    return issues


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-docx", required=True, type=Path)
    parser.add_argument("--output-docx", required=True, type=Path)
    parser.add_argument("--plan-json", required=True, type=Path)
    parser.add_argument("--figure-manifest", required=True, type=Path)
    parser.add_argument("--source-docx", required=True, type=Path)
    parser.add_argument("--transaction-record", required=True, type=Path)
    parser.add_argument("--report-json", type=Path)
    args = parser.parse_args()

    source_docx = args.source_docx.resolve()
    if not source_docx.exists():
        raise SystemExit(f"--source-docx does not exist: {source_docx}")
    if source_docx != args.input_docx.resolve():
        raise SystemExit("--source-docx must match --input-docx for transaction-owned display extent repair")
    if not args.transaction_record.exists():
        raise SystemExit(f"--transaction-record does not exist: {args.transaction_record}")
    if not args.figure_manifest.exists():
        raise SystemExit(f"--figure-manifest does not exist: {args.figure_manifest}")
    transaction_issues = validate_transaction_record_binding(
        args.transaction_record.resolve(),
        source_docx=source_docx,
        output_docx=args.output_docx.resolve(),
        figure_manifest=args.figure_manifest.resolve(),
    )
    if transaction_issues:
        raise SystemExit("; ".join(transaction_issues))

    plan = json.loads(args.plan_json.read_text(encoding="utf-8"))
    rows = plan.get("resizes")
    if not isinstance(rows, list) or not rows:
        raise SystemExit("plan.resizes must contain at least one resize row")
    for index, row in enumerate(rows, start=1):
        if not isinstance(row, dict):
            raise SystemExit(f"plan.resizes[{index}] must be an object")
        if not str(row.get("authorization") or plan.get("authorization") or "").strip():
            raise SystemExit(f"plan.resizes[{index}] missing explicit drawing resize authorization")

    manifest = json.loads(args.figure_manifest.read_text(encoding="utf-8"))
    report = repair_docx(args.input_docx, args.output_docx, plan)
    manifest_binding_issues = bind_manifest_to_display_extent_repair(
        manifest,
        source_docx=source_docx,
        final_docx=args.output_docx.resolve(),
        report=report,
        report_json=args.report_json,
        transaction_record=args.transaction_record.resolve(),
    )
    args.figure_manifest.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    manifest_issues = validate_figure_manifest(
        manifest,
        final_docx=args.output_docx,
        source_docx=source_docx,
        manifest_path=args.figure_manifest,
    )
    all_manifest_issues = manifest_binding_issues + manifest_issues
    if all_manifest_issues:
        report["verdict"] = "fail"
        report["figure_manifest_issues"] = all_manifest_issues
        if args.report_json:
            args.report_json.parent.mkdir(parents=True, exist_ok=True)
            args.report_json.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 1
    report["figure_manifest_path"] = str(args.figure_manifest)
    report["transaction_record_path"] = str(args.transaction_record)
    if args.report_json:
        args.report_json.parent.mkdir(parents=True, exist_ok=True)
        args.report_json.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
