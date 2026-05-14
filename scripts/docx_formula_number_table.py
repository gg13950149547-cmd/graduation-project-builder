from __future__ import annotations

import argparse
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
import re
import shutil
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET


NS = {
    "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
    "w14": "http://schemas.microsoft.com/office/word/2010/wordml",
    "m": "http://schemas.openxmlformats.org/officeDocument/2006/math",
}
W = "{%s}" % NS["w"]
W14 = "{%s}" % NS["w14"]
M = "{%s}" % NS["m"]

ET.register_namespace("w", NS["w"])
ET.register_namespace("w14", NS["w14"])
ET.register_namespace("m", NS["m"])

PPR_AFTER_JC_TAGS = {
    W + "textDirection",
    W + "textAlignment",
    W + "textboxTightWrap",
    W + "outlineLvl",
    W + "divId",
    W + "cnfStyle",
    W + "rPr",
    W + "sectPr",
    W + "pPrChange",
}
PPR_AFTER_TABS_TAGS = {
    W + "suppressAutoHyphens",
    W + "kinsoku",
    W + "wordWrap",
    W + "overflowPunct",
    W + "topLinePunct",
    W + "autoSpaceDE",
    W + "autoSpaceDN",
    W + "bidi",
    W + "adjustRightInd",
    W + "snapToGrid",
    W + "spacing",
    W + "ind",
    W + "contextualSpacing",
    W + "mirrorIndents",
    W + "suppressOverlap",
    W + "jc",
    W + "textDirection",
    W + "textAlignment",
    W + "textboxTightWrap",
    W + "outlineLvl",
    W + "divId",
    W + "cnfStyle",
    W + "rPr",
    W + "sectPr",
    W + "pPrChange",
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def paragraph_text(paragraph: ET.Element) -> str:
    return "".join(node.text or "" for node in paragraph.findall(".//w:t", NS)).strip()


def root_namespace_declarations(document_xml: bytes) -> dict[str, str]:
    match = re.search(rb"<w:document\b(?P<attrs>[^>]*)>", document_xml[:12000], flags=re.S)
    if not match:
        return {}
    attrs = match.group("attrs")
    return {
        prefix.decode("ascii", errors="ignore"): uri.decode("utf-8", errors="ignore")
        for prefix, uri in re.findall(rb'\sxmlns:([A-Za-z0-9]+)="([^"]+)"', attrs)
    }


def serialize_document(root: ET.Element, original_document_xml: bytes) -> bytes:
    payload = ET.tostring(root, encoding="utf-8", xml_declaration=True)
    declarations = root_namespace_declarations(original_document_xml)
    root_start = payload.find(b"<w:document")
    if root_start < 0:
        return payload
    root_end = payload.find(b">", root_start)
    if root_end < 0:
        return payload
    root_tag = payload[root_start:root_end]
    additions: list[bytes] = []
    for prefix, uri in declarations.items():
        token = f"xmlns:{prefix}=".encode("ascii")
        if token not in root_tag:
            additions.append(f' xmlns:{prefix}="{uri}"'.encode("utf-8"))
    if not additions:
        return payload
    return payload[:root_end] + b"".join(additions) + payload[root_end:]


def add_paragraph_jc(ppr: ET.Element, value: str) -> None:
    for jc in list(ppr.findall(W + "jc")):
        ppr.remove(jc)
    element = ET.Element(W + "jc", {W + "val": value})
    for index, child in enumerate(list(ppr)):
        if child.tag in PPR_AFTER_JC_TAGS:
            ppr.insert(index, element)
            return
    ppr.append(element)


def add_right_tab(ppr: ET.Element, position: str = "9000") -> None:
    for tabs in list(ppr.findall(W + "tabs")):
        ppr.remove(tabs)
    tabs = ET.Element(W + "tabs")
    ET.SubElement(tabs, W + "tab", {W + "val": "right", W + "pos": position})
    for index, child in enumerate(list(ppr)):
        if child.tag in PPR_AFTER_TABS_TAGS:
            ppr.insert(index, tabs)
            return
    ppr.append(tabs)


def add_formula_tabs(ppr: ET.Element, center_position: str, right_position: str) -> None:
    for tabs in list(ppr.findall(W + "tabs")):
        ppr.remove(tabs)
    tabs = ET.Element(W + "tabs")
    ET.SubElement(tabs, W + "tab", {W + "val": "center", W + "pos": center_position})
    ET.SubElement(tabs, W + "tab", {W + "val": "right", W + "pos": right_position})
    for index, child in enumerate(list(ppr)):
        if child.tag in PPR_AFTER_TABS_TAGS:
            ppr.insert(index, tabs)
            return
    ppr.append(tabs)


def attr_int(element: ET.Element | None, name: str, default: int = 0) -> int:
    if element is None:
        return default
    value = element.attrib.get(W + name)
    if value is None:
        return default
    try:
        return int(value)
    except ValueError:
        return default


def content_width_from_sect_pr(sect_pr: ET.Element | None) -> int:
    if sect_pr is None:
        return 9000
    page_size = sect_pr.find(W + "pgSz")
    page_margin = sect_pr.find(W + "pgMar")
    page_width = attr_int(page_size, "w", 11906)
    left_margin = attr_int(page_margin, "left", 1800)
    right_margin = attr_int(page_margin, "right", 1800)
    content_width = page_width - left_margin - right_margin
    return content_width if content_width > 0 else 9000


def section_content_width_for_body_index(body: ET.Element, index: int) -> int:
    children = list(body)
    for child in children[index:]:
        sect_pr = None
        if child.tag == W + "sectPr":
            sect_pr = child
        elif child.tag == W + "p":
            ppr = child.find(W + "pPr")
            if ppr is not None:
                sect_pr = ppr.find(W + "sectPr")
        if sect_pr is not None:
            return content_width_from_sect_pr(sect_pr)
    return content_width_from_sect_pr(body.find(W + "sectPr"))


def paragraph_indent_adjustment(paragraph: ET.Element) -> int:
    ppr = paragraph.find(W + "pPr")
    if ppr is None:
        return 0
    ind = ppr.find(W + "ind")
    if ind is None:
        return 0
    return max(0, attr_int(ind, "left", 0)) + max(0, attr_int(ind, "right", 0))


def formula_tab_positions(content_width_twips: int, paragraph: ET.Element) -> tuple[str, str]:
    usable_width = max(2000, content_width_twips - paragraph_indent_adjustment(paragraph))
    return str(usable_width // 2), str(usable_width)


def remove_paragraph_jc(ppr: ET.Element) -> None:
    for jc in list(ppr.findall(W + "jc")):
        ppr.remove(jc)


def make_text_run(text_value: str) -> ET.Element:
    run = ET.Element(W + "r")
    text = ET.SubElement(run, W + "t")
    text.text = text_value
    return run


def make_tab_run() -> ET.Element:
    run = ET.Element(W + "r")
    ET.SubElement(run, W + "tab")
    return run


def make_break_run() -> ET.Element:
    run = ET.Element(W + "r")
    ET.SubElement(run, W + "br")
    return run


def add_math_run(parent: ET.Element, text: str) -> None:
    run = ET.SubElement(parent, M + "r")
    text_node = ET.SubElement(run, M + "t")
    text_node.text = text


def add_segments(parent: ET.Element, segments: list[object]) -> None:
    for segment in segments:
        if isinstance(segment, str):
            add_math_run(parent, segment)
            continue
        if not isinstance(segment, dict):
            raise ValueError(f"Unsupported formula segment: {segment!r}")
        if "text" in segment:
            add_math_run(parent, str(segment["text"]))
            continue
        if "sub" in segment:
            value = segment["sub"]
            if not isinstance(value, dict):
                raise ValueError(f"Formula sub segment must be an object: {segment!r}")
            sub = ET.SubElement(parent, M + "sSub")
            base = ET.SubElement(sub, M + "e")
            add_segments(base, [str(value.get("base", ""))])
            subscript = ET.SubElement(sub, M + "sub")
            add_segments(subscript, [str(value.get("subscript", ""))])
            continue
        if "frac" in segment:
            value = segment["frac"]
            if not isinstance(value, dict):
                raise ValueError(f"Formula frac segment must be an object: {segment!r}")
            frac = ET.SubElement(parent, M + "f")
            num = ET.SubElement(frac, M + "num")
            add_segments(num, list(value.get("num", [])))
            den = ET.SubElement(frac, M + "den")
            add_segments(den, list(value.get("den", [])))
            continue
        if "abs" in segment:
            add_math_run(parent, "|")
            add_segments(parent, list(segment["abs"]))
            add_math_run(parent, "|")
            continue
        raise ValueError(f"Unsupported formula segment keys: {segment!r}")


def make_formula_paragraph(template_para: ET.Element, segments: list[object], keep_paragraph_attrs: bool = True) -> ET.Element:
    formula_para = ET.Element(W + "p", dict(template_para.attrib) if keep_paragraph_attrs else {})
    ppr = template_para.find(W + "pPr")
    if ppr is not None:
        ppr_copy = deepcopy(ppr)
    else:
        ppr_copy = ET.Element(W + "pPr")
    add_paragraph_jc(ppr_copy, "center")
    formula_para.append(ppr_copy)
    omath_para = ET.SubElement(formula_para, M + "oMathPara")
    omath = ET.SubElement(omath_para, M + "oMath")
    add_segments(omath, segments)
    return formula_para


def make_inline_formula_paragraph(
    template_para: ET.Element,
    lines: list[list[object]],
    number_text: str,
    content_width_twips: int,
) -> ET.Element:
    formula_para = ET.Element(W + "p", dict(template_para.attrib))
    ppr = template_para.find(W + "pPr")
    if ppr is not None:
        ppr_copy = deepcopy(ppr)
    else:
        ppr_copy = ET.Element(W + "pPr")
    center_position, right_position = formula_tab_positions(content_width_twips, template_para)
    add_formula_tabs(ppr_copy, center_position=center_position, right_position=right_position)
    remove_paragraph_jc(ppr_copy)
    formula_para.append(ppr_copy)
    for index, line in enumerate(lines):
        if index > 0:
            formula_para.append(make_break_run())
        formula_para.append(make_tab_run())
        omath = ET.SubElement(formula_para, M + "oMath")
        add_segments(omath, line)
        if index == 0:
            formula_para.append(make_tab_run())
            formula_para.append(make_text_run(number_text))
    return formula_para


def make_borderless_table_from_formula_paragraphs(
    formula_paras: list[ET.Element],
    number_text: str,
    total_width_twips: int = 9000,
) -> ET.Element:
    if not formula_paras:
        raise ValueError("formula_paras must not be empty")
    total_width = max(3600, total_width_twips)
    side_width = min(1200, max(720, total_width // 8))
    middle_width = total_width - (side_width * 2)
    tbl = ET.Element(W + "tbl")
    tbl_pr = ET.SubElement(tbl, W + "tblPr")
    ET.SubElement(tbl_pr, W + "tblW", {W + "w": str(total_width), W + "type": "dxa"})
    tbl_borders = ET.SubElement(tbl_pr, W + "tblBorders")
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        ET.SubElement(tbl_borders, W + edge, {W + "val": "nil"})
    ET.SubElement(tbl_pr, W + "tblLayout", {W + "type": "fixed"})

    tbl_grid = ET.SubElement(tbl, W + "tblGrid")
    ET.SubElement(tbl_grid, W + "gridCol", {W + "w": str(side_width)})
    ET.SubElement(tbl_grid, W + "gridCol", {W + "w": str(middle_width)})
    ET.SubElement(tbl_grid, W + "gridCol", {W + "w": str(side_width)})

    tr = ET.SubElement(tbl, W + "tr")
    left_tc = ET.SubElement(tr, W + "tc")
    left_tc_pr = ET.SubElement(left_tc, W + "tcPr")
    ET.SubElement(left_tc_pr, W + "tcW", {W + "w": str(side_width), W + "type": "dxa"})
    ET.SubElement(left_tc, W + "p")

    middle_tc = ET.SubElement(tr, W + "tc")
    middle_tc_pr = ET.SubElement(middle_tc, W + "tcPr")
    ET.SubElement(middle_tc_pr, W + "tcW", {W + "w": str(middle_width), W + "type": "dxa"})
    for formula_para in formula_paras:
        middle_tc.append(formula_para)

    right_tc = ET.SubElement(tr, W + "tc")
    right_tc_pr = ET.SubElement(right_tc, W + "tcPr")
    ET.SubElement(right_tc_pr, W + "tcW", {W + "w": str(side_width), W + "type": "dxa"})
    ET.SubElement(right_tc_pr, W + "vAlign", {W + "val": "center"})
    right_para = ET.SubElement(right_tc, W + "p")
    right_ppr = ET.SubElement(right_para, W + "pPr")
    add_paragraph_jc(right_ppr, "right")
    run = ET.SubElement(right_para, W + "r")
    text = ET.SubElement(run, W + "t")
    text.text = number_text
    return tbl


def make_formula_table_from_segments(
    template_para: ET.Element,
    segments: list[object],
    number_text: str,
    content_width_twips: int = 9000,
) -> ET.Element:
    formula_para = make_formula_paragraph(template_para, segments)
    return make_borderless_table_from_formula_paragraphs([formula_para], number_text, content_width_twips)


def make_formula_table_from_lines(
    template_para: ET.Element,
    lines: list[list[object]],
    number_text: str,
    content_width_twips: int = 9000,
) -> ET.Element:
    formula_paras = [
        make_formula_paragraph(template_para, line, keep_paragraph_attrs=(index == 0))
        for index, line in enumerate(lines)
    ]
    return make_borderless_table_from_formula_paragraphs(formula_paras, number_text, content_width_twips)


def make_borderless_table(
    formula_para: ET.Element,
    number_text: str,
    content_width_twips: int = 9000,
) -> ET.Element:
    moved_para = ET.Element(W + "p", formula_para.attrib)
    ppr = formula_para.find(W + "pPr")
    if ppr is not None:
        moved_para.append(ppr)
    else:
        moved_para.append(ET.Element(W + "pPr"))
    add_paragraph_jc(moved_para.find(W + "pPr"), "center")
    for child in list(formula_para):
        if child.tag != W + "pPr":
            moved_para.append(child)
    return make_borderless_table_from_formula_paragraphs([moved_para], number_text, content_width_twips)


def patch_formula(docx_path: Path, para_id: str, number_text: str, output_path: Path | None) -> Path:
    out_path = output_path or docx_path
    if output_path:
        shutil.copy2(docx_path, out_path)

    with zipfile.ZipFile(out_path, "r") as zin:
        members = {name: zin.read(name) for name in zin.namelist()}

    original_document_xml = members["word/document.xml"]
    root = ET.fromstring(original_document_xml)
    body = root.find(".//w:body", NS)
    if body is None:
        raise ValueError("word/document.xml does not contain w:body")

    index = None
    formula_para = None
    for i, child in enumerate(list(body)):
        if child.tag != W + "p":
            continue
        if child.attrib.get(W14 + "paraId") == para_id:
            formula_para = child
            index = i
            break
    if formula_para is None or index is None:
        raise ValueError(f"Formula paragraph {para_id} not found")
    if formula_para.find(".//m:oMathPara", NS) is None and formula_para.find(".//m:oMath", NS) is None:
        raise ValueError(f"Paragraph {para_id} does not contain a math object")

    content_width_twips = section_content_width_for_body_index(body, index)
    tbl = make_borderless_table(formula_para, number_text, content_width_twips)
    body.remove(formula_para)
    body.insert(index, tbl)

    members["word/document.xml"] = serialize_document(root, original_document_xml)
    with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as zout:
        for name, data in members.items():
            zout.writestr(name, data)
    return out_path


def replace_text_formulas(docx_path: Path, formula_map_path: Path, output_path: Path, report_path: Path | None = None) -> dict[str, object]:
    shutil.copy2(docx_path, output_path)
    formula_map = json.loads(formula_map_path.read_text(encoding="utf-8"))
    formulas = formula_map.get("formulas")
    if not isinstance(formulas, list) or not formulas:
        raise ValueError("formula map must contain a non-empty formulas list")

    with zipfile.ZipFile(output_path, "r") as zin:
        members = {name: zin.read(name) for name in zin.namelist()}

    original_document_xml = members["word/document.xml"]
    root = ET.fromstring(original_document_xml)
    body = root.find(".//w:body", NS)
    if body is None:
        raise ValueError("word/document.xml does not contain w:body")

    replacements: list[dict[str, object]] = []
    missing: list[dict[str, object]] = []
    body_children = list(body)
    for formula in formulas:
        if not isinstance(formula, dict):
            raise ValueError(f"formula map row must be an object: {formula!r}")
        source_text = str(formula.get("source_text", "")).strip()
        number_text = str(formula.get("number", "")).strip()
        segments = formula.get("segments")
        lines = formula.get("lines")
        if not source_text or not number_text:
            raise ValueError(f"formula map row missing source_text or number: {formula!r}")
        if lines is not None and not isinstance(lines, list):
            raise ValueError(f"formula map row lines must be a list: {formula!r}")
        if lines is None and not isinstance(segments, list):
            raise ValueError(f"formula map row missing segments or lines: {formula!r}")
        match_index = None
        match_para = None
        for index, child in enumerate(body_children):
            if child.tag != W + "p":
                continue
            if paragraph_text(child) == source_text:
                match_index = index
                match_para = child
                break
        if match_index is None or match_para is None:
            missing.append({"source_text": source_text, "number": number_text})
            continue
        if lines is not None:
            line_segments = [list(line) for line in lines]
        else:
            line_segments = [list(segments)]
        content_width_twips = section_content_width_for_body_index(body, match_index)
        if str(formula.get("layout", "table")).strip().lower() == "paragraph":
            replacement = make_inline_formula_paragraph(match_para, line_segments, number_text, content_width_twips)
        elif lines is not None:
            replacement = make_formula_table_from_lines(match_para, line_segments, number_text, content_width_twips)
        else:
            replacement = make_formula_table_from_segments(match_para, line_segments[0], number_text, content_width_twips)
        body.remove(match_para)
        body.insert(match_index, replacement)
        body_children = list(body)
        replacements.append(
            {
                "source_text": source_text,
                "number": number_text,
                "body_child_index": match_index,
                "source_para_id": match_para.attrib.get(W14 + "paraId", ""),
            }
        )

    if missing:
        raise ValueError(f"formula text anchors not found: {missing}")

    members["word/document.xml"] = serialize_document(root, original_document_xml)
    with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zout:
        for name, data in members.items():
            zout.writestr(name, data)

    report = {
        "schema": "graduation-project-builder.text-formula-omml-replacement.v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "source_docx": str(docx_path.resolve()),
        "source_docx_sha256": sha256_file(docx_path),
        "formula_map": str(formula_map_path.resolve()),
        "output_docx": str(output_path.resolve()),
        "output_docx_sha256": sha256_file(output_path),
        "changed_zip_parts": ["word/document.xml"],
        "replacement_count": len(replacements),
        "replacements": replacements,
        "missing": missing,
    }
    if report_path is not None:
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Convert one formula paragraph into a borderless table with right-side number.")
    parser.add_argument("--docx", required=True)
    parser.add_argument("--para-id")
    parser.add_argument("--number")
    parser.add_argument("--output")
    parser.add_argument("--replace-text-formulas", action="store_true")
    parser.add_argument("--formula-map")
    parser.add_argument("--report")
    args = parser.parse_args()

    if args.replace_text_formulas:
        if not args.formula_map or not args.output:
            parser.error("--replace-text-formulas requires --formula-map and --output")
        report = replace_text_formulas(
            docx_path=Path(args.docx),
            formula_map_path=Path(args.formula_map),
            output_path=Path(args.output),
            report_path=Path(args.report) if args.report else None,
        )
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 0

    if not args.para_id or not args.number:
        parser.error("--para-id and --number are required unless --replace-text-formulas is used")

    out_path = patch_formula(
        docx_path=Path(args.docx),
        para_id=args.para_id,
        number_text=args.number,
        output_path=Path(args.output) if args.output else None,
    )
    print(f"patched_docx={out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
