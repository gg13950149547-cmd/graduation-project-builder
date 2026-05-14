#!/usr/bin/env python3
"""Audit whether a thesis bibliography satisfies a paper-only requirement."""

from __future__ import annotations

import argparse
import json
import re
import sys
import zipfile
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable
import xml.etree.ElementTree as ET


NS = {
    "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
}
W = "{%s}" % NS["w"]

ACCEPT_TAGS = {"J", "C", "D"}
REJECT_TAGS = {"M", "EB/OL", "R", "R/OL"}
NON_PAPER_HINTS = (
    "documentation",
    "financial results",
    "report",
    "news",
    "show/",
    "docs.",
    "ir.",
)
TAIL_HEADINGS = {
    "致谢",
    "致 谢",
    "附录",
    "appendix",
    "acknowledgements",
    "acknowledgments",
}
BODY_EXCLUDE_EXACT = {
    "",
    "目录",
    "目 录",
    "摘要",
    "摘 要",
    "abstract",
    "参考文献",
}
PAPER_ONLY_ERROR_CODES = {
    "nonpaper": "PAPER_ONLY_NONPAPER_SOURCE",
    "unverified": "PAPER_ONLY_UNVERIFIED_ITEM",
    "body_depends": "BODY_DEPENDS_ON_REJECTED_SOURCE",
}


@dataclass
class ParagraphRecord:
    index: int
    para_id: str
    text: str
    style: str
    has_numbering: bool


@dataclass
class ReferenceEntry:
    number: int
    para_id: str
    paragraph_index: int
    text: str
    source_type: str
    accepted_under_paper_only: bool
    template_present: bool
    template_query_entry: str
    template_query_path_type: str
    body_citation_paragraphs: list[str]


@dataclass
class AuditResult:
    passed: bool
    error_codes: list[str]
    bibliography_total_count: int
    non_paper_count: int
    unverified_count: int
    body_dependency_count: int
    entries: list[ReferenceEntry]
    findings: list[str]


def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text or "").strip()


def paragraph_text(paragraph: ET.Element) -> str:
    return "".join((node.text or "") for node in paragraph.iterfind(".//w:t", NS))


def paragraph_style_id(paragraph: ET.Element) -> str:
    style = paragraph.find("./w:pPr/w:pStyle", NS)
    if style is None:
        return ""
    return style.attrib.get(f"{W}val", "")


def paragraph_has_numbering(paragraph: ET.Element) -> bool:
    return paragraph.find("./w:pPr/w:numPr", NS) is not None


def paragraph_id(paragraph: ET.Element) -> str:
    for key, value in paragraph.attrib.items():
        if key.endswith("paraId"):
            return value
    return ""


def iter_paragraphs(docx_path: Path) -> list[ParagraphRecord]:
    with zipfile.ZipFile(docx_path, "r") as zf:
        xml_bytes = zf.read("word/document.xml")
    root = ET.fromstring(xml_bytes)
    records: list[ParagraphRecord] = []
    for index, paragraph in enumerate(root.iterfind(".//w:body/w:p", NS)):
        records.append(
            ParagraphRecord(
                index=index,
                para_id=paragraph_id(paragraph),
                text=normalize_text(paragraph_text(paragraph)),
                style=paragraph_style_id(paragraph),
                has_numbering=paragraph_has_numbering(paragraph),
            )
        )
    return records


def looks_like_heading(text: str) -> bool:
    stripped = normalize_text(text)
    if not stripped:
        return False
    if stripped.lower() in TAIL_HEADINGS or stripped == "参考文献":
        return True
    if len(stripped) > 40:
        return False
    return bool(
        re.match(r"^(第[一二三四五六七八九十0-9]+章.*|[0-9]+(\.[0-9]+)?\S.*)$", stripped)
    )


def find_bibliography_range(paragraphs: list[ParagraphRecord]) -> tuple[int, int]:
    start = next((p.index for p in paragraphs if p.text == "参考文献"), -1)
    if start < 0:
        raise ValueError("Could not find bibliography heading '参考文献'.")

    end = len(paragraphs)
    for record in paragraphs[start + 1 :]:
        if record.text.lower() in TAIL_HEADINGS:
            end = record.index
            break
        if looks_like_heading(record.text) and not record.has_numbering:
            end = record.index
            break
    return start, end


def extract_bibliography_entries(paragraphs: list[ParagraphRecord]) -> list[ParagraphRecord]:
    start, end = find_bibliography_range(paragraphs)
    return [p for p in paragraphs[start + 1 : end] if p.text]


def extract_body_citations(paragraphs: Iterable[ParagraphRecord]) -> dict[int, list[str]]:
    citations: dict[int, list[str]] = {}
    for record in paragraphs:
        text = normalize_text(record.text)
        if text.lower() in BODY_EXCLUDE_EXACT:
            continue
        for match in re.findall(r"\[(\d+)\]", text):
            citations.setdefault(int(match), []).append(text)
    return citations


def detect_source_type(text: str) -> tuple[str, bool]:
    upper_text = text.upper()
    for tag in ACCEPT_TAGS:
        if f"[{tag}]" in upper_text:
            return "paper", True
    for tag in REJECT_TAGS:
        if f"[{tag}]" in upper_text:
            return "non-paper", False
    lowered = text.lower()
    if any(token in lowered for token in NON_PAPER_HINTS):
        return "non-paper", False
    return "unknown", False


