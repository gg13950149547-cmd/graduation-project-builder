#!/usr/bin/env python3
"""Close Word/WPS DOCX comments after a source-bound resolution ledger exists.

This helper changes only ``word/commentsExtended.xml``. It does not remove
teacher comments, anchors, tracked changes, media, relationships, or document
text. Use it after semantic comment fixes have been proven by detector-bound
ledger rows, then rerun the comment-resolution audit against the new output.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
import tempfile
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET


NS_W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
NS_W14 = "http://schemas.microsoft.com/office/word/2010/wordml"
NS_W15 = "http://schemas.microsoft.com/office/word/2012/wordml"
W = f"{{{NS_W}}}"
W14 = f"{{{NS_W14}}}"
W15 = f"{{{NS_W15}}}"
SCHEMA = "graduation-project-builder.close-docx-comments-from-ledger.v1"
LEDGER_SCHEMA = "graduation-project-builder.comment-resolution-ledger.v1"
FIXED_STATUSES = {"fixed", "pass", "passed", "resolved", "done", "implemented"}


ET.register_namespace("w", NS_W)
ET.register_namespace("w14", NS_W14)
ET.register_namespace("w15", NS_W15)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().lower()


def load_json(path: Path) -> dict[str, object]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"JSON root must be an object: {path}")
    return payload


def ledger_entries(payload: dict[str, object]) -> list[dict[str, object]]:
    for key in ("comments", "comment_records", "issues", "records"):
        value = payload.get(key)
        if isinstance(value, list):
            return [item for item in value if isinstance(item, dict)]
    return []


def entry_id(entry: dict[str, object]) -> str:
    return str(entry.get("comment_id") or entry.get("id") or "").strip()


def entry_status(entry: dict[str, object]) -> str:
    return str(entry.get("status") or entry.get("final_status") or entry.get("verdict") or "").strip().lower()


def entry_detector_binding(entry: dict[str, object]) -> dict[str, object]:
    binding = entry.get("detector_binding")
    return binding if isinstance(binding, dict) else {}


def read_zip_xml(zf: zipfile.ZipFile, name: str) -> ET.Element | None:
    try:
        return ET.fromstring(zf.read(name))
    except KeyError:
        return None


def collect_comment_para_ids(docx_path: Path) -> dict[str, str]:
    with zipfile.ZipFile(docx_path, "r") as zf:
        root = read_zip_xml(zf, "word/comments.xml")
    if root is None:
        return {}
    result: dict[str, str] = {}
    for comment in root.iter(f"{W}comment"):
        comment_id = str(comment.attrib.get(f"{W}id") or "").strip()
        if not comment_id:
            continue
        paragraph = next((item for item in comment.iter(f"{W}p")), None)
        para_id = ""
        if paragraph is not None:
            para_id = str(
                paragraph.attrib.get(f"{W15}paraId")
                or paragraph.attrib.get(f"{W14}paraId")
                or paragraph.attrib.get("paraId")
                or ""
            ).strip()
        result[comment_id] = para_id
    return result


def require_ledger_authorizes_closure(
    *,
    ledger: dict[str, object],
    ledger_path: Path,
    input_docx: Path,
    source_docx: Path,
    comment_para_ids: dict[str, str],
) -> None:
    issues: list[str] = []
    if ledger.get("schema") != LEDGER_SCHEMA:
        issues.append(f"ledger schema must be {LEDGER_SCHEMA}")
    final_sha = str(ledger.get("final_docx_sha256") or "").strip().lower()
    if final_sha != sha256_file(input_docx):
        issues.append("ledger final_docx_sha256 must match input DOCX before comment closure")
    source_sha = str(ledger.get("source_docx_sha256") or "").strip().lower()
    if source_sha != sha256_file(source_docx):
        issues.append("ledger source_docx_sha256 must match source DOCX before comment closure")

    entries = ledger_entries(ledger)
    by_id = {entry_id(item): item for item in entries if entry_id(item)}
    def comment_sort_key(item: tuple[str, str]) -> tuple[int, int | str]:
        comment_id = item[0]
        return (0, int(comment_id)) if comment_id.isdigit() else (1, comment_id)

    for comment_id, para_id in sorted(comment_para_ids.items(), key=comment_sort_key):
        if not para_id:
            issues.append(f"comment id {comment_id} has no comments.xml paragraph id for done-state closure")
        entry = by_id.get(comment_id)
        if entry is None:
            issues.append(f"comment id {comment_id} lacks a ledger row")
            continue
        if entry_status(entry) not in FIXED_STATUSES:
            issues.append(f"comment id {comment_id} ledger status is not fixed")
        evidence = entry.get("evidence_path") or entry.get("evidence_paths")
        if not evidence:
            issues.append(f"comment id {comment_id} lacks evidence path")
        binding = entry_detector_binding(entry)
        missing = [
            key
            for key in ("surface", "subissue", "detector_id", "detector_report_path", "detector_verdict")
            if not str(entry.get(key) or binding.get(key) or "").strip()
        ]
        if missing:
            issues.append(f"comment id {comment_id} lacks detector binding fields: {', '.join(missing)}")
    if issues:
        detail = "\n- ".join(issues)
        raise ValueError(f"comment closure is not authorized by the ledger:\n- {detail}")


def close_comments(input_docx: Path, output_docx: Path, comment_para_ids: dict[str, str]) -> dict[str, object]:
    if input_docx.resolve() == output_docx.resolve():
        raise ValueError("input and output DOCX paths must differ")
    output_docx.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(prefix=f".{output_docx.name}.", suffix=".tmp", dir=str(output_docx.parent))
    os.close(fd)
    Path(tmp_name).unlink(missing_ok=True)

    changed_count = 0
    added_count = 0
    changed_para_ids: list[str] = []
    added_para_ids: list[str] = []
    try:
        with zipfile.ZipFile(input_docx, "r") as zin, zipfile.ZipFile(tmp_name, "w", zipfile.ZIP_DEFLATED) as zout:
            comments_ext_root = read_zip_xml(zin, "word/commentsExtended.xml")
            if comments_ext_root is None:
                raise ValueError("word/commentsExtended.xml is required to close comments without removing them")
            expected_para_ids = {value for value in comment_para_ids.values() if value}
            existing_para_ids: set[str] = set()
            for item in comments_ext_root.iter(f"{W15}commentEx"):
                para_id = str(item.attrib.get(f"{W15}paraId") or item.attrib.get("paraId") or "").strip()
                if not para_id:
                    continue
                existing_para_ids.add(para_id)
                if para_id in expected_para_ids and item.attrib.get(f"{W15}done") != "1":
                    item.attrib[f"{W15}done"] = "1"
                    changed_count += 1
                    changed_para_ids.append(para_id)
            missing_para_ids = sorted(expected_para_ids - existing_para_ids)
            for para_id in missing_para_ids:
                new_item = ET.SubElement(comments_ext_root, f"{W15}commentEx")
                new_item.attrib[f"{W15}paraId"] = para_id
                new_item.attrib[f"{W15}done"] = "1"
                added_count += 1
                added_para_ids.append(para_id)

            changed_payload = ET.tostring(comments_ext_root, encoding="utf-8", xml_declaration=True)
            for item in zin.infolist():
                payload = changed_payload if item.filename == "word/commentsExtended.xml" else zin.read(item.filename)
                info = zipfile.ZipInfo(item.filename, item.date_time)
                info.comment = item.comment
                info.extra = item.extra
                info.internal_attr = item.internal_attr
                info.external_attr = item.external_attr
                info.create_system = item.create_system
                info.compress_type = item.compress_type
                zout.writestr(info, payload)
        os.replace(tmp_name, output_docx)
    finally:
        Path(tmp_name).unlink(missing_ok=True)

    return {
        "closed_comment_count": changed_count,
        "added_comment_extension_count": added_count,
        "closed_comment_para_ids": sorted(changed_para_ids),
        "added_comment_extension_para_ids": sorted(added_para_ids),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-docx", required=True, type=Path)
    parser.add_argument("--source-docx", required=True, type=Path)
    parser.add_argument("--ledger", required=True, type=Path)
    parser.add_argument("--output-docx", required=True, type=Path)
    parser.add_argument("--report-json", type=Path)
    args = parser.parse_args(argv)

    input_docx = args.input_docx.resolve()
    source_docx = args.source_docx.resolve()
    ledger_path = args.ledger.resolve()
    output_docx = args.output_docx.resolve()
    ledger = load_json(ledger_path)
    comment_para_ids = collect_comment_para_ids(input_docx)
    require_ledger_authorizes_closure(
        ledger=ledger,
        ledger_path=ledger_path,
        input_docx=input_docx,
        source_docx=source_docx,
        comment_para_ids=comment_para_ids,
    )
    close_report = close_comments(input_docx, output_docx, comment_para_ids)
    report = {
        "schema": SCHEMA,
        "generator": "scripts/close_docx_comments_from_ledger.py",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_docx_path": str(source_docx),
        "source_docx_sha256": sha256_file(source_docx),
        "input_docx_path": str(input_docx),
        "input_docx_sha256": sha256_file(input_docx),
        "ledger_path": str(ledger_path),
        "output_docx_path": str(output_docx),
        "output_docx_sha256": sha256_file(output_docx),
        "changed_parts": ["word/commentsExtended.xml"],
        "comment_count": len(comment_para_ids),
        "verdict": "pass",
        **close_report,
    }
    if args.report_json:
        args.report_json.parent.mkdir(parents=True, exist_ok=True)
        args.report_json.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
