#!/usr/bin/env python3
"""Audit thesis body table structure without mutating the DOCX."""

from __future__ import annotations

import argparse
import json
import re
import sys
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

NS = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
W = NS["w"]


def q(name: str) -> str:
    return f"{{{W}}}{name}"


def text_of(element: ET.Element | None) -> str:
    if element is None:
        return ""
    return "".join(node.text or "" for node in element.findall(".//w:t", NS))


def compact(value: str) -> str:
    return re.sub(r"\s+", "", value or "")


def w_attr(element: ET.Element | None, name: str) -> str | None:
    return element.get(q(name)) if element is not None else None


def paragraph_info(paragraph: ET.Element | None) -> dict[str, object]:
    ppr = paragraph.find("w:pPr", NS) if paragraph is not None else None
    ind = ppr.find("w:ind", NS) if ppr is not None else None
    jc = ppr.find("w:jc", NS) if ppr is not None else None
    pstyle = ppr.find("w:pStyle", NS) if ppr is not None else None
    keep_next = ppr.find("w:keepNext", NS) is not None if ppr is not None else False
    return {
        "text": text_of(paragraph),
        "style": w_attr(pstyle, "val"),
        "jc": w_attr(jc, "val"),
        "keepNext": keep_next,
        "ind": {
            key: ind.get(q(key))
            for key in ("firstLine", "firstLineChars", "left", "right", "hanging", "hangingChars")
            if ind is not None and ind.get(q(key)) is not None
        },
    }


def border_info(border: ET.Element | None) -> dict[str, str] | None:
    if border is None:
        return None
    return {
        key: border.get(q(key))
        for key in ("val", "sz", "space", "color")
        if border.get(q(key)) is not None
    }


def cell_borders(cell: ET.Element) -> dict[str, object]:
    tcpr = cell.find("w:tcPr", NS)
    borders = tcpr.find("w:tcBorders", NS) if tcpr is not None else None
    if borders is None:
        return {}
    result: dict[str, object] = {}
    for name in ("top", "bottom", "left", "right", "insideH", "insideV"):
        node = borders.find(f"w:{name}", NS)
        if node is not None:
            result[name] = border_info(node)
    return result


def row_flags(row: ET.Element | None) -> dict[str, bool]:
    trpr = row.find("w:trPr", NS) if row is not None else None
    return {
        "tblHeader": trpr.find("w:tblHeader", NS) is not None if trpr is not None else False,
        "cantSplit": trpr.find("w:cantSplit", NS) is not None if trpr is not None else False,
    }


def run_size(run: ET.Element) -> str | None:
    rpr = run.find("w:rPr", NS)
    sz = rpr.find("w:sz", NS) if rpr is not None else None
    return w_attr(sz, "val")


def table_cell_margins(table: ET.Element) -> dict[str, object]:
    tblpr = table.find("w:tblPr", NS)
    margins = tblpr.find("w:tblCellMar", NS) if tblpr is not None else None
    result: dict[str, object] = {}
    if margins is None:
        return result
    for name in ("top", "bottom", "left", "right"):
        node = margins.find(f"w:{name}", NS)
        if node is not None:
            result[name] = {"w": w_attr(node, "w"), "type": w_attr(node, "type")}
    return result


def load_body_children(docx: Path) -> list[ET.Element]:
    with zipfile.ZipFile(docx) as zf:
        root = ET.fromstring(zf.read("word/document.xml"))
    body = root.find("w:body", NS)
    if body is None:
        raise ValueError("word/document.xml has no w:body")
    return list(body)


def previous_nonempty_paragraph(children: list[ET.Element], index: int) -> tuple[int | None, ET.Element | None]:
    for prev in range(index - 1, -1, -1):
        if children[prev].tag == q("p") and compact(text_of(children[prev])):
            return prev, children[prev]
    return None, None


