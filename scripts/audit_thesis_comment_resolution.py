#!/usr/bin/env python3
"""Audit teacher/user comment resolution against a DOCX and a resolution ledger."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import zipfile
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any
from xml.etree import ElementTree as ET


NS_W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
NS_W14 = "http://schemas.microsoft.com/office/word/2010/wordml"
NS_W15 = "http://schemas.microsoft.com/office/word/2012/wordml"
W = f"{{{NS_W}}}"
W14 = f"{{{NS_W14}}}"
W15 = f"{{{NS_W15}}}"

SCHEMA = "graduation-project-builder.comment-resolution-ledger.v1"
STATUS_FIXED = {"fixed", "pass", "passed", "resolved", "done", "implemented"}
STATUS_OPEN = {"open", "partial", "blocked", "failed", "unresolved", "unknown", "pending", "orphan"}
STATUS_DISPOSED = {"removed-user-approved", "disposed-user-approved", "not-applicable-user-approved"}
AUTH_TRUE = {"true", "yes", "pass", "passed", "authorized", "explicitly-authorized"}
APPROVAL_TRUE = AUTH_TRUE | {"user-approved", "explicit-user-approved", "approved-by-user"}
ALL_RESOLVED_TOKENS = {
    "all-comments-resolved",
    "all comments resolved",
    "comments resolved",
    "verified comments resolved",
    "批注已改完",
    "批注全部解决",
    "所有批注已解决",
    "批注解决",
}
FIGURE_TOKENS = {
    "figure",
    "image",
    "picture",
    "screenshot",
    "diagram",
    "flowchart",
    "er",
    "model",
    "network",
    "\u56fe",
    "\u56fe片",
    "\u622a图",
    "\u6a21型",
    "\u7ed3构",
    "\u6d41程图",
    "\u5b9e体",
}
NON_SIZE_FIGURE_TOKENS = {
    "crop",
    "recrop",
    "source",
    "redraw",
    "replace",
    "model",
    "network",
    "structure",
    "caption",
    "explain",
    "provenance",
    "readability",
    "content",
    "reference",
    "bibliography",
    "\u88c1剪",
    "\u91cd绘",
    "\u66ff换",
    "\u6765源",
    "\u6a21型",
    "\u7ed3构",
    "\u8bf4明",
    "\u53c2考文献",
    "\u6e05晰",
    "\u5185容",
}
SIZE_ONLY_TOKENS = {"size", "resize", "scale", "width", "height", "large", "small", "\u5c3a寸", "\u7f29放"}

SAME_AS_ABOVE_TOKENS = {
    "sameasabove",
    "ditto",
    "\u540c\u4e0a",
    "\u540c\u4e0a\u8ff0\u56fe\u7247\u95ee\u9898",
    "\u540c\u4e0a\u8ff0\u56fe\u7247\u7c7b\u4f3c\u95ee\u9898",
}

COMMENT_INTENT_REQUIREMENTS: dict[str, dict[str, Any]] = {
    "network_model_structure_figure": {
        "required_any": (
            "network_model_structure",
            "model_structure_figure",
            "model-structure-figure",
            "inserted_figure",
            "figure_manifest",
        ),
        "description": "network/model structure figure",
    },
    "figure_size": {
        "required_any": (
            "figure_extents",
            "display_extent",
            "image_size",
            "oversized_count",
            "figure-size",
        ),
        "description": "figure size/display extent",
    },
    "figure_explanation": {
        "required_any": (
            "figure_explanation",
            "adjacent_explanation",
            "figure_content_explanation",
            "image_content_explanation",
            "caption_adjacent_explanation",
        ),
        "description": "figure/image content explanation",
    },
    "screenshot_crop": {
        "required_any": (
            "screenshot_crop",
            "crop_verdict",
            "cropped",
            "recrop",
            "bottom_crop",
            "unneeded_bottom_removed",
        ),
        "description": "screenshot crop/irrelevant-area removal",
    },
    "risk_weight_rationale": {
        "required_any": (
            "weight_rationale",
            "risk_weight",
            "risk_weight_explanation",
            "0.15",
            "0.30",
        ),
        "description": "risk-weight rationale",
    },
    "table_vertical_borders": {
        "required_any": (
            "table_vertical_borders",
            "vertical_border",
            "vertical_borders_removed",
            "no_vertical_borders",
            "er_connector_cleanup",
        ),
        "description": "table vertical-border cleanup",
    },
    "reference_count_year": {
        "required_all": (
            "reference_count",
            "english_reference_count",
            "contains_2026_reference_count",
        ),
        "description": "reference count, English-reference count, and 2026-year exclusion",
    },
}


@dataclass
class CommentRecord:
    comment_id: str
    text: str
    text_digest: str
    done: bool
    has_anchor: bool
    anchor_count: int
    para_id: str


@dataclass
class CommentSnapshot:
    docx_path: str
    docx_sha256: str
    comments: list[CommentRecord]
    anchor_ids: list[str]
    comment_count: int
    done_count: int
    open_count: int


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def normalize(value: object) -> str:
    return " ".join(str(value or "").strip().lower().split())


def text_digest(text: str) -> str:
    return hashlib.sha256(" ".join(text.split()).encode("utf-8")).hexdigest()


def read_zip_xml(zf: zipfile.ZipFile, name: str) -> ET.Element | None:
    if name not in zf.namelist():
        return None
    return ET.fromstring(zf.read(name))


def story_part_names(zf: zipfile.ZipFile) -> list[str]:
    names: list[str] = []
    for name in zf.namelist():
        if not name.startswith("word/") or not name.endswith(".xml"):
            continue
        if name == "word/document.xml" or re.match(r"word/(header|footer)\d+\.xml$", name):
            names.append(name)
        elif name in {"word/footnotes.xml", "word/endnotes.xml", "word/comments.xml"}:
            names.append(name)
    return sorted(names)


def collect_comment_snapshot(docx_path: Path) -> CommentSnapshot:
    with zipfile.ZipFile(docx_path, "r") as zf:
        comments_root = read_zip_xml(zf, "word/comments.xml")
        comments_ext_root = read_zip_xml(zf, "word/commentsExtended.xml")

        done_by_para_id: dict[str, bool] = {}
        if comments_ext_root is not None:
            for item in comments_ext_root.iter():
                para_id = item.attrib.get(f"{W15}paraId") or item.attrib.get("paraId") or ""
                if not para_id:
                    continue
                done_value = item.attrib.get(f"{W15}done") or item.attrib.get("done") or ""
                done_by_para_id[para_id] = done_value in {"1", "true", "True"}

        anchors: list[str] = []
        anchor_counts: dict[str, int] = {}
        for part_name in story_part_names(zf):
            root = read_zip_xml(zf, part_name)
            if root is None:
                continue
            for element in root.iter():
                if element.tag in {f"{W}commentRangeStart", f"{W}commentRangeEnd", f"{W}commentReference"}:
                    comment_id = element.attrib.get(f"{W}id", "")
                    if comment_id:
                        anchors.append(f"{part_name}:{comment_id}")
                        anchor_counts[comment_id] = anchor_counts.get(comment_id, 0) + 1

        records: list[CommentRecord] = []
        if comments_root is not None:
            for comment in comments_root.findall(f"{W}comment"):
                comment_id = comment.attrib.get(f"{W}id", "")
                para_id = ""
                first_para = comment.find(f"{W}p")
                if first_para is not None:
                    para_id = (
                        first_para.attrib.get(f"{W15}paraId")
                        or first_para.attrib.get(f"{W14}paraId")
                        or first_para.attrib.get("paraId")
                        or ""
                    )
                text = " ".join("".join(comment.itertext()).split())
                done = done_by_para_id.get(para_id, False)
                records.append(
                    CommentRecord(
                        comment_id=comment_id,
                        text=text,
                        text_digest=text_digest(text),
                        done=done,
                        has_anchor=anchor_counts.get(comment_id, 0) > 0,
                        anchor_count=anchor_counts.get(comment_id, 0),
                        para_id=para_id,
                    )
                )

    done_count = sum(1 for item in records if item.done)
    return CommentSnapshot(
        docx_path=str(docx_path),
        docx_sha256=sha256_file(docx_path),
        comments=records,
        anchor_ids=sorted(set(anchors)),
        comment_count=len(records),
        done_count=done_count,
        open_count=len(records) - done_count,
    )


def resolve_path(value: object, base: Path) -> Path | None:
    text = str(value or "").strip()
    if not text or normalize(text) in {"none", "n/a", "not-applicable", "missing"}:
        return None
    path = Path(text)
    if not path.is_absolute():
        path = (base.parent / path).resolve()
    return path


def flatten_json_scalars(value: object) -> list[str]:
    if isinstance(value, dict):
        values: list[str] = []
        for key, item in value.items():
            values.append(str(key))
            values.extend(flatten_json_scalars(item))
        return values
    if isinstance(value, list):
        values = []
        for item in value:
            values.extend(flatten_json_scalars(item))
        return values
    return [str(value)]


def detector_report_text(path: Path) -> str:
    raw = path.read_text(encoding="utf-8", errors="ignore")
    try:
        payload = json.loads(raw)
    except Exception:
        return raw
    return raw + "\n" + "\n".join(flatten_json_scalars(payload))


def detector_report_json_issues(path: Path) -> list[str]:
    """JSON detector artifacts must be machine-readable, not pass-shaped text."""
    if path.suffix.lower() != ".json":
        return []
    raw = path.read_text(encoding="utf-8", errors="ignore")
    try:
        payload = json.loads(raw)
    except Exception as exc:
        return [f"detector report JSON is unreadable: {path} ({exc})"]
    if not isinstance(payload, (dict, list)):
        return [f"detector report JSON root must be an object or list: {path}"]
    return []


def detector_report_has_pass_verdict(text: str) -> bool:
    lowered = text.lower()
    return (
        re.search(r"\b(result|verdict|status)[\"']?\s*[:=]\s*[\"']?pass(?:ed)?\b", lowered) is not None
        or '"passed": true' in lowered
        or "'passed': true" in lowered
        or "passed true" in lowered
    )


def load_ledger(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("comment resolution ledger JSON root must be an object")
    return payload


def ledger_entries(payload: dict[str, Any]) -> list[dict[str, Any]]:
    for key in ("comments", "comment_records", "issues", "records"):
        value = payload.get(key)
        if isinstance(value, list):
            return [item for item in value if isinstance(item, dict)]
        if isinstance(value, dict):
            return [item for item in value.values() if isinstance(item, dict)]
    return []


def entry_id(entry: dict[str, Any]) -> str:
    return str(entry.get("comment_id") or entry.get("id") or entry.get("source_comment_id") or "").strip()


def entry_status(entry: dict[str, Any]) -> str:
    return normalize(entry.get("status") or entry.get("final_status") or entry.get("verdict"))


def entry_text(entry: dict[str, Any]) -> str:
    return json.dumps(entry, ensure_ascii=False).lower()


def entry_done_authorized(entry: dict[str, Any]) -> bool:
    for key in ("done_state_authorized", "done_state_authorization", "comment_done_authorized"):
        if normalize(entry.get(key)) in AUTH_TRUE:
            return True
    return False


def entry_disposal_authorized(entry: dict[str, Any], ledger_path: Path) -> bool:
    for key in (
        "explicit_user_approval",
        "disposal_user_approval",
        "comment_disposal_user_approval",
        "comment_removal_user_approval",
    ):
        if normalize(entry.get(key)) in APPROVAL_TRUE:
            return True
    for key in ("approval_evidence_path", "disposal_approval_evidence_path", "user_approval_evidence_path"):
        for raw_path in as_path_list(entry.get(key)):
            resolved = resolve_path(raw_path, ledger_path)
            if resolved is not None and resolved.exists() and (not resolved.is_file() or resolved.stat().st_size > 0):
                return True
    return False


def entry_anchor_restoration_authorized(entry: dict[str, Any], ledger_path: Path) -> bool:
    for key in (
        "anchor_restoration_authorized",
        "comment_anchor_restoration_authorized",
        "orphan_comment_anchor_restoration_authorized",
    ):
        if normalize(entry.get(key)) in AUTH_TRUE:
            break
    else:
        return False
    for key in (
        "anchor_restoration_evidence_path",
        "comment_anchor_restoration_evidence_path",
        "original_anchor_evidence_path",
    ):
        for raw_path in as_path_list(entry.get(key)):
            resolved = resolve_path(raw_path, ledger_path)
            if resolved is not None and resolved.exists() and (not resolved.is_file() or resolved.stat().st_size > 0):
                return True
    return False


def as_path_list(value: object) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    if isinstance(value, tuple):
        return [str(item).strip() for item in value if str(item).strip()]
    text = str(value).strip()
    if not text or normalize(text) in {"none", "n/a", "not-applicable"}:
        return []
    parts: list[str] = []
    for separator in (";", ",", "\n"):
        if separator in text:
            parts = [item.strip() for item in text.split(separator)]
            break
    return [item for item in (parts or [text]) if item]


def entry_evidence_paths(entry: dict[str, Any]) -> list[str]:
    paths: list[str] = []
    for key in ("evidence_paths", "evidence_path", "rendered_evidence_paths", "detector_evidence_paths"):
        paths.extend(as_path_list(entry.get(key)))
    return paths


def entry_detector_report_path(entry: dict[str, Any]) -> str:
    binding = entry.get("detector_binding")
    if not isinstance(binding, dict):
        binding = {}
    return str(
        entry.get("detector_report")
        or entry.get("detector_report_path")
        or binding.get("detector_report")
        or binding.get("detector_report_path")
        or ""
    ).strip()


def has_all_comments_claim(*values: object) -> bool:
    text = " ".join(str(value or "") for value in values).lower()
    return any(token.lower() in text for token in ALL_RESOLVED_TOKENS)


def is_fixed(entry: dict[str, Any]) -> bool:
    return entry_status(entry) in STATUS_FIXED


def fixed_entry_detector_binding_issues(
    comment_id: str,
    entry: dict[str, Any],
    ledger_path: Path | None,
    *,
    final_docx: Path,
    source_docx: Path | None = None,
) -> list[str]:
    binding = entry.get("detector_binding")
    if not isinstance(binding, dict):
        binding = {}
    fields = {
        "surface": entry.get("surface") or binding.get("surface"),
        "subissue": entry.get("subissue") or binding.get("subissue"),
        "detector_id": entry.get("detector_id") or binding.get("detector_id"),
        "detector_report": (
            entry.get("detector_report")
            or entry.get("detector_report_path")
            or binding.get("detector_report")
            or binding.get("detector_report_path")
        ),
        "verdict": entry.get("verdict") or entry.get("detector_verdict") or binding.get("verdict") or binding.get("detector_verdict"),
    }
    issues: list[str] = []
    for key, value in fields.items():
        if not str(value or "").strip():
            issues.append(f"comment id {comment_id} fixed ledger row lacks detector binding field `{key}`")
    verdict = str(fields.get("verdict") or "").strip().lower()
    if verdict and not verdict.startswith("pass"):
        issues.append(f"comment id {comment_id} fixed detector verdict is not pass: {fields.get('verdict')}")
    detector_report = str(fields.get("detector_report") or "").strip()
    if detector_report:
        resolved = resolve_path(detector_report, ledger_path)
        if resolved is None or not resolved.exists() or (resolved.is_file() and resolved.stat().st_size == 0):
            issues.append(f"comment id {comment_id} detector report is missing or empty: {detector_report}")
        elif resolved.is_file():
            issues.extend(
                f"comment id {comment_id} {issue}"
                for issue in detector_report_json_issues(resolved)
            )
            report_text = detector_report_text(resolved)
            report_text_lower = report_text.lower()
            detector_id = str(fields.get("detector_id") or "").strip()
            if detector_id and detector_id.lower() not in report_text_lower:
                issues.append(f"comment id {comment_id} detector report does not contain detector id `{detector_id}`")
            if sha256_file(final_docx).lower() not in report_text_lower:
                issues.append(f"comment id {comment_id} detector report is not bound to the final DOCX SHA256")
            if source_docx is not None and source_docx.exists() and sha256_file(source_docx).lower() not in report_text_lower:
                issues.append(f"comment id {comment_id} detector report is not bound to the source DOCX SHA256")
            if not detector_report_has_pass_verdict(report_text):
                issues.append(f"comment id {comment_id} detector report does not contain a machine-readable pass verdict")
    return issues


def is_disposed(entry: dict[str, Any]) -> bool:
    return entry_status(entry) in STATUS_DISPOSED


def comment_has_token(text: str, tokens: set[str]) -> bool:
    lowered = text.lower()
    return any(token.lower() in lowered for token in tokens)


def compact_for_intent(text: str) -> str:
    return re.sub(r"\s+", "", str(text or "")).lower()


def comment_is_same_as_above(text: str) -> bool:
    compact = compact_for_intent(text)
    if compact in SAME_AS_ABOVE_TOKENS:
        return True
    return compact.startswith("\u540c\u4e0a\u8ff0")


def classify_comment_intents(text: str) -> list[str]:
    lowered = str(text or "").lower()
    compact = compact_for_intent(text)
    intents: list[str] = []

    def has_any(tokens: tuple[str, ...]) -> bool:
        return any(token.lower() in lowered or compact_for_intent(token) in compact for token in tokens)

    if has_any(("network model structure", "model structure", "\u7f51\u7edc\u6a21\u578b\u7ed3\u6784", "\u7ed3\u6784\u56fe")):
        intents.append("network_model_structure_figure")
    if has_any(("figure", "image", "picture", "screenshot", "\u56fe", "\u56fe\u7247", "\u622a\u56fe")) and has_any(
        ("too large", "large", "resize", "scale", "\u7f29\u5c0f", "\u592a\u5927", "\u5c3a\u5bf8")
    ):
        intents.append("figure_size")
    if has_any(("figure", "image", "picture", "\u56fe", "\u56fe\u7247")) and has_any(
        ("explain", "content", "what content", "\u5185\u5bb9", "\u8bf4\u660e", "\u89e3\u91ca")
    ):
        intents.append("figure_explanation")
    if has_any(("screenshot", "crop", "recrop", "\u622a\u56fe", "\u88c1\u526a", "\u622a\u4e0a", "\u4e0b\u65b9\u6ca1\u6709\u7528")):
        intents.append("screenshot_crop")
    if has_any(("weight", "risk weight", "\u6743\u91cd", "\u539f\u56e0")) and "\u6743\u91cd" in lowered:
        intents.append("risk_weight_rationale")
    if has_any(("vertical line", "vertical border", "\u7ad6\u7ebf", "\u8fde\u63a5\u7ad6\u7ebf")):
        intents.append("table_vertical_borders")
    if has_any(("reference", "bibliography", "\u53c2\u8003\u6587\u732e")) and (
        "25" in lowered or "2026" in lowered or has_any(("english", "\u82f1\u6587"))
    ):
        intents.append("reference_count_year")

    return list(dict.fromkeys(intents))


def intent_binding_issues(
    comment_id: str,
    intents: list[str],
    *,
    entry: dict[str, Any],
    report_text: str,
) -> list[str]:
    if not intents:
        return []
    combined = (entry_text(entry) + "\n" + report_text).lower()
    issues: list[str] = []
    for intent in intents:
        requirement = COMMENT_INTENT_REQUIREMENTS.get(intent, {})
        required_any = [str(item).lower() for item in requirement.get("required_any", ())]
        required_all = [str(item).lower() for item in requirement.get("required_all", ())]
        description = str(requirement.get("description") or intent)
        if required_any and not any(token in combined for token in required_any):
            issues.append(
                f"comment id {comment_id} intent `{intent}` lacks detector evidence for {description}"
            )
        missing_all = [token for token in required_all if token not in combined]
        if missing_all:
            issues.append(
                f"comment id {comment_id} intent `{intent}` lacks detector evidence fields: {missing_all}"
            )
    return issues


def validate_comment_resolution_ledger(
    ledger_path: Path | None,
    *,
    final_docx: Path,
    source_docx: Path | None = None,
    assert_all_resolved: bool = False,
) -> list[str]:
    issues: list[str] = []
    final_snapshot = collect_comment_snapshot(final_docx)
    source_snapshot = collect_comment_snapshot(source_docx) if source_docx is not None and source_docx.exists() else None

    if assert_all_resolved and source_docx is None:
        issues.append("source DOCX is required for an all-comments-resolved claim")
    if assert_all_resolved and source_docx is not None and not source_docx.exists():
        issues.append("source DOCX must exist for an all-comments-resolved claim")
    if assert_all_resolved and final_snapshot.open_count:
        issues.append(
            "all-comments-resolved claim requires final DOCX open comment count to be zero "
            f"(open_count={final_snapshot.open_count})"
        )
    if source_docx is not None:
        try:
            if source_docx.resolve() == final_docx.resolve():
                issues.append("source and final DOCX paths must differ for comment-resolution audit")
        except OSError:
            pass

    if ledger_path is None:
        if assert_all_resolved:
            issues.append("comment-resolution ledger path is missing for an all-comments-resolved claim")
        if final_snapshot.done_count:
            issues.append("final DOCX has done comments but no comment-resolution ledger authorizes done state")
        if source_snapshot is not None:
            for source_comment in source_snapshot.comments:
                final_comment = next(
                    (item for item in final_snapshot.comments if item.comment_id == source_comment.comment_id),
                    None,
                )
                if final_comment is None:
                    issues.append(f"source comment id {source_comment.comment_id} is missing from final DOCX without approved disposal")
                    continue
                if source_comment.text_digest != final_comment.text_digest:
                    issues.append(f"comment id {source_comment.comment_id} text changed without preserving the teacher comment text")
                if source_comment.anchor_count != final_comment.anchor_count:
                    issues.append(
                        f"comment id {source_comment.comment_id} anchor count changed "
                        f"(source={source_comment.anchor_count}, final={final_comment.anchor_count})"
                    )
                if source_comment.has_anchor and not final_comment.has_anchor:
                    issues.append(f"comment id {source_comment.comment_id} lost all final DOCX anchors")
                if source_comment.done != final_comment.done:
                    issues.append(f"comment id {source_comment.comment_id} done state changed without a ledger row")
        return issues
    if not ledger_path.exists():
        return [f"comment-resolution ledger path does not exist: {ledger_path}"]

    try:
        payload = load_ledger(ledger_path)
    except Exception as exc:
        return [f"comment-resolution ledger is unreadable: {ledger_path} ({exc})"]

    claim_all = assert_all_resolved or has_all_comments_claim(
        payload.get("claim_scope"),
        payload.get("resolution_scope"),
        payload.get("handoff_claim"),
        payload.get("summary"),
    )
    if claim_all and not assert_all_resolved and final_snapshot.open_count:
        issues.append(
            "all-comments-resolved claim requires final DOCX open comment count to be zero "
            f"(open_count={final_snapshot.open_count})"
        )
    if payload.get("schema") != SCHEMA:
        issues.append(f"comment-resolution ledger schema must be {SCHEMA}")
    if claim_all:
        if source_docx is None:
            issues.append("source DOCX is required for an all-comments-resolved claim")
        elif not source_docx.exists():
            issues.append("source DOCX must exist for an all-comments-resolved claim")
        else:
            try:
                if source_docx.resolve() == final_docx.resolve():
                    issues.append("source and final DOCX paths must differ for comment-resolution audit")
            except OSError:
                issues.append("source DOCX path cannot be resolved for comment-resolution audit")

    final_docx_value = payload.get("final_docx_path")
    final_sha_value = str(payload.get("final_docx_sha256") or "").strip().lower()
    resolved_final = resolve_path(final_docx_value, ledger_path)
    if resolved_final is None:
        issues.append("comment-resolution ledger final_docx_path is missing")
    else:
        try:
            if resolved_final.resolve() != final_docx.resolve():
                issues.append("comment-resolution ledger final_docx_path does not match final DOCX")
        except OSError:
            issues.append("comment-resolution ledger final_docx_path cannot be resolved")
    if final_sha_value != sha256_file(final_docx).lower():
        issues.append("comment-resolution ledger final_docx_sha256 does not match final DOCX")

    if source_docx is not None:
        source_docx_value = payload.get("source_docx_path")
        source_sha_value = str(payload.get("source_docx_sha256") or "").strip().lower()
        resolved_source = resolve_path(source_docx_value, ledger_path)
        if resolved_source is None:
            issues.append("comment-resolution ledger source_docx_path is missing")
        else:
            try:
                if resolved_source.resolve() != source_docx.resolve():
                    issues.append("comment-resolution ledger source_docx_path does not match source DOCX")
            except OSError:
                issues.append("comment-resolution ledger source_docx_path cannot be resolved")
        if source_sha_value != sha256_file(source_docx).lower():
            issues.append("comment-resolution ledger source_docx_sha256 does not match source DOCX")

    entries = ledger_entries(payload)
    by_id = {entry_id(entry): entry for entry in entries if entry_id(entry)}
    if not entries:
        issues.append("comment-resolution ledger has no comment rows")

    final_ids = {item.comment_id for item in final_snapshot.comments}
    source_ids = {item.comment_id for item in source_snapshot.comments} if source_snapshot else set()

    if claim_all:
        missing_rows = sorted(final_ids - set(by_id))
        if missing_rows:
            issues.append(f"all-comments-resolved claim lacks ledger rows for comment ids: {missing_rows}")

    unresolved_ids: list[str] = []
    previous_comment_intents: list[str] = []
    for comment in final_snapshot.comments:
        comment_intents = classify_comment_intents(comment.text)
        if comment_intents:
            previous_comment_intents = comment_intents
        elif comment_is_same_as_above(comment.text):
            comment_intents = list(previous_comment_intents)
        entry = by_id.get(comment.comment_id)
        if entry is None:
            if claim_all or comment.done:
                issues.append(f"comment id {comment.comment_id} lacks a ledger row")
            if not comment.done:
                unresolved_ids.append(comment.comment_id)
            continue
        status = entry_status(entry)
        if claim_all and status not in STATUS_FIXED and status not in STATUS_DISPOSED:
            unresolved_ids.append(comment.comment_id)
        if comment.done and not is_fixed(entry):
            issues.append(f"comment id {comment.comment_id} is done in final DOCX but ledger status is not fixed")
        if comment.done and not entry_done_authorized(entry):
            issues.append(f"comment id {comment.comment_id} is done in final DOCX but done_state_authorized is missing")
        if is_fixed(entry):
            evidence_paths = entry_evidence_paths(entry)
            if not evidence_paths:
                issues.append(f"comment id {comment.comment_id} is fixed but has no evidence path")
            for raw_path in evidence_paths:
                resolved = resolve_path(raw_path, ledger_path)
                if resolved is None or not resolved.exists() or (resolved.is_file() and resolved.stat().st_size == 0):
                    issues.append(f"comment id {comment.comment_id} evidence path is missing or empty: {raw_path}")
            issues.extend(
                fixed_entry_detector_binding_issues(
                    comment.comment_id,
                    entry,
                    ledger_path,
                    final_docx=final_docx,
                    source_docx=source_docx,
                )
            )
            detector_report = entry_detector_report_path(entry)
            detector_text = ""
            if detector_report:
                resolved_detector = resolve_path(detector_report, ledger_path)
                if resolved_detector is not None and resolved_detector.exists() and resolved_detector.is_file():
                    detector_text = detector_report_text(resolved_detector)
            issues.extend(
                intent_binding_issues(
                    comment.comment_id,
                    comment_intents,
                    entry=entry,
                    report_text=detector_text,
                )
            )
        if comment_has_token(comment.text, FIGURE_TOKENS) and comment_has_token(comment.text, NON_SIZE_FIGURE_TOKENS):
            entry_payload = entry_text(entry)
            mentions_non_size = any(token.lower() in entry_payload for token in NON_SIZE_FIGURE_TOKENS)
            mentions_size = any(token.lower() in entry_payload for token in SIZE_ONLY_TOKENS)
            if is_fixed(entry) and mentions_size and not mentions_non_size:
                issues.append(
                    f"comment id {comment.comment_id} is a figure/content comment but ledger closes it with size-only evidence"
                )

    if unresolved_ids and claim_all:
        issues.append(f"all-comments-resolved claim still has unresolved comment ids: {sorted(set(unresolved_ids))}")

    if source_snapshot is not None:
        for source_comment in source_snapshot.comments:
            final_comment = next(
                (item for item in final_snapshot.comments if item.comment_id == source_comment.comment_id),
                None,
            )
            entry = by_id.get(source_comment.comment_id)
            if final_comment is None:
                if entry is None or not is_disposed(entry):
                    issues.append(f"source comment id {source_comment.comment_id} is missing from final DOCX without approved disposal")
                elif not entry_disposal_authorized(entry, ledger_path):
                    issues.append(f"source comment id {source_comment.comment_id} disposal lacks explicit user approval evidence")
                continue
            if source_comment.text_digest != final_comment.text_digest:
                issues.append(f"comment id {source_comment.comment_id} text changed without preserving the teacher comment text")
            if source_comment.anchor_count != final_comment.anchor_count:
                anchor_restored = (
                    not source_comment.has_anchor
                    and final_comment.has_anchor
                    and entry is not None
                    and entry_anchor_restoration_authorized(entry, ledger_path)
                )
                if not anchor_restored:
                    issues.append(
                        f"comment id {source_comment.comment_id} anchor count changed "
                        f"(source={source_comment.anchor_count}, final={final_comment.anchor_count})"
                    )
            if source_comment.has_anchor and not final_comment.has_anchor:
                issues.append(f"comment id {source_comment.comment_id} lost all final DOCX anchors")
            if source_comment.done != final_comment.done:
                if entry is None:
                    issues.append(f"comment id {source_comment.comment_id} done state changed without a ledger row")
                elif not entry_done_authorized(entry):
                    issues.append(f"comment id {source_comment.comment_id} done state changed without authorization")
                elif final_comment.done and not is_fixed(entry):
                    issues.append(f"comment id {source_comment.comment_id} was marked done but ledger status is not fixed")

    return issues


def build_report(
    final_snapshot: CommentSnapshot,
    issues: list[str],
    *,
    source_snapshot: CommentSnapshot | None = None,
    ledger_path: Path | None = None,
) -> str:
    lines = [
        "# Thesis Comment Resolution Audit",
        "",
        "## Summary",
        f"- final docx path: {final_snapshot.docx_path}",
        f"- final docx sha256: {final_snapshot.docx_sha256}",
        f"- final comment count: {final_snapshot.comment_count}",
        f"- final done count: {final_snapshot.done_count}",
        f"- final open count: {final_snapshot.open_count}",
        f"- ledger path: {ledger_path if ledger_path is not None else 'none'}",
        f"- result: {'pass' if not issues else 'fail'}",
    ]
    if source_snapshot is not None:
        lines.extend(
            [
                f"- source docx path: {source_snapshot.docx_path}",
                f"- source docx sha256: {source_snapshot.docx_sha256}",
                f"- source comment count: {source_snapshot.comment_count}",
                f"- source done count: {source_snapshot.done_count}",
            ]
        )
    lines.extend(["", "## Findings"])
    lines.extend([f"- {issue}" for issue in issues] if issues else ["- none"])
    lines.extend(["", "## Final Comments"])
    if final_snapshot.comments:
        for comment in final_snapshot.comments:
            snippet = comment.text[:120]
            lines.append(
                f"- id={comment.comment_id} done={'yes' if comment.done else 'no'} "
                f"anchors={comment.anchor_count} text={snippet}"
            )
    else:
        lines.append("- none")
    return "\n".join(lines) + "\n"


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--final-docx", required=True)
    parser.add_argument("--source-docx")
    parser.add_argument("--ledger")
    parser.add_argument("--assert-all-resolved", action="store_true")
    parser.add_argument("--report-output")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--json-output")
    args = parser.parse_args(argv)

    final_docx = Path(args.final_docx).resolve()
    source_docx = Path(args.source_docx).resolve() if args.source_docx else None
    ledger_path = Path(args.ledger).resolve() if args.ledger else None

    issues = validate_comment_resolution_ledger(
        ledger_path,
        final_docx=final_docx,
        source_docx=source_docx,
        assert_all_resolved=args.assert_all_resolved,
    )
    final_snapshot = collect_comment_snapshot(final_docx)
    source_snapshot = collect_comment_snapshot(source_docx) if source_docx is not None and source_docx.exists() else None
    report = build_report(final_snapshot, issues, source_snapshot=source_snapshot, ledger_path=ledger_path)
    payload = {
        "schema": "graduation-project-builder.comment-resolution-audit.v1",
        "final": asdict(final_snapshot),
        "source": asdict(source_snapshot) if source_snapshot is not None else None,
        "ledger_path": str(ledger_path) if ledger_path is not None else None,
        "assert_all_resolved": args.assert_all_resolved,
        "issues": issues,
        "passed": not issues,
    }

    if args.report_output:
        report_path = Path(args.report_output).resolve()
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(report, encoding="utf-8")
    if args.json_output:
        json_path = Path(args.json_output).resolve()
        json_path.parent.mkdir(parents=True, exist_ok=True)
        json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(report)
    return 0 if not issues else 1


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass
    raise SystemExit(main(sys.argv[1:]))
