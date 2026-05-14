#!/usr/bin/env python3
"""Close out common thesis format blockers in a bounded DOCX copy.

Owned surfaces:
- body chapter page-start ownership on level-1 headings
- level-1/level-2 heading direct-bold cleanup only
- figure/table caption direct bold cleanup and table-caption keepNext binding
- blank visible body paragraphs between prose paragraphs
- redundant hard page breaks or blank paragraphs immediately before chapter
  headings that already own ``pageBreakBefore``

The script rewrites only ``word/document.xml`` in a fresh output DOCX. It does
not touch media, relationships, styles, numbering, headers, or footers.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
from copy import deepcopy
import json
import re
import shutil
import tempfile
import zipfile
from pathlib import Path
import xml.etree.ElementTree as ET


W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
A_NS = "http://schemas.openxmlformats.org/drawingml/2006/main"
WP_NS = "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing"
W = f"{{{W_NS}}}"
NS = {"w": W_NS, "a": A_NS, "wp": WP_NS}

ET.register_namespace("w", W_NS)
ET.register_namespace("a", A_NS)
ET.register_namespace("wp", WP_NS)


def qn(local: str) -> str:
    return f"{W}{local}"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def paragraph_text(paragraph: ET.Element) -> str:
    return "".join(node.text or "" for node in paragraph.findall(".//w:t", NS))


def element_text(element: ET.Element) -> str:
    return "".join(node.text or "" for node in element.findall(".//w:t", NS))


def compact_text(text: str) -> str:
    return re.sub(r"[\s\u3000\u25a1]+", "", text or "").lower()


def heading_level(text: str) -> int | None:
    stripped = (text or "").strip().replace("\uff0e", ".").replace("\u3002", ".")
    if "\t" in stripped or "\u2026" in stripped:
        return None
    if re.match(r"^\u7b2c[0-9\u4e00-\u9fff]+\u7ae0", stripped):
        return 1
    if re.match(r"^\d{1,2}\s+\S", stripped):
        return 1
    if re.match(r"^\d{1,2}\.\d{1,2}\s+\S", stripped):
        return 2
    if re.match(r"^\d{1,2}\.\d{1,2}\.\d{1,2}\s+\S", stripped):
        return 3
    return None


def looks_like_toc_entry(text: str, style_id: str = "") -> bool:
    stripped = (text or "").strip()
    if style_id.lower().startswith("toc"):
        return True
    if "\t" in stripped or "\u2026" in stripped:
        return True
    return bool(re.search(r"\d+\s*$", stripped)) and heading_level(re.sub(r"\s*\d+\s*$", "", stripped)) is not None


def is_toc_style_id(style_id: str) -> bool:
    normalized = (style_id or "").strip().upper()
    return normalized.startswith("TOC") or normalized in {"13", "16", "17"}


def is_toc_title(text: str) -> bool:
    return compact_text(text) in {"\u76ee\u5f55", "contents", "tableofcontents"}


def is_reference_heading(text: str) -> bool:
    return compact_text(text) in {"\u53c2\u8003\u6587\u732e", "references", "bibliography"}


def is_conclusion_heading(text: str) -> bool:
    return compact_text(text) in {"\u7ed3\u8bba", "conclusion", "conclusions"}


def is_acknowledgement_heading(text: str) -> bool:
    return compact_text(text) in {
        "\u81f4\u8c22",
        "\u81f4\u8b1d",
        "acknowledgement",
        "acknowledgements",
        "acknowledgment",
        "acknowledgments",
    }


def is_tail_heading(text: str) -> bool:
    return is_conclusion_heading(text) or is_reference_heading(text) or is_acknowledgement_heading(text)


def remove_page_break_before(paragraph: ET.Element) -> bool:
    ppr = paragraph.find("./w:pPr", NS)
    if ppr is None:
        return False
    changed = False
    for node in list(ppr.findall("./w:pageBreakBefore", NS)):
        ppr.remove(node)
        changed = True
    return changed


def caption_kind(text: str) -> str | None:
    match = re.match(r"^\s*([\u56fe\u8868])\s*\d{1,2}(?:[-\u2010-\u2015\.]\d{1,2})?\s+\S", text or "")
    if not match:
        return None
    return "figure" if match.group(1) == "\u56fe" else "table"


def has_image(paragraph: ET.Element) -> bool:
    return (
        paragraph.find(".//w:drawing", NS) is not None
        or paragraph.find(".//w:pict", NS) is not None
        or paragraph.find(".//w:object", NS) is not None
    )


def has_page_break(paragraph: ET.Element) -> bool:
    return any(br.attrib.get(qn("type"), "textWrapping") == "page" for br in paragraph.findall(".//w:br", NS))


def has_page_break_before(paragraph: ET.Element) -> bool:
    return paragraph.find("./w:pPr/w:pageBreakBefore", NS) is not None


def has_section_break(paragraph: ET.Element) -> bool:
    return paragraph.find("./w:pPr/w:sectPr", NS) is not None


def removable_blank_paragraph(paragraph: ET.Element) -> bool:
    return (
        not paragraph_text(paragraph).strip()
        and not has_image(paragraph)
        and not has_section_break(paragraph)
        and not has_page_break(paragraph)
    )


def table_has_math(table: ET.Element) -> bool:
    return any("officeDocument/2006/math" in node.tag for node in table.iter())


def nearest_visible_text_from_previous_body_child(child: ET.Element) -> str:
    if child.tag == qn("p"):
        return paragraph_text(child).strip()
    if child.tag == qn("tbl") and not table_has_math(child):
        return element_text(child).strip()
    return ""


def ensure_ppr(paragraph: ET.Element) -> ET.Element:
    ppr = paragraph.find("./w:pPr", NS)
    if ppr is None:
        ppr = ET.Element(qn("pPr"))
        paragraph.insert(0, ppr)
    return ppr


def remove_direct_bold(rpr: ET.Element) -> bool:
    changed = False
    for child in list(rpr):
        if child.tag in {qn("b"), qn("bCs")}:
            rpr.remove(child)
            changed = True
    return changed


def add_page_break_before(paragraph: ET.Element) -> bool:
    ppr = ensure_ppr(paragraph)
    if ppr.find("./w:pageBreakBefore", NS) is not None:
        return False
    ppr.insert(0, ET.Element(qn("pageBreakBefore")))
    return True


def remove_page_break_runs(paragraph: ET.Element) -> int:
    removed = 0
    for run in list(paragraph.findall("./w:r", NS)):
        for br in list(run.findall("./w:br", NS)):
            if br.attrib.get(qn("type"), "textWrapping") != "page":
                continue
            run.remove(br)
            removed += 1
        if (
            not list(run.findall("./w:t", NS))
            and run.find(".//w:drawing", NS) is None
            and run.find(".//w:pict", NS) is None
            and run.find(".//w:object", NS) is None
            and run.find("./w:tab", NS) is None
            and run.find("./w:br", NS) is None
        ):
            paragraph.remove(run)
    return removed


def ensure_keep_next(paragraph: ET.Element) -> bool:
    ppr = ensure_ppr(paragraph)
    node = ppr.find("./w:keepNext", NS)
    if node is not None:
        current = node.get(qn("val"))
        if current in {None, "1", "true", "True", "on", "ON"}:
            return False
        node.attrib.pop(qn("val"), None)
        return True
    ppr.append(ET.Element(qn("keepNext")))
    return True


def ensure_keep_lines(paragraph: ET.Element) -> bool:
    ppr = ensure_ppr(paragraph)
    node = ppr.find("./w:keepLines", NS)
    if node is not None:
        current = node.get(qn("val"))
        if current in {None, "1", "true", "True", "on", "ON"}:
            return False
        node.attrib.pop(qn("val"), None)
        return True
    ppr.append(ET.Element(qn("keepLines")))
    return True


def move_sectpr(source: ET.Element, target: ET.Element) -> bool:
    source_ppr = source.find("./w:pPr", NS)
    if source_ppr is None:
        return False
    sect_pr = source_ppr.find("./w:sectPr", NS)
    if sect_pr is None:
        return False
    target_ppr = ensure_ppr(target)
    existing_target = target_ppr.find("./w:sectPr", NS)
    if existing_target is not None:
        target_ppr.remove(existing_target)
    source_ppr.remove(sect_pr)
    target_ppr.append(sect_pr)
    return True


def paragraph_style_id(paragraph: ET.Element) -> str:
    ppr = paragraph.find("./w:pPr", NS)
    if ppr is None:
        return ""
    style = ppr.find("./w:pStyle", NS)
    return style.get(qn("val"), "") if style is not None else ""


def is_generated_figure_followup(text: str) -> bool:
    return str(text or "").strip().startswith("\u8be5\u56fe\u5c55\u793a\u4e86")


def first_body_prose_donor(children: list[ET.Element]) -> tuple[ET.Element | None, ET.Element | None]:
    body_started = False
    for child in children:
        if child.tag != qn("p"):
            continue
        text = paragraph_text(child).strip()
        if is_reference_heading(text):
            break
        if heading_level(text) == 1:
            body_started = True
            continue
        if (
            not body_started
            or not text
            or heading_level(text) is not None
            or caption_kind(text) is not None
            or has_image(child)
            or is_toc_style_id(paragraph_style_id(child))
        ):
            continue
        ppr = child.find("./w:pPr", NS)
        rpr = None
        for run in child.findall("./w:r", NS):
            if paragraph_text(run).strip() and run.find(".//w:drawing", NS) is None:
                rpr = run.find("./w:rPr", NS)
                break
        return deepcopy(ppr) if ppr is not None else None, deepcopy(rpr) if rpr is not None else None
    return None, None


def apply_body_prose_donor(paragraph: ET.Element, donor_ppr: ET.Element | None, donor_rpr: ET.Element | None) -> bool:
    changed = False
    existing_ppr = paragraph.find("./w:pPr", NS)
    if donor_ppr is not None:
        if existing_ppr is not None:
            paragraph.remove(existing_ppr)
        paragraph.insert(0, deepcopy(donor_ppr))
        changed = True
    elif existing_ppr is not None:
        for node in list(existing_ppr):
            if node.tag in {qn("pStyle"), qn("tabs")}:
                existing_ppr.remove(node)
                changed = True
    for run in paragraph.findall("./w:r", NS):
        if not paragraph_text(run).strip() or run.find(".//w:drawing", NS) is not None:
            continue
        old_rpr = run.find("./w:rPr", NS)
        if donor_rpr is not None:
            if old_rpr is not None:
                run.remove(old_rpr)
            run.insert(0, deepcopy(donor_rpr))
            changed = True
        elif old_rpr is not None:
            for node in list(old_rpr):
                if node.tag in {qn("b"), qn("bCs")}:
                    old_rpr.remove(node)
                    changed = True
    return changed


def run_visible_text(run: ET.Element) -> str:
    return "".join(node.text or "" for node in run.findall("./w:t", NS))


def has_cjk(text: str) -> bool:
    return any("\u4e00" <= char <= "\u9fff" for char in text or "")


def has_ascii_alnum(text: str) -> bool:
    return any(("A" <= char <= "Z") or ("a" <= char <= "z") or ("0" <= char <= "9") for char in text or "")


def split_ascii_segments(text: str) -> list[str]:
    if not text:
        return []
    segments: list[str] = []
    cursor = 0
    for match in re.finditer(r"[A-Za-z0-9][A-Za-z0-9_.+\-/]*", text):
        if match.start() > cursor:
            segments.append(text[cursor : match.start()])
        segments.append(match.group(0))
        cursor = match.end()
    if cursor < len(text):
        segments.append(text[cursor:])
    return [segment for segment in segments if segment]


def make_text_run(text: str, rpr: ET.Element | None) -> ET.Element:
    run = ET.Element(qn("r"))
    if rpr is not None:
        run.append(deepcopy(rpr))
    node = ET.SubElement(run, qn("t"))
    if text.startswith(" ") or text.endswith(" "):
        node.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
    node.text = text
    return run


def split_mixed_script_runs(paragraph: ET.Element) -> int:
    split_count = 0
    for run in list(paragraph.findall("./w:r", NS)):
        if run.find(".//w:drawing", NS) is not None or run.find(".//w:pict", NS) is not None:
            continue
        text_nodes = run.findall("./w:t", NS)
        if len(text_nodes) != 1:
            continue
        text = text_nodes[0].text or ""
        if not (has_cjk(text) and has_ascii_alnum(text)):
            continue
        rpr = run.find("./w:rPr", NS)
        parent_children = list(paragraph)
        insert_at = parent_children.index(run)
        paragraph.remove(run)
        for offset, segment in enumerate(split_ascii_segments(text)):
            paragraph.insert(insert_at + offset, make_text_run(segment, deepcopy(rpr) if rpr is not None else None))
        split_count += 1
    return split_count


def remove_heading_direct_bold(paragraph: ET.Element, level: int) -> dict[str, object]:
    changed_runs = 0
    for run in paragraph.findall("./w:r", NS):
        if not paragraph_text(run).strip() or run.find(".//w:drawing", NS) is not None:
            continue
        rpr = run.find("./w:rPr", NS)
        if rpr is not None and remove_direct_bold(rpr):
            changed_runs += 1
    return {"level": level, "changed_runs": changed_runs}


def normalize_caption(paragraph: ET.Element, kind: str) -> dict[str, object]:
    changed_runs = 0
    for run in paragraph.findall("./w:r", NS):
        if not paragraph_text(run):
            continue
        rpr = run.find("./w:rPr", NS)
        changed = remove_direct_bold(rpr) if rpr is not None else False
        if changed:
            changed_runs += 1
    keep_next_added = ensure_keep_next(paragraph) if kind == "table" else False
    return {"kind": kind, "changed_runs": changed_runs, "keep_next_added": keep_next_added}


def repair_document(root: ET.Element, operations: set[str]) -> dict[str, object]:
    body = root.find("./w:body", NS)
    if body is None:
        raise RuntimeError("word/document.xml has no w:body")
    children = list(body)
    toc_seen = False
    body_started = False
    first_chapter_seen = False
    heading_changes: list[dict[str, object]] = []
    heading_direct_bold_changes: list[dict[str, object]] = []
    caption_changes: list[dict[str, object]] = []
    chapter_page_breaks: list[str] = []
    blanks_removed: list[dict[str, object]] = []
    chapter_inline_page_breaks_removed: list[dict[str, object]] = []
    chapter_preceding_blank_paragraphs_removed: list[dict[str, object]] = []
    body_toc_followups_repaired: list[dict[str, object]] = []
    body_toc_followup_mixed_runs_split: list[dict[str, object]] = []
    duplicate_figure_followups_removed: list[dict[str, object]] = []
    chapter_summary_keep_next_added: list[dict[str, object]] = []
    chapter_summary_keep_lines_added: list[dict[str, object]] = []
    misplaced_subheading_page_breaks_removed: list[dict[str, object]] = []
    tail_page_breaks_added: list[dict[str, object]] = []
    tail_keep_next_added: list[dict[str, object]] = []
    tail_following_breaks_removed: list[dict[str, object]] = []
    tail_preceding_blank_paragraphs_removed: list[dict[str, object]] = []
    tail_section_boundaries_moved: list[dict[str, object]] = []
    donor_ppr, donor_rpr = first_body_prose_donor(children)

    idx = 0
    while idx < len(children):
        child = children[idx]
        if child.tag != qn("p"):
            idx += 1
            continue
        text = paragraph_text(child).strip()
        style_node = child.find("./w:pPr/w:pStyle", NS)
        style_id = style_node.attrib.get(qn("val"), "") if style_node is not None else ""
        if is_toc_title(text):
            toc_seen = True
            idx += 1
            continue
        if toc_seen and not body_started:
            if looks_like_toc_entry(text, style_id):
                idx += 1
                continue
            if heading_level(text) == 1:
                body_started = True
            else:
                idx += 1
                continue
        if body_started and is_reference_heading(text) and "tail-page-starts" not in operations:
            break

        level = heading_level(text)
        if body_started and level is not None:
            if "chapter-summary-keep-next" in operations and level in {2, 3} and "\u672c\u7ae0\u5c0f\u7ed3" in text:
                next_paragraph = next(
                    (
                        node
                        for node in children[idx + 1 :]
                        if node.tag == qn("p") and (paragraph_text(node).strip() or has_image(node) or has_section_break(node))
                    ),
                    None,
                )
                following_heading = None
                if next_paragraph is not None:
                    next_index = children.index(next_paragraph)
                    following_heading = next(
                        (
                            node
                            for node in children[next_index + 1 :]
                            if node.tag == qn("p") and paragraph_text(node).strip()
                        ),
                        None,
                    )
                if (
                    next_paragraph is not None
                    and following_heading is not None
                    and heading_level(paragraph_text(next_paragraph).strip()) is None
                    and heading_level(paragraph_text(following_heading).strip()) == 1
                ):
                    keep_next_added = ensure_keep_next(child)
                    keep_lines_added = ensure_keep_lines(next_paragraph)
                    if keep_next_added:
                        chapter_summary_keep_next_added.append(
                            {
                                "body_child_index": idx,
                                "heading": text,
                                "next_heading": paragraph_text(following_heading).strip(),
                            }
                        )
                    if keep_lines_added:
                        chapter_summary_keep_lines_added.append(
                            {
                                "body_child_index": next_index,
                                "summary_heading": text,
                                "next_heading": paragraph_text(following_heading).strip(),
                            }
                        )
            if "heading-direct-bold" in operations and level in {1, 2}:
                heading_direct = remove_heading_direct_bold(child, level)
                if heading_direct["changed_runs"]:
                    heading_direct["text"] = text
                    heading_direct_bold_changes.append(heading_direct)
            if level == 1:
                previous = next((node for node in reversed(children[:idx]) if node.tag == qn("p")), None)
                has_owner = has_page_break_before(child) or (
                    previous is not None and (has_page_break(previous) or has_section_break(previous))
                )
                if "chapter-page-starts" in operations and first_chapter_seen and not has_owner and add_page_break_before(child):
                    chapter_page_breaks.append(text)
                    heading_changes.append({"level": level, "text": text, "page_break_before_added": True})
                if "chapter-page-starts" in operations and first_chapter_seen and has_page_break_before(child):
                    removed_breaks = remove_page_break_runs(child)
                    if removed_breaks:
                        chapter_inline_page_breaks_removed.append({"text": text, "removed_breaks": removed_breaks})
                    while idx > 0 and children[idx - 1].tag == qn("p") and removable_blank_paragraph(children[idx - 1]):
                        body.remove(children[idx - 1])
                        children.pop(idx - 1)
                        idx -= 1
                        chapter_preceding_blank_paragraphs_removed.append({"text": text, "body_child_index": idx})
                first_chapter_seen = True
            elif (
                "repair-misplaced-heading-pagebreaks" in operations
                and level == 2
                and has_page_break_before(child)
            ):
                previous = next((node for node in reversed(children[:idx]) if node.tag == qn("p") and paragraph_text(node).strip()), None)
                if previous is not None and heading_level(paragraph_text(previous).strip()) == 1:
                    remove_page_break_before(child)
                    removed_breaks = remove_page_break_runs(child)
                    ensure_keep_next(previous)
                    ensure_keep_lines(previous)
                    misplaced_subheading_page_breaks_removed.append(
                        {
                            "subheading": text,
                            "chapter_heading": paragraph_text(previous).strip(),
                            "removed_inline_page_breaks": removed_breaks,
                        }
                    )
            idx += 1
            continue

        if body_started and "tail-page-starts" in operations and is_tail_heading(text):
            if add_page_break_before(child):
                tail_page_breaks_added.append({"text": text, "body_child_index": idx})
            if ensure_keep_next(child):
                tail_keep_next_added.append({"text": text, "body_child_index": idx})
            if ensure_keep_lines(child):
                tail_keep_next_added.append({"text": text, "body_child_index": idx, "keep_lines_added": True})
            while idx > 0 and children[idx - 1].tag == qn("p") and removable_blank_paragraph(children[idx - 1]):
                body.remove(children[idx - 1])
                children.pop(idx - 1)
                idx -= 1
                tail_preceding_blank_paragraphs_removed.append({"text": text, "body_child_index": idx})
            following_index = idx + 1
            while following_index < len(children) and children[following_index].tag == qn("p"):
                following = children[following_index]
                following_text = paragraph_text(following).strip()
                if following_text or has_image(following):
                    removed_pbb = remove_page_break_before(following)
                    removed_runs = remove_page_break_runs(following)
                    if removed_pbb or removed_runs:
                        tail_following_breaks_removed.append(
                            {
                                "tail_heading": text,
                                "following_text": following_text[:120],
                                "removed_page_break_before": removed_pbb,
                                "removed_inline_page_breaks": removed_runs,
                            }
                        )
                    break
                if has_section_break(following):
                    removed_runs = remove_page_break_runs(following)
                    if removed_runs:
                        tail_following_breaks_removed.append(
                            {
                                "tail_heading": text,
                                "following_text": "",
                                "removed_page_break_before": False,
                                "removed_inline_page_breaks": removed_runs,
                            }
                        )
                    break
                removed_pbb = remove_page_break_before(following)
                removed_runs = remove_page_break_runs(following)
                if removed_pbb or removed_runs:
                    tail_following_breaks_removed.append(
                        {
                            "tail_heading": text,
                            "following_text": "",
                            "removed_page_break_before": removed_pbb,
                            "removed_inline_page_breaks": removed_runs,
                        }
                    )
                following_index += 1
            idx += 1
            continue

        kind = caption_kind(text)
        if "caption-direct-format" in operations and body_started and kind is not None:
            change = normalize_caption(child, kind)
            change["text"] = text
            caption_changes.append(change)
            idx += 1
            continue

        if body_started and is_generated_figure_followup(text):
            prev_text = nearest_visible_text_from_previous_body_child(children[idx - 1]) if idx > 0 else ""
            if "duplicate-figure-followups" in operations and prev_text == text:
                body.remove(child)
                children.pop(idx)
                duplicate_figure_followups_removed.append({"body_child_index": idx, "text": text[:120]})
                continue
            if "body-toc-figure-followups" in operations and is_toc_style_id(style_id) and apply_body_prose_donor(child, donor_ppr, donor_rpr):
                split_count = split_mixed_script_runs(child)
                body_toc_followups_repaired.append(
                    {
                        "body_child_index": idx,
                        "text": text[:120],
                        "old_style_id": style_id,
                        "reason": "generated figure follow-up was mis-bound to TOC style and dot-leader tab",
                    }
                )
                if split_count:
                    body_toc_followup_mixed_runs_split.append(
                        {
                            "body_child_index": idx,
                            "split_run_count": split_count,
                            "text": text[:120],
                        }
                    )

        if "blank-body-paragraphs" in operations and (body_started or toc_seen) and not text and not has_image(child) and not has_section_break(child) and not has_page_break(child):
            prev_text = nearest_visible_text_from_previous_body_child(children[idx - 1]) if idx > 0 else ""
            next_text = paragraph_text(children[idx + 1]).strip() if idx + 1 < len(children) and children[idx + 1].tag == qn("p") else ""
            prev_kind = caption_kind(prev_text)
            next_kind = caption_kind(next_text)
            if (
                prev_text
                and next_text
                and not looks_like_toc_entry(prev_text)
                and not looks_like_toc_entry(next_text)
                and heading_level(prev_text) is None
                and heading_level(next_text) is None
                and prev_kind is None
                and next_kind is None
            ):
                body.remove(child)
                children.pop(idx)
                blanks_removed.append({"body_child_index": idx, "prev": prev_text[:80], "next": next_text[:80]})
                continue
        idx += 1

    if "repair-tail-section-boundaries" in operations:
        children = list(body)
        reference_heading_index = None
        acknowledgement_heading_index = None
        for position, node in enumerate(children):
            if node.tag != qn("p"):
                continue
            current_text = paragraph_text(node).strip()
            if reference_heading_index is None and is_reference_heading(current_text):
                reference_heading_index = position
                continue
            if reference_heading_index is not None and is_acknowledgement_heading(current_text):
                acknowledgement_heading_index = position
                break
        if reference_heading_index is not None and acknowledgement_heading_index is not None:
            section_source_index = None
            for position in range(reference_heading_index + 1, min(reference_heading_index + 4, acknowledgement_heading_index)):
                candidate = children[position]
                if (
                    candidate.tag == qn("p")
                    and not paragraph_text(candidate).strip()
                    and has_section_break(candidate)
                    and not has_image(candidate)
                ):
                    section_source_index = position
                    break
                if candidate.tag == qn("p") and paragraph_text(candidate).strip():
                    break
            target_index = None
            for position in range(acknowledgement_heading_index - 1, reference_heading_index, -1):
                candidate = children[position]
                if candidate.tag != qn("p"):
                    continue
                if paragraph_text(candidate).strip() and not has_section_break(candidate):
                    target_index = position
                    break
            if section_source_index is not None and target_index is not None and move_sectpr(children[section_source_index], children[target_index]):
                if removable_blank_paragraph(children[section_source_index]):
                    body.remove(children[section_source_index])
                tail_section_boundaries_moved.append(
                    {
                        "source_empty_paragraph_index": section_source_index,
                        "target_last_reference_index": target_index,
                        "reference_heading_index": reference_heading_index,
                        "acknowledgement_heading_index": acknowledgement_heading_index,
                    }
                )

    return {
        "heading_changes": heading_changes,
        "heading_direct_bold_changes": heading_direct_bold_changes,
        "caption_changes": caption_changes,
        "chapter_page_breaks_added": chapter_page_breaks,
        "blank_paragraphs_removed": blanks_removed,
        "chapter_inline_page_breaks_removed": chapter_inline_page_breaks_removed,
        "chapter_preceding_blank_paragraphs_removed": chapter_preceding_blank_paragraphs_removed,
        "body_toc_figure_followups_repaired": body_toc_followups_repaired,
        "body_toc_followup_mixed_runs_split": body_toc_followup_mixed_runs_split,
        "duplicate_figure_followups_removed": duplicate_figure_followups_removed,
        "chapter_summary_keep_next_added": chapter_summary_keep_next_added,
        "chapter_summary_keep_lines_added": chapter_summary_keep_lines_added,
        "misplaced_subheading_page_breaks_removed": misplaced_subheading_page_breaks_removed,
        "tail_page_breaks_added": tail_page_breaks_added,
        "tail_keep_next_added": tail_keep_next_added,
        "tail_following_breaks_removed": tail_following_breaks_removed,
        "tail_preceding_blank_paragraphs_removed": tail_preceding_blank_paragraphs_removed,
        "tail_section_boundaries_moved": tail_section_boundaries_moved,
    }


def write_docx_with_document_xml(input_docx: Path, output_docx: Path, document_xml: bytes) -> None:
    with tempfile.TemporaryDirectory() as tmp_name:
        tmp = Path(tmp_name)
        with zipfile.ZipFile(input_docx, "r") as zin:
            zin.extractall(tmp)
        (tmp / "word" / "document.xml").write_bytes(document_xml)
        if output_docx.exists():
            output_docx.unlink()
        archive_base = output_docx.with_suffix("")
        archive_path = Path(shutil.make_archive(str(archive_base), "zip", tmp))
        archive_path.replace(output_docx)


def parse_operations(raw: str | None) -> set[str]:
    allowed = {
        "chapter-page-starts",
        "heading-direct-bold",
        "caption-direct-format",
        "body-toc-figure-followups",
        "duplicate-figure-followups",
        "blank-body-paragraphs",
        "chapter-summary-keep-next",
        "repair-misplaced-heading-pagebreaks",
        "tail-page-starts",
        "repair-tail-section-boundaries",
    }
    if raw is None:
        return set(allowed)
    operations = {item.strip() for item in raw.split(",") if item.strip()}
    unknown = sorted(operations - allowed)
    if unknown:
        raise RuntimeError(f"unknown operation(s): {', '.join(unknown)}")
    if not operations:
        raise RuntimeError("at least one explicit operation is required")
    return operations


def main() -> int:
    parser = argparse.ArgumentParser(description="Repair bounded thesis closeout formatting in a fresh DOCX copy.")
    parser.add_argument("--input-docx", required=True)
    parser.add_argument("--output-docx", required=True)
    parser.add_argument("--report", required=True)
    parser.add_argument(
        "--operations",
        help=(
            "Comma-separated explicit operations: chapter-page-starts,heading-direct-bold,"
            "caption-direct-format,body-toc-figure-followups,duplicate-figure-followups,"
            "blank-body-paragraphs,chapter-summary-keep-next,repair-misplaced-heading-pagebreaks,"
            "tail-page-starts,repair-tail-section-boundaries. Omit for legacy all-operations mode."
        ),
    )
    args = parser.parse_args()

    input_docx = Path(args.input_docx)
    output_docx = Path(args.output_docx)
    report_path = Path(args.report)
    if input_docx.resolve() == output_docx.resolve():
        raise RuntimeError("output DOCX must be a fresh review copy")

    with zipfile.ZipFile(input_docx, "r") as zf:
        root = ET.fromstring(zf.read("word/document.xml"))
    operations = parse_operations(args.operations)
    changes = repair_document(root, operations)
    xml_bytes = ET.tostring(root, encoding="utf-8", xml_declaration=True)
    write_docx_with_document_xml(input_docx, output_docx, xml_bytes)

    payload = {
        "schema": "graduation-project-builder.thesis-closeout-format-repair.v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "input_docx": str(input_docx),
        "input_docx_sha256": sha256_file(input_docx),
        "output_docx": str(output_docx),
        "output_docx_sha256": sha256_file(output_docx),
        "operations": sorted(operations),
        "touched_scope": "word/document.xml bounded closeout surfaces selected by operations",
        **changes,
    }
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"output_docx": str(output_docx), "sha256": payload["output_docx_sha256"], "verdict": "pass"}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
