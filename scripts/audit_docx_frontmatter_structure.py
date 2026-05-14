#!/usr/bin/env python3
"""Audit front-matter order, abstract labels, keyword runs, and style refs."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import zipfile
from pathlib import Path
import xml.etree.ElementTree as ET


W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
W = f"{{{W_NS}}}"
NS = {"w": W_NS}


def qn(local: str) -> str:
    return f"{W}{local}"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().lower()


def paragraph_text(paragraph: ET.Element) -> str:
    return "".join(node.text or "" for node in paragraph.findall(".//w:t", NS))


def compact_text(text: str) -> str:
    return re.sub(r"[\s\u3000]+", "", text or "")


def paragraph_style_id(paragraph: ET.Element) -> str:
    node = paragraph.find("./w:pPr/w:pStyle", NS)
    return node.get(qn("val")) if node is not None else ""


def paragraph_numbering_level(paragraph: ET.Element) -> int | None:
    level_node = paragraph.find("./w:pPr/w:numPr/w:ilvl", NS)
    if level_node is None:
        return None
    value = level_node.get(qn("val"))
    try:
        return int(value) if value is not None else None
    except ValueError:
        return None


def style_ids(styles_root: ET.Element) -> set[str]:
    return {
        style.get(qn("styleId")) or ""
        for style in styles_root.findall("./w:style", NS)
    }


def has_tab(paragraph: ET.Element) -> bool:
    return paragraph.find(".//w:tab", NS) is not None


def is_toc_title(text: str) -> bool:
    return compact_text(text).lower() in {"\u76ee\u5f55", "contents", "tableofcontents"}


def is_toc_entry(paragraph: ET.Element) -> bool:
    text = paragraph_text(paragraph).strip()
    sid = paragraph_style_id(paragraph).lower()
    if sid.startswith("toc") or has_tab(paragraph) or "\u2026" in text:
        return True
    if re.search(r"(?:\d+|[ivxlcdm]+)\s*$", text or "", flags=re.IGNORECASE) is None:
        return False
    stripped = re.sub(r"(?:\d+|[ivxlcdm]+)\s*$", "", compact_text(text), flags=re.IGNORECASE).lower()
    return stripped in {"\u6458\u8981", "abstract", "\u5173\u952e\u8bcd", "keywords", "keyword", "keywords"}


def heading_level(text: str) -> int | None:
    stripped = (text or "").strip()
    if re.match(r"^\d{1,2}\s+\S", stripped):
        return 1
    if re.match(r"^\d{1,2}[.．]\d{1,2}\s+\S", stripped):
        return 2
    if re.match(r"^\d{1,2}[.．]\d{1,2}[.．]\d{1,2}\s+\S", stripped):
        return 3
    return None


def paragraph_heading_level(paragraph: ET.Element) -> int | None:
    numbering_level = paragraph_numbering_level(paragraph)
    if numbering_level is not None and numbering_level <= 3:
        return numbering_level + 1
    return heading_level(paragraph_text(paragraph))


def is_zh_abstract(text: str) -> bool:
    return compact_text(re.sub(r"[:：].*$", "", text or "")) == "\u6458\u8981"


def is_zh_keyword(text: str) -> bool:
    return compact_text(text).startswith("\u5173\u952e\u8bcd")


def is_en_abstract(text: str) -> bool:
    compact = re.sub(r"[\s:：]+", "", text or "").lower()
    return compact.startswith("abstract")


def is_en_keyword(text: str) -> bool:
    return (text or "").strip().lower().startswith(("key words", "keywords", "keyword"))


def find_index(paragraphs: list[ET.Element], predicate) -> int | None:
    for index, paragraph in enumerate(paragraphs, start=1):
        if predicate(paragraph):
            return index
    return None


def find_index_after(paragraphs: list[ET.Element], after_index: int | None, predicate) -> int | None:
    start = after_index or 0
    for index, paragraph in enumerate(paragraphs[start:], start=start + 1):
        if predicate(paragraph):
            return index
    return None


def run_text(run: ET.Element) -> str:
    return "".join(node.text or "" for node in run.findall(".//w:t", NS))


def run_is_bold(run: ET.Element) -> bool:
    rpr = run.find("./w:rPr", NS)
    if rpr is None:
        return False
    for tag in ("b", "bCs"):
        node = rpr.find(f"./w:{tag}", NS)
        if node is None:
            continue
        value = (node.get(qn("val")) or "").strip().lower()
        if value not in {"0", "false", "off"}:
            return True
    return False


def normalize_label_text(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "").replace("\uff1a", ":")).strip().lower()


def split_label_and_content_runs(
    runs: list[ET.Element],
    labels: tuple[str, ...],
) -> tuple[list[ET.Element], list[ET.Element]]:
    normalized_labels = {normalize_label_text(label) for label in labels}
    for end in range(1, len(runs) + 1):
        candidate = "".join(run_text(run) for run in runs[:end])
        if normalize_label_text(candidate) in normalized_labels:
            return runs[:end], runs[end:]
    return (runs[:1], runs[1:]) if runs else ([], [])


def paragraph_metric_detail(paragraph: ET.Element) -> dict[str, object]:
    ppr = paragraph.find("./w:pPr", NS)
    spacing = ppr.find("./w:spacing", NS) if ppr is not None else None
    ind = ppr.find("./w:ind", NS) if ppr is not None else None
    jc = ppr.find("./w:jc", NS) if ppr is not None else None
    return {
        "style_id": paragraph_style_id(paragraph),
        "spacing": {
            "before": spacing.get(qn("before")) if spacing is not None else "",
            "after": spacing.get(qn("after")) if spacing is not None else "",
            "line": spacing.get(qn("line")) if spacing is not None else "",
            "lineRule": spacing.get(qn("lineRule")) if spacing is not None else "",
        },
        "indent": {
            "firstLine": ind.get(qn("firstLine")) if ind is not None else "",
            "firstLineChars": ind.get(qn("firstLineChars")) if ind is not None else "",
            "left": ind.get(qn("left")) if ind is not None else "",
            "right": ind.get(qn("right")) if ind is not None else "",
            "hanging": ind.get(qn("hanging")) if ind is not None else "",
        },
        "jc": jc.get(qn("val")) if jc is not None else "",
    }


def label_run_detail(paragraph: ET.Element, labels: tuple[str, ...] = ()) -> dict[str, object]:
    runs = [run for run in paragraph.findall("./w:r", NS) if run_text(run)]
    label_runs, content_run_candidates = split_label_and_content_runs(runs, labels) if labels else ((runs[:1], runs[1:]) if runs else ([], []))
    label_text = "".join(run_text(run) for run in label_runs)
    content_runs = [run for run in content_run_candidates if run_text(run).strip()]
    return {
        "run_count": len(runs),
        "label_text": label_text,
        "label_bold": any(run_is_bold(run) for run in label_runs),
        "content_run_count": len(content_runs),
        "content_first_text_prefix": run_text(content_runs[0])[:40] if content_runs else "",
        "content_bold_count": sum(1 for run in content_runs if run_is_bold(run)),
        "label_content_split": bool(runs and content_runs),
    }


def surface_detail(paragraphs: list[ET.Element], index: int | None) -> dict[str, object] | None:
    if index is None:
        return None
    paragraph = paragraphs[index - 1]
    return {
        "paragraph_index": index,
        "text_prefix": paragraph_text(paragraph).strip()[:160],
        "metrics": paragraph_metric_detail(paragraph),
        "label_runs": label_run_detail(paragraph),
    }


def label_run_issues(paragraph: ET.Element, labels: tuple[str, ...], surface: str) -> list[str]:
    runs = [run for run in paragraph.findall("./w:r", NS) if run_text(run)]
    if not runs:
        return [f"{surface} has no visible runs"]
    label_runs, content_run_candidates = split_label_and_content_runs(runs, labels)
    label_text = "".join(run_text(run) for run in label_runs)
    if normalize_label_text(label_text) not in {normalize_label_text(label) for label in labels}:
        return [f"{surface} first run sequence is not an isolated label: {label_text!r}"]
    issues: list[str] = []
    if not any(run_is_bold(run) for run in label_runs):
        issues.append(f"{surface} label run is not bold")
    content_runs = [run for run in content_run_candidates if run_text(run).strip()]
    if not content_runs:
        issues.append(f"{surface} has no content run after label")
    elif surface == "en_keyword" and not (
        label_text.endswith(" ") or "".join(run_text(run) for run in content_run_candidates).startswith(" ")
    ):
        issues.append(f"{surface} content run must start with a separator space after the bold label")
    if any(run_is_bold(run) for run in content_runs):
        issues.append(f"{surface} content run is bold")
    return issues


def label_content_text(paragraph: ET.Element) -> str:
    runs = [run for run in paragraph.findall("./w:r", NS) if run_text(run)]
    return "".join(run_text(run) for run in runs[1:]).strip()


def frontmatter_metric_issues(paragraph: ET.Element, surface: str) -> list[str]:
    issues: list[str] = []
    ppr = paragraph.find("./w:pPr", NS)
    spacing = ppr.find("./w:spacing", NS) if ppr is not None else None
    ind = ppr.find("./w:ind", NS) if ppr is not None else None
    expected_spacing = {"line": "360", "lineRule": "auto"}
    for key, expected in expected_spacing.items():
        actual = spacing.get(qn(key)) if spacing is not None else None
        if actual != expected:
            issues.append(f"{surface} paragraph {key} must be {expected}, found {actual or '<missing>'}")
    for key in ("before", "after"):
        actual = spacing.get(qn(key)) if spacing is not None else None
        if actual not in {None, "0"}:
            issues.append(f"{surface} paragraph {key} must be template-compatible 0 or omitted, found {actual}")
    first_line = ind.get(qn("firstLine")) if ind is not None else None
    if first_line not in {"480", "482"}:
        issues.append(f"{surface} first-line indent must be template-compatible 480/482 twips (2 characters), found {first_line or '<missing>'}")
    first_line_chars = ind.get(qn("firstLineChars")) if ind is not None else None
    if first_line_chars != "200":
        issues.append(
            f"{surface} first-line indent must also include firstLineChars=200 for WPS/Word 2-character indentation, "
            f"found {first_line_chars or '<missing>'}"
        )
    return issues


def abstract_content_issues(paragraph: ET.Element, surface: str, *, english: bool) -> list[str]:
    content = label_content_text(paragraph)
    compact = compact_text(content).lower()
    if not content:
        return [f"{surface} has no abstract content after label"]
    if english and compact in {"abstract", "abstract:"}:
        return [f"{surface} content is only a duplicated abstract title, not the abstract body"]
    if not english and compact in {"\u6458\u8981", "\u6458\u8981\uff1a"}:
        return [f"{surface} content is only a duplicated abstract title, not the abstract body"]
    return []


def nonempty_between(paragraphs: list[ET.Element], start: int, stop: int) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for index in range(start + 1, stop):
        text = paragraph_text(paragraphs[index - 1]).strip()
        if text:
            rows.append({"paragraph": index, "text": text[:120]})
    return rows


def audit_frontmatter(final_docx: Path) -> dict[str, object]:
    with zipfile.ZipFile(final_docx, "r") as zf:
        document_root = ET.fromstring(zf.read("word/document.xml"))
        styles_root = ET.fromstring(zf.read("word/styles.xml"))
    styles = style_ids(styles_root)
    paragraphs = document_root.findall("./w:body/w:p", NS)
    issues: list[str] = []
    undefined = []
    for index, paragraph in enumerate(paragraphs, start=1):
        text = paragraph_text(paragraph).strip()
        style_id = paragraph_style_id(paragraph)
        if text and style_id and style_id not in styles:
            undefined.append({"paragraph": index, "style_id": style_id, "text": text[:120]})
    if undefined:
        issues.append(f"undefined non-empty paragraph styles: {undefined[:8]}")

    zh_abs = find_index(paragraphs, lambda p: is_zh_abstract(paragraph_text(p)) and not is_toc_entry(p))
    zh_key = find_index(paragraphs, lambda p: is_zh_keyword(paragraph_text(p)) and not is_toc_entry(p))
    en_abs = find_index(paragraphs, lambda p: is_en_abstract(paragraph_text(p)) and not is_toc_entry(p))
    en_key = find_index(paragraphs, lambda p: is_en_keyword(paragraph_text(p)) and not is_toc_entry(p))
    toc = find_index(paragraphs, lambda p: is_toc_title(paragraph_text(p)))
    first_body = find_index_after(paragraphs, toc, lambda p: paragraph_heading_level(p) == 1 and not is_toc_entry(p))
    surface_order = {
        "zh_abstract": zh_abs,
        "zh_keyword": zh_key,
        "en_abstract": en_abs,
        "en_keyword": en_key,
        "toc": toc,
        "first_body": first_body,
    }
    if any(value is None for value in surface_order.values()):
        issues.append(f"front-matter required surface missing: {surface_order}")
    elif not (zh_abs < zh_key < en_abs < en_key < toc < first_body):  # type: ignore[operator]
        issues.append(f"front-matter order must be zh abstract -> zh keyword -> en abstract -> en keyword -> TOC -> body, found {surface_order}")

    if zh_abs is not None:
        zh_abs_para = paragraphs[zh_abs - 1]
        text = paragraph_text(zh_abs_para).strip()
        if "：" not in text and ":" not in text:
            issues.append("Chinese abstract must keep label and content in one paragraph")
        if zh_key is not None:
            orphan_rows = nonempty_between(paragraphs, zh_abs, zh_key)
            if orphan_rows:
                issues.append(f"Chinese abstract body must be merged into the label paragraph, found orphan rows: {orphan_rows[:3]}")
        issues.extend(label_run_issues(zh_abs_para, ("\u6458  \u8981：", "\u6458\u8981："), "zh_abstract"))
        issues.extend(abstract_content_issues(zh_abs_para, "zh_abstract", english=False))
        issues.extend(frontmatter_metric_issues(zh_abs_para, "zh_abstract"))
    if en_abs is not None:
        en_abs_para = paragraphs[en_abs - 1]
        text = paragraph_text(en_abs_para).strip()
        if re.fullmatch(r"abstract", text, flags=re.IGNORECASE):
            issues.append("English abstract is a standalone title instead of `Abstract:` plus content")
        if en_key is not None:
            orphan_rows = nonempty_between(paragraphs, en_abs, en_key)
            if orphan_rows:
                issues.append(f"English abstract body must be merged into the label paragraph, found orphan rows: {orphan_rows[:3]}")
        issues.extend(label_run_issues(en_abs_para, ("Abstract:",), "en_abstract"))
        issues.extend(abstract_content_issues(en_abs_para, "en_abstract", english=True))
        issues.extend(frontmatter_metric_issues(en_abs_para, "en_abstract"))
    if zh_key is not None:
        issues.extend(label_run_issues(paragraphs[zh_key - 1], ("\u5173\u952e\u8bcd：", "\u5173\u952e\u8bcd:"), "zh_keyword"))
        issues.extend(frontmatter_metric_issues(paragraphs[zh_key - 1], "zh_keyword"))
    if en_key is not None:
        issues.extend(label_run_issues(paragraphs[en_key - 1], ("Key words:",), "en_keyword"))
        issues.extend(frontmatter_metric_issues(paragraphs[en_key - 1], "en_keyword"))

    surface_details = {
        "zh_abstract": surface_detail(paragraphs, zh_abs),
        "zh_keyword": surface_detail(paragraphs, zh_key),
        "en_abstract": surface_detail(paragraphs, en_abs),
        "en_keyword": surface_detail(paragraphs, en_key),
        "toc": surface_detail(paragraphs, toc),
        "first_body": surface_detail(paragraphs, first_body),
    }

    return {
        "schema": "graduation-project-builder.frontmatter-structure-audit.v1",
        "final_docx_path": str(final_docx),
        "final_docx_sha256": sha256_file(final_docx),
        "surface_order": surface_order,
        "surface_details": surface_details,
        "undefined_nonempty_style_count": len(undefined),
        "undefined_nonempty_styles": undefined,
        "issues": issues,
        "passed": not issues,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--final-docx", required=True)
    parser.add_argument("--report-json")
    args = parser.parse_args()
    payload = audit_frontmatter(Path(args.final_docx).resolve())
    if args.report_json:
        report = Path(args.report_json).resolve()
        report.parent.mkdir(parents=True, exist_ok=True)
        report.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if payload["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
