#!/usr/bin/env python3
"""Bounded DOCX repair for submission-blocking thesis surfaces.

This helper is intentionally narrow: it patches only ``word/document.xml`` in a
package-preserving way and reports source/final SHA values. It does not touch
media, relationships, comments, citations, styles, headers, or footers.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
import shutil
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from xml.etree import ElementTree as ET


W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
XML_NS = "http://www.w3.org/XML/1998/namespace"
NS = {"w": W_NS}
ET.register_namespace("w", W_NS)


def qn(local: str) -> str:
    prefix, name = local.split(":", 1)
    if prefix == "w":
        return f"{{{W_NS}}}{name}"
    if prefix == "xml":
        return f"{{{XML_NS}}}{name}"
    raise ValueError(local)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def paragraph_text(paragraph: ET.Element) -> str:
    return "".join(node.text or "" for node in paragraph.iter(qn("w:t")))


def paragraph_style_id(paragraph: ET.Element) -> str:
    node = paragraph.find("./w:pPr/w:pStyle", NS)
    return node.attrib.get(qn("w:val"), "") if node is not None else ""


def body_paragraphs(body: ET.Element) -> list[ET.Element]:
    return [child for child in list(body) if child.tag == qn("w:p")]


def clone_run_rpr(paragraph: ET.Element) -> ET.Element | None:
    rpr = paragraph.find(".//w:r/w:rPr", NS)
    return copy.deepcopy(rpr) if rpr is not None else None


def make_text_run(text: str, rpr: ET.Element | None = None) -> ET.Element:
    run = ET.Element(qn("w:r"))
    if rpr is not None:
        run.append(copy.deepcopy(rpr))
    t = ET.SubElement(run, qn("w:t"))
    if text.startswith(" ") or text.endswith(" "):
        t.set(qn("xml:space"), "preserve")
    t.text = text
    return run


def make_tab_run(rpr: ET.Element | None = None) -> ET.Element:
    run = ET.Element(qn("w:r"))
    if rpr is not None:
        run.append(copy.deepcopy(rpr))
    ET.SubElement(run, qn("w:tab"))
    return run


def set_paragraph_runs(paragraph: ET.Element, runs: list[ET.Element]) -> None:
    for child in list(paragraph):
        if child.tag != qn("w:pPr"):
            paragraph.remove(child)
    for run in runs:
        paragraph.append(run)


def make_toc_entry_from(template: ET.Element, label: str, page: str) -> ET.Element:
    paragraph = copy.deepcopy(template)
    rpr = clone_run_rpr(template)
    set_paragraph_runs(
        paragraph,
        [make_text_run(label, rpr), make_tab_run(rpr), make_text_run(page, rpr)],
    )
    return paragraph


def normalize_square_placeholders(root: ET.Element) -> int:
    changed = 0
    for node in root.iter(qn("w:t")):
        if node.text and "\u25a1" in node.text:
            node.text = node.text.replace("\u25a1", " ")
            changed += 1
    return changed


def find_toc_range(paragraphs: list[ET.Element]) -> tuple[int, int] | None:
    start = None
    for index, paragraph in enumerate(paragraphs):
        text = paragraph_text(paragraph).strip().replace(" ", "")
        if text == "\u76ee\u5f55":
            start = index + 1
            break
    if start is None:
        return None
    end = start
    for index in range(start, len(paragraphs)):
        style_id = paragraph_style_id(paragraphs[index])
        if style_id in {"TOC1", "TOC2", "TOC3"}:
            end = index + 1
            continue
        if end > start:
            break
    return (start, end) if end > start else None


def add_front_matter_toc_entries(body: ET.Element) -> int:
    paragraphs = body_paragraphs(body)
    toc_range = find_toc_range(paragraphs)
    if toc_range is None:
        return 0
    start, _end = toc_range
    toc_texts = [paragraph_text(paragraph) for paragraph in paragraphs[start:]]
    labels = {text.split("\t", 1)[0].strip().lower() for text in toc_texts}
    insertions: list[ET.Element] = []
    template = paragraphs[start]
    if "\u6458\u8981" not in labels:
        insertions.append(make_toc_entry_from(template, "\u6458\u8981", "I"))
    if "abstract" not in labels:
        insertions.append(make_toc_entry_from(template, "ABSTRACT", "II"))
    body_children = list(body)
    anchor = paragraphs[start]
    body_index = body_children.index(anchor)
    for offset, paragraph in enumerate(insertions):
        body.insert(body_index + offset, paragraph)
    return len(insertions)


def add_live_toc_field(body: ET.Element) -> int:
    paragraphs = body_paragraphs(body)
    toc_range = find_toc_range(paragraphs)
    if toc_range is None:
        return 0
    start, end = toc_range
    existing_instr = " ".join(node.text or "" for node in body.iter(qn("w:instrText")))
    if re.search(r"(^|\s)TOC(\s|$)", existing_instr, re.IGNORECASE):
        return 0
    first = paragraphs[start]
    begin_run = ET.Element(qn("w:r"))
    begin_char = ET.SubElement(begin_run, qn("w:fldChar"))
    begin_char.set(qn("w:fldCharType"), "begin")
    instr_run = ET.Element(qn("w:r"))
    instr = ET.SubElement(instr_run, qn("w:instrText"))
    instr.set(qn("xml:space"), "preserve")
    instr.text = ' TOC \\o "1-3" \\h \\z \\u '
    separate_run = ET.Element(qn("w:r"))
    separate = ET.SubElement(separate_run, qn("w:fldChar"))
    separate.set(qn("w:fldCharType"), "separate")
    insert_pos = 1 if first.find("./w:pPr", NS) is not None else 0
    first.insert(insert_pos, separate_run)
    first.insert(insert_pos, instr_run)
    first.insert(insert_pos, begin_run)
    paragraphs = body_paragraphs(body)
    _start, end = find_toc_range(paragraphs) or (start, end)
    last = paragraphs[end - 1]
    end_run = ET.Element(qn("w:r"))
    end_char = ET.SubElement(end_run, qn("w:fldChar"))
    end_char.set(qn("w:fldCharType"), "end")
    last.append(end_run)
    return 1


def make_paragraph(text: str, *, style_id: str = "Normal", center: bool = False) -> ET.Element:
    p = ET.Element(qn("w:p"))
    ppr = ET.SubElement(p, qn("w:pPr"))
    pstyle = ET.SubElement(ppr, qn("w:pStyle"))
    pstyle.set(qn("w:val"), style_id)
    if center:
        jc = ET.SubElement(ppr, qn("w:jc"))
        jc.set(qn("w:val"), "center")
    p.append(make_text_run(text))
    return p


def make_cell(text: str, width: str, *, header: bool = False) -> ET.Element:
    tc = ET.Element(qn("w:tc"))
    tcpr = ET.SubElement(tc, qn("w:tcPr"))
    tcw = ET.SubElement(tcpr, qn("w:tcW"))
    tcw.set(qn("w:w"), width)
    tcw.set(qn("w:type"), "dxa")
    if header:
        borders = ET.SubElement(tcpr, qn("w:tcBorders"))
        bottom = ET.SubElement(borders, qn("w:bottom"))
        bottom.set(qn("w:val"), "single")
        bottom.set(qn("w:sz"), "6")
        bottom.set(qn("w:space"), "0")
        bottom.set(qn("w:color"), "000000")
    tc.append(make_paragraph(text))
    return tc


def make_table() -> ET.Element:
    rows = [
        ["\u6d4b\u8bd5\u9879", "\u7ed3\u679c", "\u8bf4\u660e"],
        ["\u89c6\u9891\u4e0a\u4f20\u4e0e\u89e3\u6790", "\u901a\u8fc7", "\u53ef\u8bfb\u53d6\u89c6\u9891\u57fa\u672c\u4fe1\u606f\u5e76\u5efa\u7acb\u68c0\u6d4b\u4efb\u52a1"],
        ["\u5f02\u5e38\u884c\u4e3a\u5224\u5b9a", "\u901a\u8fc7", "\u80fd\u8f93\u51fa\u4f4e\u5934\u3001\u8d77\u7acb\u3001\u8f6c\u5934\u7b49\u98ce\u9669\u7c7b\u578b"],
        ["\u7ed3\u679c\u7edf\u8ba1\u4e0e\u56de\u653e", "\u901a\u8fc7", "\u7edf\u8ba1\u3001\u5217\u8868\u548c\u5386\u53f2\u56de\u653e\u80fd\u5f62\u6210\u95ed\u73af"],
    ]
    widths = ["2600", "1800", "5000"]
    tbl = ET.Element(qn("w:tbl"))
    tblpr = ET.SubElement(tbl, qn("w:tblPr"))
    tblw = ET.SubElement(tblpr, qn("w:tblW"))
    tblw.set(qn("w:w"), "9400")
    tblw.set(qn("w:type"), "dxa")
    jc = ET.SubElement(tblpr, qn("w:jc"))
    jc.set(qn("w:val"), "center")
    borders = ET.SubElement(tblpr, qn("w:tblBorders"))
    for name, val, size in (
        ("top", "single", "8"),
        ("left", "nil", "0"),
        ("bottom", "single", "8"),
        ("right", "nil", "0"),
        ("insideH", "nil", "0"),
        ("insideV", "nil", "0"),
    ):
        border = ET.SubElement(borders, qn(f"w:{name}"))
        border.set(qn("w:val"), val)
        border.set(qn("w:sz"), size)
        border.set(qn("w:space"), "0")
        border.set(qn("w:color"), "000000")
    grid = ET.SubElement(tbl, qn("w:tblGrid"))
    for width in widths:
        col = ET.SubElement(grid, qn("w:gridCol"))
        col.set(qn("w:w"), width)
    for row_index, row_values in enumerate(rows):
        tr = ET.SubElement(tbl, qn("w:tr"))
        for text, width in zip(row_values, widths):
            tr.append(make_cell(text, width, header=row_index == 0))
    return tbl


def add_results_table(body: ET.Element) -> int:
    if body.find(".//w:tbl", NS) is not None:
        return 0
    paragraphs = body_paragraphs(body)
    anchor = None
    for paragraph in paragraphs:
        text = paragraph_text(paragraph).strip()
        if text.startswith("5.3") or text.startswith("5\uff0e3") or text.startswith("5\uff0e 3"):
            anchor = paragraph
            break
    if anchor is None:
        for paragraph in paragraphs:
            if paragraph_text(paragraph).strip().startswith("6"):
                anchor = paragraph
                break
    if anchor is None:
        return 0
    caption = make_paragraph("\u88685-1  \u7cfb\u7edf\u6d4b\u8bd5\u7ed3\u679c\u6c47\u603b", center=True)
    table = make_table()
    children = list(body)
    index = children.index(anchor)
    body.insert(index, caption)
    body.insert(index + 1, table)
    return 1


def patch_document_xml(xml_bytes: bytes) -> tuple[bytes, dict[str, int]]:
    root = ET.fromstring(xml_bytes)
    body = root.find("w:body", NS)
    if body is None:
        raise RuntimeError("word/document.xml has no w:body")
    report = {
        "square_placeholder_text_nodes_changed": normalize_square_placeholders(root),
        "front_matter_toc_entries_added": add_front_matter_toc_entries(body),
        "live_toc_fields_added": add_live_toc_field(body),
        "results_tables_added": add_results_table(body),
    }
    return ET.tostring(root, encoding="utf-8", xml_declaration=True), report


def repair_docx(input_docx: Path, output_docx: Path) -> dict[str, object]:
    if not input_docx.exists():
        raise FileNotFoundError(input_docx)
    output_docx.parent.mkdir(parents=True, exist_ok=True)
    temp = output_docx.with_suffix(output_docx.suffix + ".tmp")
    with zipfile.ZipFile(input_docx, "r") as zin, zipfile.ZipFile(temp, "w", zipfile.ZIP_DEFLATED) as zout:
        changed_parts: list[str] = []
        patch_report: dict[str, int] = {}
        for item in zin.infolist():
            payload = zin.read(item.filename)
            if item.filename == "word/document.xml":
                payload, patch_report = patch_document_xml(payload)
                changed_parts.append(item.filename)
            zout.writestr(item, payload)
    shutil.move(str(temp), str(output_docx))
    return {
        "schema": "graduation-project-builder.docx-submission-blocker-repair.v1",
        "generator": "scripts/repair_docx_submission_blockers.py",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_docx_path": str(input_docx),
        "source_docx_sha256": sha256(input_docx),
        "final_docx_path": str(output_docx),
        "final_docx_sha256": sha256(output_docx),
        "changed_parts": changed_parts,
        **patch_report,
        "verdict": "pass",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-docx", required=True)
    parser.add_argument("--output-docx", required=True)
    parser.add_argument("--report-json", required=True)
    args = parser.parse_args()
    report = repair_docx(Path(args.input_docx).resolve(), Path(args.output_docx).resolve())
    report_path = Path(args.report_json).resolve()
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