def parse_review_template(template_path: Path) -> dict[int, dict[str, str]]:
    template = template_path.read_text(encoding="utf-8")
    item_pattern = re.compile(r"^### \[(\d+)\]\s*$", re.M)
    matches = list(item_pattern.finditer(template))
    result: dict[int, dict[str, str]] = {}

    for index, match in enumerate(matches):
        number = int(match.group(1))
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(template)
        block = template[start:end]
        fields: dict[str, str] = {}
        for line in block.splitlines():
            stripped = line.strip()
            if stripped.startswith("- ") and ":" in stripped:
                key, value = stripped[2:].split(":", 1)
                fields[key.strip().lower()] = value.strip()
        result[number] = fields
    return result


def audit_docx(docx_path: Path, review_template_path: Path) -> AuditResult:
    paragraphs = iter_paragraphs(docx_path)
    start, _ = find_bibliography_range(paragraphs)
    bibliography = extract_bibliography_entries(paragraphs)
    body_citations = extract_body_citations(paragraphs[:start])
    template_items = parse_review_template(review_template_path)

    entries: list[ReferenceEntry] = []
    findings: list[str] = []
    error_codes: set[str] = set()
    non_paper_count = 0
    unverified_count = 0
    body_dependency_count = 0

    for number, record in enumerate(bibliography, start=1):
        source_type, accepted = detect_source_type(record.text)
        template_fields = template_items.get(number, {})
        template_present = number in template_items
        query_entry = template_fields.get("query entry", "")
        query_path_type = template_fields.get("query path type", "")
        body_dependencies = body_citations.get(number, [])

        if not accepted:
            non_paper_count += 1
            error_codes.add(PAPER_ONLY_ERROR_CODES["nonpaper"])
            findings.append(
                f"[{number}] is not accepted under paper-only literature: {record.text}"
            )
        if not template_present or not query_entry:
            unverified_count += 1
            error_codes.add(PAPER_ONLY_ERROR_CODES["unverified"])
            findings.append(
                f"[{number}] is missing review-template verification evidence."
            )
        if not accepted and body_dependencies:
            body_dependency_count += len(body_dependencies)
            error_codes.add(PAPER_ONLY_ERROR_CODES["body_depends"])
            findings.append(
                f"Body still cites rejected bibliography item [{number}] in {len(body_dependencies)} paragraph(s)."
            )

        entries.append(
            ReferenceEntry(
                number=number,
                para_id=record.para_id,
                paragraph_index=record.index,
                text=record.text,
                source_type=source_type,
                accepted_under_paper_only=accepted,
                template_present=template_present,
                template_query_entry=query_entry,
                template_query_path_type=query_path_type,
                body_citation_paragraphs=body_dependencies,
            )
        )

    return AuditResult(
        passed=not error_codes,
        error_codes=sorted(error_codes),
        bibliography_total_count=len(entries),
        non_paper_count=non_paper_count,
        unverified_count=unverified_count,
        body_dependency_count=body_dependency_count,
        entries=entries,
        findings=findings,
    )


def render_markdown_report(result: AuditResult) -> str:
    lines = [
        "# Paper-Only Bibliography Audit Report",
        "",
        "## Summary",
        f"- verdict: {'PASS' if result.passed else 'FAIL'}",
        f"- bibliography total count: {result.bibliography_total_count}",
        f"- non-paper count: {result.non_paper_count}",
        f"- unverified count: {result.unverified_count}",
        f"- body dependency count: {result.body_dependency_count}",
        f"- error codes: {', '.join(result.error_codes) if result.error_codes else 'none'}",
        "",
        "## Findings",
    ]
    if result.findings:
        lines.extend(f"- {finding}" for finding in result.findings)
    else:
        lines.append("- none")

    lines.extend(["", "## Entries"])
    for entry in result.entries:
        lines.extend(
            [
                f"### [{entry.number}]",
                f"- text: {entry.text}",
                f"- source type: {entry.source_type}",
                f"- accepted under paper-only: {'yes' if entry.accepted_under_paper_only else 'no'}",
                f"- review template present: {'yes' if entry.template_present else 'no'}",
                f"- query path type: {entry.template_query_path_type or 'missing'}",
                f"- query entry: {entry.template_query_entry or 'missing'}",
                f"- body dependency paragraphs: {len(entry.body_citation_paragraphs)}",
            ]
        )
        if entry.body_citation_paragraphs:
            lines.append("- dependent body snippets:")
            lines.extend(f"  - {snippet}" for snippet in entry.body_citation_paragraphs)
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--docx", required=True, help="Target DOCX path")
    parser.add_argument("--review-template", required=True, help="Filled bibliography review template path")
    parser.add_argument("--report-out", required=True, help="Markdown report output path")
    parser.add_argument("--json", action="store_true", help="Emit structured JSON to stdout")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    result = audit_docx(Path(args.docx), Path(args.review_template))
    report = render_markdown_report(result)
    Path(args.report_out).write_text(report, encoding="utf-8")

    if args.json:
        print(
            json.dumps(
                {
                    "passed": result.passed,
                    "error_codes": result.error_codes,
                    "bibliography_total_count": result.bibliography_total_count,
                    "non_paper_count": result.non_paper_count,
                    "unverified_count": result.unverified_count,
                    "body_dependency_count": result.body_dependency_count,
                    "findings": result.findings,
                    "entries": [asdict(entry) for entry in result.entries],
                },
                ensure_ascii=False,
                indent=2,
            )
        )
    else:
        print(f"Paper-only bibliography audit: {'PASS' if result.passed else 'FAIL'}")
        print(f"- bibliography total count: {result.bibliography_total_count}")
        print(f"- non-paper count: {result.non_paper_count}")
        print(f"- unverified count: {result.unverified_count}")
        print(f"- body dependency count: {result.body_dependency_count}")
        print(f"- report: {args.report_out}")
        if result.error_codes:
            print(f"- error codes: {', '.join(result.error_codes)}")
    return 0 if result.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
