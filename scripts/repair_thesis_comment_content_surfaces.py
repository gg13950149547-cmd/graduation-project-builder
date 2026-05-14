#!/usr/bin/env python3
"""Apply bounded comment-driven thesis content and figure-surface repairs.

This helper is intentionally package-preserving: it rewrites ``word/document.xml``,
``word/_rels/document.xml.rels``, selected ``word/media/*`` entries, and content
types only when a new media extension requires it.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
import sys
import zipfile
from pathlib import Path
from typing import Any
from xml.etree import ElementTree as ET

from PIL import Image


NS = {
    "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
    "wp": "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing",
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
    "pic": "http://schemas.openxmlformats.org/drawingml/2006/picture",
    "pr": "http://schemas.openxmlformats.org/package/2006/relationships",
    "ct": "http://schemas.openxmlformats.org/package/2006/content-types",
}

for prefix, uri in NS.items():
    ET.register_namespace("" if prefix == "ct" else prefix, uri)

W = "{%s}" % NS["w"]
R = "{%s}" % NS["r"]
WP = "{%s}" % NS["wp"]
A = "{%s}" % NS["a"]
PIC = "{%s}" % NS["pic"]
PR = "{%s}" % NS["pr"]
CT = "{%s}" % NS["ct"]


IMAGE_MUTATION_KEYS = ("media_replacements", "new_media", "display_extents")
PROTECTED_TEXT_PREFIXES = (
    "abstract",
    "key words",
    "keywords",
    "\u6458\u8981",
    "\u5173\u952e\u8bcd",
    "\u76ee\u5f55",
    "\u53c2\u8003\u6587\u732e",
    "\u81f4\u8c22",
)


def qn(prefix: str, local: str) -> str:
    return f"{{{NS[prefix]}}}{local}"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_xml(zf: zipfile.ZipFile, name: str) -> ET.Element:
    return ET.fromstring(zf.read(name))


def paragraph_text(paragraph: ET.Element) -> str:
    return "".join(node.text or "" for node in paragraph.findall(".//w:t", NS))


def body_paragraphs(document_root: ET.Element) -> list[ET.Element]:
    body = document_root.find("w:body", NS)
    if body is None:
        return []
    return [child for child in list(body) if child.tag == W + "p"]


def all_paragraphs(document_root: ET.Element) -> list[ET.Element]:
    return document_root.findall(".//w:p", NS)


def clone_ppr(paragraph: ET.Element | None) -> ET.Element:
    ppr = paragraph.find("w:pPr", NS) if paragraph is not None else None
    return copy.deepcopy(ppr) if ppr is not None else ET.Element(W + "pPr")


def ensure_ppr(paragraph: ET.Element) -> ET.Element:
    ppr = paragraph.find("w:pPr", NS)
    if ppr is None:
        ppr = ET.Element(W + "pPr")
        paragraph.insert(0, ppr)
    return ppr


def set_paragraph_metrics(paragraph: ET.Element, *, first_line_chars: str | None = None, line: str | None = None) -> None:
    ppr = ensure_ppr(paragraph)
    if line is not None:
        spacing = ppr.find("w:spacing", NS)
        if spacing is None:
            spacing = ET.SubElement(ppr, W + "spacing")
        spacing.set(W + "line", line)
        spacing.set(W + "lineRule", "auto")
        spacing.set(W + "before", spacing.get(W + "before", "0"))
        spacing.set(W + "after", spacing.get(W + "after", "0"))
    if first_line_chars is not None:
        ind = ppr.find("w:ind", NS)
        if ind is None:
            ind = ET.SubElement(ppr, W + "ind")
        # Word's visible first-line indent needs the real twip value; the
        # character-unit companion alone is not stable across editors.
        if first_line_chars == "200":
            ind.set(W + "firstLine", "480")
        else:
            ind.attrib.pop(W + "firstLine", None)
        ind.set(W + "firstLineChars", first_line_chars)


def set_alignment(paragraph: ET.Element, value: str) -> None:
    ppr = ensure_ppr(paragraph)
    jc = ppr.find("w:jc", NS)
    if jc is None:
        jc = ET.SubElement(ppr, W + "jc")
    jc.set(W + "val", value)


def set_style_id(paragraph: ET.Element, style_id: str | None) -> None:
    ppr = ensure_ppr(paragraph)
    pstyle = ppr.find("w:pStyle", NS)
    if style_id is None:
        if pstyle is not None:
            ppr.remove(pstyle)
        return
    if pstyle is None:
        pstyle = ET.Element(W + "pStyle")
        ppr.insert(0, pstyle)
    pstyle.set(W + "val", style_id)


def set_spacing(paragraph: ET.Element, *, line: str = "360", before: str = "0", after: str = "0") -> None:
    ppr = ensure_ppr(paragraph)
    spacing = ppr.find("w:spacing", NS)
    if spacing is None:
        spacing = ET.SubElement(ppr, W + "spacing")
    spacing.set(W + "line", line)
    spacing.set(W + "lineRule", "auto")
    spacing.set(W + "before", before)
    spacing.set(W + "after", after)


def set_indent(
    paragraph: ET.Element,
    *,
    first_line: str | None = "480",
    first_line_chars: str | None = "200",
    left: str | None = None,
    right: str | None = None,
) -> None:
    ppr = ensure_ppr(paragraph)
    ind = ppr.find("w:ind", NS)
    if ind is None:
        ind = ET.SubElement(ppr, W + "ind")
    for key in ("leftChars", "rightChars", "hanging", "hangingChars"):
        ind.attrib.pop(W + key, None)
    if first_line is None:
        ind.attrib.pop(W + "firstLine", None)
    else:
        ind.set(W + "firstLine", first_line)
    if first_line_chars is None:
        ind.attrib.pop(W + "firstLineChars", None)
    else:
        ind.set(W + "firstLineChars", first_line_chars)
    if left is None:
        ind.attrib.pop(W + "left", None)
    else:
        ind.set(W + "left", left)
    if right is None:
        ind.attrib.pop(W + "right", None)
    else:
        ind.set(W + "right", right)


def remove_alignment(paragraph: ET.Element) -> None:
    ppr = ensure_ppr(paragraph)
    jc = ppr.find("w:jc", NS)
    if jc is not None:
        ppr.remove(jc)


def clear_runs(paragraph: ET.Element) -> None:
    for child in list(paragraph):
        if child.tag != W + "pPr":
            paragraph.remove(child)


def ensure_rpr(run: ET.Element) -> ET.Element:
    rpr = run.find("w:rPr", NS)
    if rpr is None:
        rpr = ET.Element(W + "rPr")
        run.insert(0, rpr)
    return rpr


def set_latin_font_slots(run: ET.Element) -> bool:
    text = run_text(run)
    if not re.search(r"[A-Za-z]", text):
        return False
    rpr = ensure_rpr(run)
    rfonts = rpr.find("w:rFonts", NS)
    if rfonts is None:
        rfonts = ET.SubElement(rpr, W + "rFonts")
    changed = False
    for key in ("ascii", "hAnsi", "cs"):
        if rfonts.get(W + key) != "Times New Roman":
            rfonts.set(W + key, "Times New Roman")
            changed = True
    return changed


def clear_run_bold(run: ET.Element) -> bool:
    rpr = run.find("w:rPr", NS)
    if rpr is None:
        return False
    changed = False
    for tag in ("b", "bCs"):
        node = rpr.find(f"w:{tag}", NS)
        if node is not None:
            rpr.remove(node)
            changed = True
    return changed


def set_run_font_size(run: ET.Element, half_points: str) -> bool:
    rpr = ensure_rpr(run)
    changed = False
    for tag in ("sz", "szCs"):
        node = rpr.find(f"w:{tag}", NS)
        if node is None:
            node = ET.SubElement(rpr, W + tag)
        if node.get(W + "val") != half_points:
            node.set(W + "val", half_points)
            changed = True
    return changed


def set_paragraph_run_font_size(paragraph: ET.Element, half_points: str) -> int:
    changed = 0
    for run in paragraph.findall("w:r", NS):
        if set_run_font_size(run, half_points):
            changed += 1
    return changed


def normalize_paragraph_runs(paragraph: ET.Element, *, clear_bold: bool) -> dict[str, int]:
    latin = 0
    bold = 0
    for run in paragraph.findall("w:r", NS):
        if set_latin_font_slots(run):
            latin += 1
        if clear_bold and clear_run_bold(run):
            bold += 1
    return {"latin_font_runs": latin, "bold_runs_cleared": bold}


def run_text(run: ET.Element) -> str:
    return "".join(node.text or "" for node in run.findall(".//w:t", NS))


def collect_run_donors(document_root: ET.Element) -> dict[str, ET.Element | None]:
    donors: dict[str, ET.Element | None] = {"cjk": None, "latin": None, "citation": None}
    for paragraph in candidate_body_text_paragraphs(document_root):
        for run in paragraph.findall("w:r", NS):
            text = run_text(run)
            if not text:
                continue
            rpr = run.find("w:rPr", NS)
            if rpr is None:
                continue
            if donors["citation"] is None and re.fullmatch(r"\[\d+\]", text.strip()) and rpr.find("w:vertAlign", NS) is not None:
                donors["citation"] = copy.deepcopy(rpr)
            if donors["latin"] is None and re.search(r"[A-Za-z0-9]", text) and not re.search(r"[\u4e00-\u9fff]", text):
                donors["latin"] = copy.deepcopy(rpr)
            if donors["cjk"] is None and re.search(r"[\u4e00-\u9fff]", text):
                donors["cjk"] = copy.deepcopy(rpr)
            if all(value is not None for value in donors.values()):
                break
        if all(value is not None for value in donors.values()):
            break
    return donors


def paragraph_style_id(paragraph: ET.Element) -> str:
    style = paragraph.find("./w:pPr/w:pStyle", NS)
    return style.get(W + "val", "") if style is not None else ""


def is_caption_text(text: str) -> bool:
    stripped = (text or "").strip()
    match = re.match(
        r"^[\u56fe\u8868]\s*(?:\d+|[一二三四五六七八九十]+)"
        r"(?:[-.\uff0d\uff0e](?:\d+|[一二三四五六七八九十]+))*"
        r"(?:\s+|[\u3000:：]\s*)(?P<title>\S.*)$",
        stripped,
        re.I,
    )
    if not match:
        return False
    title = (match.group("title") or "").strip()
    compact_title = re.sub(r"\s+", "", title)
    # Narrative follow-up paragraphs such as "图3-1展示了..." are body text,
    # not formal captions, and must not donate caption formatting.
    if compact_title.startswith(("展示", "进一步", "补充", "给出", "说明", "反映", "保留", "按照", "中", "里")):
        return False
    if len(title) > 80 and re.search(r"[。；;，,]", title):
        return False
    return True


def plan_contains_image_mutation(plan: dict[str, Any]) -> bool:
    if any(plan.get(key) for key in IMAGE_MUTATION_KEYS):
        return True
    for insertion in plan.get("insertions", []):
        for item in insertion.get("items", []):
            if item.get("type") == "image":
                return True
    return False


def plan_contains_global_ascii_font_repair(plan: dict[str, Any]) -> bool:
    for item in plan.get("english_font_slot_repairs", []):
        scope = str(item.get("scope") or "all_ascii_runs")
        if scope == "all_ascii_runs" and not item.get("surface_allowlist"):
            return True
    return False


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
    source_sha = sha256_file(source_docx).lower()
    if not path_bound_in_record(text, source_docx) or source_sha not in text:
        issues.append("transaction record does not bind the source DOCX path and SHA256")
    if not path_bound_in_record(text, output_docx):
        issues.append("transaction record does not bind the intended final/output DOCX path")
    if not path_bound_in_record(text, figure_manifest):
        issues.append("transaction record does not bind the figure manifest path")
    return issues


def protected_body_format_target(text: str) -> bool:
    stripped = (text or "").strip()
    lowered = stripped.lower()
    if is_caption_text(stripped):
        return True
    if re.match(r"^\[\d+\]", stripped):
        return True
    return any(lowered.startswith(prefix) for prefix in PROTECTED_TEXT_PREFIXES)


def is_headingish_text(text: str) -> bool:
    stripped = (text or "").strip()
    return bool(re.match(r"^(?:\d+(?:[．.]\d+){0,3}|第[一二三四五六七八九十]+章|摘\s*要|ABSTRACT|目\s*录|参考文献|致谢)\b", stripped, re.I))


def candidate_body_text_paragraphs(document_root: ET.Element) -> list[ET.Element]:
    candidates: list[ET.Element] = []
    body_started = False
    for paragraph in body_paragraphs(document_root):
        text = paragraph_text(paragraph).strip()
        if not text:
            continue
        if text.startswith("1 引言") or text.startswith("1．1") or text.startswith("1.1"):
            body_started = True
        if not body_started:
            continue
        if text == "参考文献":
            break
        if is_caption_text(text) or is_headingish_text(text):
            continue
        if paragraph_style_id(paragraph) and len(text) > 20:
            candidates.append(paragraph)
    return candidates


def body_text_template(document_root: ET.Element) -> ET.Element | None:
    candidates = candidate_body_text_paragraphs(document_root)
    return candidates[0] if candidates else None


def append_text_run(paragraph: ET.Element, text: str, rpr: ET.Element | None = None, *, superscript: bool = False, bold: bool | None = None) -> ET.Element:
    run = ET.SubElement(paragraph, W + "r")
    if rpr is not None:
        run.append(copy.deepcopy(rpr))
    if superscript or bold is not None:
        rpr_node = run.find("w:rPr", NS)
        if rpr_node is None:
            rpr_node = ET.Element(W + "rPr")
            run.insert(0, rpr_node)
        if superscript and rpr_node.find("w:vertAlign", NS) is None:
            va = ET.SubElement(rpr_node, W + "vertAlign")
            va.set(W + "val", "superscript")
        if bold is not None:
            for tag in ("b", "bCs"):
                existing = rpr_node.find(f"w:{tag}", NS)
                if bold:
                    if existing is None:
                        ET.SubElement(rpr_node, W + tag)
                elif existing is not None:
                    rpr_node.remove(existing)
    t = ET.SubElement(run, W + "t")
    if text.startswith(" ") or text.endswith(" "):
        t.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
    t.text = text
    return run


def normalize_body_rpr(rpr: ET.Element | None) -> ET.Element | None:
    if rpr is None:
        return None
    normalized = copy.deepcopy(rpr)
    for tag in ("b", "bCs"):
        node = normalized.find(f"w:{tag}", NS)
        if node is not None:
            normalized.remove(node)
    rfonts = normalized.find("w:rFonts", NS)
    if rfonts is None:
        rfonts = ET.SubElement(normalized, W + "rFonts")
    rfonts.set(W + "ascii", "Times New Roman")
    rfonts.set(W + "hAnsi", "Times New Roman")
    rfonts.set(W + "cs", "Times New Roman")
    if not rfonts.get(W + "eastAsia"):
        rfonts.set(W + "eastAsia", "\u5b8b\u4f53")
    return normalized


def split_text_chunks(text: str) -> list[tuple[str, str]]:
    chunks: list[tuple[str, str]] = []
    for piece in re.split(r"(\[\d+\]|[A-Za-z0-9_./<>:+-]+)", text):
        if not piece:
            continue
        if re.fullmatch(r"\[\d+\]", piece):
            chunks.append(("citation", piece))
        elif re.search(r"[A-Za-z0-9]", piece):
            chunks.append(("latin", piece))
        else:
            chunks.append(("cjk", piece))
    return chunks


def make_text_paragraph(text: str, template: ET.Element | None, donors: dict[str, ET.Element | None]) -> ET.Element:
    para = ET.Element(W + "p")
    para.append(clone_ppr(template))
    clear_runs(para)
    for kind, piece in split_text_chunks(text):
        if kind == "citation":
            append_text_run(para, piece, donors.get("citation") if donors.get("citation") is not None else donors.get("latin"), superscript=True)
        elif kind == "latin":
            append_text_run(para, piece, normalize_body_rpr(donors.get("latin") if donors.get("latin") is not None else donors.get("cjk")), bold=False)
        else:
            append_text_run(para, piece, normalize_body_rpr(donors.get("cjk") if donors.get("cjk") is not None else donors.get("latin")), bold=False)
    return para


def make_caption_paragraph(text: str, template: ET.Element | None, donors: dict[str, ET.Element | None]) -> ET.Element:
    para = make_text_paragraph(text, template, donors)
    set_alignment(para, "center")
    ppr = ensure_ppr(para)
    pstyle = ppr.find("w:pStyle", NS)
    if pstyle is not None:
        ppr.remove(pstyle)
    spacing = ppr.find("w:spacing", NS)
    if spacing is None:
        spacing = ET.SubElement(ppr, W + "spacing")
    spacing.set(W + "line", "240")
    spacing.set(W + "lineRule", "auto")
    spacing.set(W + "before", "120")
    spacing.set(W + "after", "120")
    ind = ppr.find("w:ind", NS)
    if ind is None:
        ind = ET.SubElement(ppr, W + "ind")
    ind.set(W + "firstLine", "0")
    ind.set(W + "left", "0")
    ind.set(W + "right", "0")
    ind.attrib.pop(W + "firstLineChars", None)
    ind.attrib.pop(W + "leftChars", None)
    set_paragraph_run_font_size(para, "21")
    return para


def max_docpr_id(document_root: ET.Element) -> int:
    result = 0
    for node in document_root.findall(".//wp:docPr", NS):
        try:
            result = max(result, int(node.get("id") or "0"))
        except ValueError:
            pass
    return result


def make_image_paragraph(rid: str, cx: int, cy: int, docpr_id: int, name: str) -> ET.Element:
    para = ET.Element(W + "p")
    ppr = ET.SubElement(para, W + "pPr")
    style = ET.SubElement(ppr, W + "pStyle")
    style.set(W + "val", "Normal")
    jc = ET.SubElement(ppr, W + "jc")
    jc.set(W + "val", "center")
    run = ET.SubElement(para, W + "r")
    drawing = ET.SubElement(run, W + "drawing")
    inline = ET.SubElement(drawing, WP + "inline")
    extent = ET.SubElement(inline, WP + "extent")
    extent.set("cx", str(cx))
    extent.set("cy", str(cy))
    effect = ET.SubElement(inline, WP + "effectExtent")
    for key in ("l", "t", "r", "b"):
        effect.set(key, "0")
    docpr = ET.SubElement(inline, WP + "docPr")
    docpr.set("id", str(docpr_id))
    docpr.set("name", name)
    ET.SubElement(inline, WP + "cNvGraphicFramePr")
    graphic = ET.SubElement(inline, A + "graphic")
    graphic_data = ET.SubElement(graphic, A + "graphicData")
    graphic_data.set("uri", "http://schemas.openxmlformats.org/drawingml/2006/picture")
    pic = ET.SubElement(graphic_data, PIC + "pic")
    nv = ET.SubElement(pic, PIC + "nvPicPr")
    cnvpr = ET.SubElement(nv, PIC + "cNvPr")
    cnvpr.set("id", "0")
    cnvpr.set("name", name)
    ET.SubElement(nv, PIC + "cNvPicPr")
    blip_fill = ET.SubElement(pic, PIC + "blipFill")
    blip = ET.SubElement(blip_fill, A + "blip")
    blip.set(R + "embed", rid)
    stretch = ET.SubElement(blip_fill, A + "stretch")
    ET.SubElement(stretch, A + "fillRect")
    sppr = ET.SubElement(pic, PIC + "spPr")
    xfrm = ET.SubElement(sppr, A + "xfrm")
    off = ET.SubElement(xfrm, A + "off")
    off.set("x", "0")
    off.set("y", "0")
    ext = ET.SubElement(xfrm, A + "ext")
    ext.set("cx", str(cx))
    ext.set("cy", str(cy))
    prst = ET.SubElement(sppr, A + "prstGeom")
    prst.set("prst", "rect")
    ET.SubElement(prst, A + "avLst")
    return para


def relationship_map(rels_root: ET.Element) -> dict[str, str]:
    result: dict[str, str] = {}
    for rel in rels_root.findall("pr:Relationship", NS):
        rid = rel.get("Id")
        target = rel.get("Target")
        if rid and target:
            result[rid] = target
    return result


def next_rid(rels_root: ET.Element) -> str:
    max_id = 0
    for rel in rels_root.findall("pr:Relationship", NS):
        rid = rel.get("Id", "")
        match = re.fullmatch(r"rId(\d+)", rid)
        if match:
            max_id = max(max_id, int(match.group(1)))
    return f"rId{max_id + 1}"


def add_image_relationship(rels_root: ET.Element, media_name: str) -> str:
    rid = next_rid(rels_root)
    rel = ET.SubElement(rels_root, PR + "Relationship")
    rel.set("Id", rid)
    rel.set("Type", "http://schemas.openxmlformats.org/officeDocument/2006/relationships/image")
    rel.set("Target", f"media/{media_name}")
    return rid


def ensure_png_content_type(types_root: ET.Element) -> bool:
    for node in types_root.findall("ct:Default", NS):
        if node.get("Extension") == "png":
            return False
    node = ET.SubElement(types_root, CT + "Default")
    node.set("Extension", "png")
    node.set("ContentType", "image/png")
    return True


def find_body_child_by_text(document_root: ET.Element, needle: str) -> ET.Element:
    body = document_root.find("w:body", NS)
    if body is None:
        raise ValueError("missing body")
    matches: list[ET.Element] = []
    for child in list(body):
        if child.tag == W + "p" and needle in paragraph_text(child):
            matches.append(child)
    caption_matches = [child for child in matches if is_caption_text(paragraph_text(child).strip())]
    if caption_matches:
        return caption_matches[-1]
    if matches:
        return matches[0]
    raise ValueError(f"anchor text not found: {needle}")


def find_unique_body_child_by_text(document_root: ET.Element, needle: str) -> ET.Element:
    body = document_root.find("w:body", NS)
    if body is None:
        raise ValueError("missing body")
    matches = [child for child in list(body) if child.tag == W + "p" and needle in paragraph_text(child)]
    if not matches:
        raise ValueError(f"anchor text not found: {needle}")
    if len(matches) != 1:
        raise ValueError(f"non-unique anchor text for bounded repair: {needle}")
    return matches[0]


def find_unique_paragraph_by_text(document_root: ET.Element, needle: str) -> ET.Element:
    matches = [paragraph for paragraph in all_paragraphs(document_root) if needle in paragraph_text(paragraph)]
    if not matches:
        raise ValueError(f"surface_allowlist anchor text not found: {needle}")
    if len(matches) != 1:
        raise ValueError(f"non-unique surface_allowlist anchor text: {needle}")
    return matches[0]


def surface_allowlist_paragraphs(document_root: ET.Element, allowlist: object) -> list[ET.Element]:
    if not isinstance(allowlist, list) or not allowlist:
        raise ValueError("surface_allowlist must be a non-empty list")
    paragraphs: list[ET.Element] = []
    seen: set[int] = set()
    for item in allowlist:
        if isinstance(item, str):
            needle = item
        elif isinstance(item, dict):
            needle = str(item.get("contains_text") or item.get("text") or item.get("anchor_text") or "")
        else:
            needle = ""
        if not needle.strip():
            raise ValueError("each surface_allowlist row requires contains_text/text/anchor_text")
        paragraph = find_unique_paragraph_by_text(document_root, needle)
        key = id(paragraph)
        if key not in seen:
            seen.add(key)
            paragraphs.append(paragraph)
    return paragraphs


def insert_after(body: ET.Element, anchor: ET.Element, new_nodes: list[ET.Element]) -> None:
    children = list(body)
    index = children.index(anchor)
    for offset, node in enumerate(new_nodes, start=1):
        body.insert(index + offset, node)


def replace_paragraph_text(paragraph: ET.Element, text: str, donors: dict[str, ET.Element | None]) -> None:
    ppr = paragraph.find("w:pPr", NS)
    ppr_clone = copy.deepcopy(ppr) if ppr is not None else ET.Element(W + "pPr")
    comment_starts = [node.get(W + "id", "") for node in paragraph.findall("w:commentRangeStart", NS)]
    comment_ends = [node.get(W + "id", "") for node in paragraph.findall("w:commentRangeEnd", NS)]
    comment_refs = [node.get(W + "id", "") for node in paragraph.findall(".//w:commentReference", NS)]
    clear_runs(paragraph)
    if paragraph.find("w:pPr", NS) is None:
        paragraph.insert(0, ppr_clone)
    for cid in comment_starts:
        if cid:
            node = ET.SubElement(paragraph, W + "commentRangeStart")
            node.set(W + "id", cid)
    for kind, piece in split_text_chunks(text):
        if kind == "citation":
            append_text_run(paragraph, piece, donors.get("citation") if donors.get("citation") is not None else donors.get("latin"), superscript=True)
        elif kind == "latin":
            append_text_run(paragraph, piece, normalize_body_rpr(donors.get("latin") if donors.get("latin") is not None else donors.get("cjk")), bold=False)
        else:
            append_text_run(paragraph, piece, normalize_body_rpr(donors.get("cjk") if donors.get("cjk") is not None else donors.get("latin")), bold=False)
    for cid in comment_ends:
        if cid:
            node = ET.SubElement(paragraph, W + "commentRangeEnd")
            node.set(W + "id", cid)
    for cid in comment_refs:
        if cid:
            run = ET.SubElement(paragraph, W + "r")
            rpr = ET.SubElement(run, W + "rPr")
            ET.SubElement(rpr, W + "rStyle").set(W + "val", "CommentReference")
            node = ET.SubElement(run, W + "commentReference")
            node.set(W + "id", cid)


def normalize_keyword_line(paragraph: ET.Element, label: str, content: str, donors: dict[str, ET.Element | None], *, english: bool) -> None:
    clear_runs(paragraph)
    label_donor = donors.get("latin" if english else "cjk")
    if label_donor is None:
        label_donor = donors.get("cjk")
    content_donor = donors.get("latin" if english else "cjk")
    if content_donor is None:
        content_donor = donors.get("cjk")
    append_text_run(paragraph, label, normalize_body_rpr(label_donor), bold=True)
    for kind, piece in split_text_chunks(content):
        append_text_run(paragraph, piece, normalize_body_rpr(donors.get("latin") if kind == "latin" else content_donor), bold=False)


def set_drawing_extents_by_rid(document_root: ET.Element, rid: str, cx: int, cy: int) -> int:
    changed = 0
    for drawing in document_root.findall(".//w:drawing", NS):
        rids = [node.get(R + "embed") or node.get(R + "link") for node in drawing.findall(".//a:blip", NS)]
        if rid not in rids:
            continue
        for extent in drawing.findall(".//wp:extent", NS):
            extent.set("cx", str(cx))
            extent.set("cy", str(cy))
            changed += 1
        for ext in drawing.findall(".//a:xfrm/a:ext", NS):
            ext.set("cx", str(cx))
            ext.set("cy", str(cy))
    return changed


def emu_for_image(path: Path, width_emu: int, max_height_emu: int | None = None) -> tuple[int, int]:
    with Image.open(path) as image:
        width, height = image.size
    cy = int(width_emu * height / width)
    if max_height_emu and cy > max_height_emu:
        scale = max_height_emu / cy
        return int(width_emu * scale), max_height_emu
    return width_emu, cy


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-docx", required=True)
    parser.add_argument("--output-docx", required=True)
    parser.add_argument("--plan", required=True)
    parser.add_argument("--report", required=True)
    parser.add_argument("--source-docx")
    parser.add_argument("--transaction-record")
    parser.add_argument("--figure-manifest")
    parser.add_argument("--allow-global-ascii-font-repair", action="store_true")
    args = parser.parse_args()

    input_docx = Path(args.input_docx).resolve()
    output_docx = Path(args.output_docx).resolve()
    plan_path = Path(args.plan).resolve()
    report_path = Path(args.report).resolve()
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    source_docx = Path(args.source_docx).resolve() if args.source_docx else None
    transaction_record = Path(args.transaction_record).resolve() if args.transaction_record else None
    figure_manifest = Path(args.figure_manifest).resolve() if args.figure_manifest else None
    if plan_contains_image_mutation(plan):
        missing = []
        if source_docx is None:
            missing.append("--source-docx")
        if transaction_record is None:
            missing.append("--transaction-record")
        if figure_manifest is None:
            missing.append("--figure-manifest")
        if missing:
            raise SystemExit("image/display mutations require " + ", ".join(missing))
        if source_docx != input_docx:
            raise SystemExit("--source-docx must match --input-docx for comment-content image/display mutation")
        if not transaction_record.exists():
            raise SystemExit(f"--transaction-record does not exist: {transaction_record}")
        if not figure_manifest.exists():
            raise SystemExit(f"--figure-manifest does not exist: {figure_manifest}")
        transaction_issues = validate_transaction_record_binding(
            transaction_record,
            source_docx=source_docx,
            output_docx=output_docx,
            figure_manifest=figure_manifest,
        )
        if transaction_issues:
            raise SystemExit("; ".join(transaction_issues))
    if plan_contains_global_ascii_font_repair(plan) and not args.allow_global_ascii_font_repair:
        raise SystemExit(
            "all_ascii_runs english_font_slot_repairs requires surface_allowlist "
            "or --allow-global-ascii-font-repair"
        )
    output_docx.parent.mkdir(parents=True, exist_ok=True)
    report_path.parent.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(input_docx, "r") as zf:
        document_root = read_xml(zf, "word/document.xml")
        rels_root = read_xml(zf, "word/_rels/document.xml.rels")
        types_root = read_xml(zf, "[Content_Types].xml")
        original_entries = {name: zf.read(name) for name in zf.namelist()}

    donors = collect_run_donors(document_root)
    body = document_root.find("w:body", NS)
    if body is None:
        raise SystemExit("missing w:body")
    rels = relationship_map(rels_root)
    body_template = body_text_template(document_root)
    media_replacements: dict[str, bytes] = {}
    rels_dirty = False
    types_dirty = False
    report: dict[str, Any] = {
        "schema": "graduation-project-builder.comment-content-repair-report.v1",
        "input_docx": str(input_docx),
        "input_docx_sha256": sha256_file(input_docx),
        "plan": str(plan_path),
        "changes": [],
    }

    for item in plan.get("media_replacements", []):
        media_name = str(item["media_name"])
        asset_path = Path(item["asset_path"]).resolve()
        target = f"word/media/{media_name}"
        media_replacements[target] = asset_path.read_bytes()
        report["changes"].append({"type": "media_replacement", "media": target, "asset": str(asset_path), "sha256": sha256_file(asset_path)})

    for item in plan.get("new_media", []):
        asset_path = Path(item["asset_path"]).resolve()
        media_name = str(item.get("media_name") or asset_path.name)
        rid = add_image_relationship(rels_root, media_name)
        rels_dirty = True
        item["assigned_rid"] = rid
        media_replacements[f"word/media/{media_name}"] = asset_path.read_bytes()
        types_dirty = ensure_png_content_type(types_root) or types_dirty
        report["changes"].append({"type": "new_media", "rid": rid, "media": f"word/media/{media_name}", "asset": str(asset_path), "sha256": sha256_file(asset_path)})

    max_doc_id = max_docpr_id(document_root)
    for insertion in plan.get("insertions", []):
        anchor = find_body_child_by_text(document_root, str(insertion["after_text"]))
        nodes: list[ET.Element] = []
        for entry in insertion.get("items", []):
            kind = entry.get("type")
            if kind == "paragraph":
                nodes.append(make_text_paragraph(str(entry["text"]), body_template if body_template is not None else anchor, donors))
            elif kind == "caption":
                nodes.append(make_caption_paragraph(str(entry["text"]), anchor, donors))
            elif kind == "image":
                media_name = str(entry.get("media_name") or Path(entry["asset_path"]).name)
                rid = next((m.get("assigned_rid") for m in plan.get("new_media", []) if str(m.get("media_name") or Path(m["asset_path"]).name) == media_name), "")
                if not rid:
                    rid = add_image_relationship(rels_root, media_name)
                    rels_dirty = True
                    media_replacements[f"word/media/{media_name}"] = Path(entry["asset_path"]).resolve().read_bytes()
                    types_dirty = ensure_png_content_type(types_root) or types_dirty
                max_doc_id += 1
                cx, cy = emu_for_image(Path(entry["asset_path"]).resolve(), int(entry.get("width_emu", 4680000)), int(entry.get("max_height_emu", 3600000)))
                nodes.append(make_image_paragraph(rid, cx, cy, max_doc_id, media_name))
        insert_after(body, anchor, nodes)
        report["changes"].append({"type": "insertion", "after_text": insertion["after_text"], "count": len(nodes)})

    for replacement in plan.get("paragraph_replacements", []):
        para = find_body_child_by_text(document_root, str(replacement["contains_text"]))
        replace_paragraph_text(para, str(replacement["text"]), donors)
        report["changes"].append({"type": "paragraph_replacement", "contains_text": replacement["contains_text"]})

    for insertion in plan.get("insert_after_existing", []):
        anchor = find_body_child_by_text(document_root, str(insertion["after_text"]))
        template = body_template if body_template is not None else anchor
        nodes = [make_text_paragraph(str(text), template, donors) for text in insertion.get("paragraphs", [])]
        insert_after(body, anchor, nodes)
        report["changes"].append({"type": "insert_after_existing", "after_text": insertion["after_text"], "count": len(nodes)})

    for item in plan.get("abstract_metric_repairs", []):
        para = find_unique_body_child_by_text(document_root, str(item["contains_text"]))
        set_paragraph_metrics(
            para,
            first_line_chars=str(item.get("firstLineChars")) if item.get("firstLineChars") is not None else None,
            line=str(item.get("line")) if item.get("line") is not None else None,
        )
        report["changes"].append({"type": "abstract_metric_repair", "contains_text": item["contains_text"]})

    for item in plan.get("keyword_repairs", []):
        para = find_unique_body_child_by_text(document_root, str(item["contains_text"]))
        normalize_keyword_line(para, str(item["label"]), str(item["content"]), donors, english=bool(item.get("english")))
        report["changes"].append({"type": "keyword_repair", "contains_text": item["contains_text"]})

    for item in plan.get("body_paragraph_format_repairs", []):
        para = find_unique_body_child_by_text(document_root, str(item["contains_text"]))
        if protected_body_format_target(paragraph_text(para)):
            raise SystemExit(
                "body_paragraph_format_repairs target is not a body_text paragraph: "
                + str(item["contains_text"])
            )
        set_style_id(para, str(item.get("style_id") or "1"))
        set_spacing(
            para,
            line=str(item.get("line") or "360"),
            before=str(item.get("before") if item.get("before") is not None else "0"),
            after=str(item.get("after") if item.get("after") is not None else "0"),
        )
        set_indent(
            para,
            first_line=str(item.get("firstLine") or "480"),
            first_line_chars=str(item.get("firstLineChars") or "200"),
        )
        if bool(item.get("remove_alignment", True)):
            remove_alignment(para)
        if bool(item.get("resplit_runs", False)):
            replace_paragraph_text(para, paragraph_text(para), donors)
        run_changes = normalize_paragraph_runs(para, clear_bold=bool(item.get("clear_bold", True)))
        report["changes"].append({"type": "body_paragraph_format_repair", "contains_text": item["contains_text"], **run_changes})

    for item in plan.get("caption_format_repairs", []):
        para = find_body_child_by_text(document_root, str(item["contains_text"]))
        set_style_id(para, None)
        set_alignment(para, "center")
        set_spacing(
            para,
            line=str(item.get("line") or "240"),
            before=str(item.get("before") if item.get("before") is not None else "120"),
            after=str(item.get("after") if item.get("after") is not None else "120"),
        )
        set_indent(para, first_line="0", first_line_chars=None, left="0", right="0")
        run_changes = normalize_paragraph_runs(para, clear_bold=bool(item.get("clear_bold", True)))
        font_size_runs = set_paragraph_run_font_size(para, str(item.get("font_size") or "21"))
        report["changes"].append(
            {
                "type": "caption_format_repair",
                "contains_text": item["contains_text"],
                "font_size_runs": font_size_runs,
                **run_changes,
            }
        )

    for item in plan.get("english_font_slot_repairs", []):
        scope = str(item.get("scope") or "all_ascii_runs")
        changed = 0
        if scope == "all_ascii_runs":
            allowlist = item.get("surface_allowlist")
            paragraphs = (
                surface_allowlist_paragraphs(document_root, allowlist)
                if allowlist
                else all_paragraphs(document_root)
            )
            for paragraph in paragraphs:
                changed += normalize_paragraph_runs(paragraph, clear_bold=False)["latin_font_runs"]
        else:
            para = find_body_child_by_text(document_root, str(item["contains_text"]))
            changed += normalize_paragraph_runs(para, clear_bold=bool(item.get("clear_bold", False)))["latin_font_runs"]
        report["changes"].append({"type": "english_font_slot_repair", "scope": scope, "changed_runs": changed})

    for item in plan.get("display_extents", []):
        rid = str(item["rid"])
        target = rels.get(rid, "")
        media_name = Path(target).name
        asset = Path(item.get("asset_path") or "")
        if not asset.exists() and media_name:
            repl_target = Path("word/media") / media_name
            if str(repl_target).replace("\\", "/") in media_replacements:
                temp = report_path.parent / f"_extent_{media_name}"
                temp.write_bytes(media_replacements[str(repl_target).replace("\\", "/")])
                asset = temp
        if not asset.exists():
            continue
        cx, cy = emu_for_image(asset, int(item.get("width_emu", 4680000)), int(item.get("max_height_emu", 3600000)))
        changed = set_drawing_extents_by_rid(document_root, rid, cx, cy)
        report["changes"].append({"type": "display_extent", "rid": rid, "cx": cx, "cy": cy, "changed": changed})

    for item in plan.get("reference_entries", []):
        text = str(item["text"])
        anchor = None
        for child in reversed(list(body)):
            if child.tag == W + "p" and re.match(r"^\[\d+\]", paragraph_text(child).strip()):
                anchor = child
                break
        if anchor is None:
            raise ValueError("no reference-entry anchor found")
        para = make_text_paragraph(text, anchor, donors)
        insert_after(body, anchor, [para])
        report["changes"].append({"type": "reference_entry", "text": text[:80]})

    document_bytes = ET.tostring(document_root, encoding="utf-8", xml_declaration=True)
    rels_bytes = ET.tostring(rels_root, encoding="utf-8", xml_declaration=True) if rels_dirty else original_entries["word/_rels/document.xml.rels"]
    types_bytes = ET.tostring(types_root, encoding="utf-8", xml_declaration=True) if types_dirty else original_entries["[Content_Types].xml"]
    with zipfile.ZipFile(output_docx, "w", compression=zipfile.ZIP_DEFLATED) as out:
        written: set[str] = set()
        for name, data in original_entries.items():
            if name == "word/document.xml":
                data = document_bytes
            elif name == "word/_rels/document.xml.rels":
                data = rels_bytes
            elif name == "[Content_Types].xml":
                data = types_bytes
            elif name in media_replacements:
                data = media_replacements[name]
            out.writestr(name, data)
            written.add(name)
        for name, data in media_replacements.items():
            if name not in written:
                out.writestr(name, data)
                written.add(name)

    report["output_docx"] = str(output_docx)
    report["output_docx_sha256"] = sha256_file(output_docx)
    if plan_contains_image_mutation(plan) and figure_manifest is not None and source_docx is not None:
        from thesis_figure_contract import validate_figure_manifest

        manifest = json.loads(figure_manifest.read_text(encoding="utf-8"))
        manifest_issues = validate_figure_manifest(
            manifest,
            final_docx=output_docx,
            source_docx=source_docx,
            manifest_path=figure_manifest,
        )
        report["figure_manifest_path"] = str(figure_manifest)
        report["transaction_record_path"] = str(transaction_record) if transaction_record is not None else ""
        report["figure_manifest_issues"] = manifest_issues
        if manifest_issues:
            report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            for issue in manifest_issues:
                print(issue, file=sys.stderr)
            return 1
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output_docx": str(output_docx), "sha256": report["output_docx_sha256"], "changes": len(report["changes"])}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