def audit_docx(docx: Path, rendered_pages: list[str] | None = None) -> dict[str, object]:
    children = load_body_children(docx)
    title_pattern = re.compile(r"\s*\u8868\s*\d+[\-\u2014\uff0d.]\d+")
    tables: list[dict[str, object]] = []
    for index, child in enumerate(children):
        if child.tag != q("tbl"):
            continue
        title_index, title_paragraph = previous_nonempty_paragraph(children, index)
        title = text_of(title_paragraph)
        if not title_pattern.match(title):
            continue
        rows = child.findall("w:tr", NS)
        first_row = rows[0] if rows else None
        last_row = rows[-1] if rows else None
        first_row_borders = [cell_borders(cell) for cell in first_row.findall("w:tc", NS)] if first_row is not None else []
        last_row_borders = [cell_borders(cell) for cell in last_row.findall("w:tc", NS)] if last_row is not None else []
        cell_sizes = sorted(
            {
                size
                for row in rows
                for cell in row.findall("w:tc", NS)
                for paragraph in cell.findall("w:p", NS)
                for run in paragraph.findall("w:r", NS)
                for size in [run_size(run)]
                if size is not None and compact(text_of(run))
            }
        )
        nonzero_indent_count = 0
        for row in rows:
            for cell in row.findall("w:tc", NS):
                for paragraph in cell.findall("w:p", NS):
                    if not compact(text_of(paragraph)):
                        continue
                    ind = paragraph_info(paragraph)["ind"]
                    if isinstance(ind, dict) and any(value not in ("0", None) for value in ind.values()):
                        nonzero_indent_count += 1
        first_top = [border.get("top", {}).get("val") for border in first_row_borders]
        header_bottom = [border.get("bottom", {}).get("val") for border in first_row_borders]
        last_bottom = [border.get("bottom", {}).get("val") for border in last_row_borders]
        visible_verticals = []
        for row in rows:
            for border in [cell_borders(cell) for cell in row.findall("w:tc", NS)]:
                for side in ("left", "right"):
                    if border.get(side, {}).get("val") not in (None, "nil", "none"):
                        visible_verticals.append(border)
        row_flag_list = [row_flags(row) for row in rows]
        table_record = {
            "table_child_index": index,
            "title_child_index": title_index,
            "title": title,
            "title_info": paragraph_info(title_paragraph),
            "row_count": len(rows),
            "column_count_first_row": len(first_row.findall("w:tc", NS)) if first_row is not None else 0,
            "table_cell_margins": table_cell_margins(child),
            "row_flags": row_flag_list,
            "cell_run_sizes": cell_sizes,
            "nonzero_cell_indent_count": nonzero_indent_count,
            "title_keep_next_verdict": bool(paragraph_info(title_paragraph)["keepNext"]),
            "header_repeat_verdict": bool(first_row is not None and row_flags(first_row)["tblHeader"]),
            "row_cant_split_verdict": all(flag["cantSplit"] for flag in row_flag_list),
            "cell_size_5hao_verdict": cell_sizes == ["21"],
            "cell_zero_indent_verdict": nonzero_indent_count == 0,
            "visible_border_structure_verdict": (
                all(value == "single" for value in first_top)
                and all(value == "single" for value in header_bottom)
                and all(value == "single" for value in last_bottom)
                and not visible_verticals
            ),
        }
        tables.append(table_record)
    summary = {
        "body_table_count": len(tables),
        "all_table_title_keep_next": all(t["title_keep_next_verdict"] for t in tables),
        "all_table_visible_border_structure": all(t["visible_border_structure_verdict"] for t in tables),
        "all_table_header_repeat": all(t["header_repeat_verdict"] for t in tables),
        "all_table_rows_cant_split": all(t["row_cant_split_verdict"] for t in tables),
        "all_table_cell_5hao": all(t["cell_size_5hao_verdict"] for t in tables),
        "all_table_zero_indent": all(t["cell_zero_indent_verdict"] for t in tables),
        "rendered_pages": rendered_pages or [],
        "cross_page_table_summary": "explicit continuation evidence must be supplied by rendered-page review",
    }
    passed = bool(tables) and all(
        bool(t[key])
        for t in tables
        for key in (
            "title_keep_next_verdict",
            "visible_border_structure_verdict",
            "header_repeat_verdict",
            "row_cant_split_verdict",
            "cell_size_5hao_verdict",
            "cell_zero_indent_verdict",
        )
    )
    return {
        "schema": "graduation-project-builder.docx-table-structure.v1",
        "docx": str(docx),
        "passed": passed,
        "summary": summary,
        "body_tables": tables,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--docx", required=True)
    parser.add_argument("--report-json")
    parser.add_argument("--rendered-pages", default="")
    parser.add_argument("--fail-on-drift", action="store_true")
    args = parser.parse_args(argv)
    rendered_pages = [part.strip() for part in re.split(r"[;\n]", args.rendered_pages) if part.strip()]
    report = audit_docx(Path(args.docx), rendered_pages)
    if args.report_json:
        output = Path(args.report_json)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"passed": report["passed"], **report["summary"]}, ensure_ascii=False))
    return 1 if args.fail_on_drift and not report["passed"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
