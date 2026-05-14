#!/usr/bin/env python3
"""Check active skill text files for UTF-8 decoding, BOM, and mojibake patterns."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


TEXT_EXTENSIONS = {".cmd", ".json", ".md", ".ps1", ".py", ".txt", ".yaml", ".yml"}
SUSPICIOUS_TOKEN_ESCAPES = (
    "\\ufffd",
    "\\u95b8?",
    "\\u941e?",
    "\\u95c2?",
    "\\u7f02?",
    "\\u951f\\u65a4\\u62f7",
    "\\u95bc?",
    "\\u95b8\\u6b0f\\u503d\\u9227\\ue100\\u556f\\u93cb\\u51ae\\u60ae?",
    "\\u7f02\\u4f79\\u633b\\u5a3c\\ue0a4\\u62e0?",
    "\\u93cd\\u56ec\\ue57d",
    "\\u7f01\\ue161\\u3003",
    "\\u9365?-",
    "\\u93bd\\u6a3f\\ue6e6\\u951b\\u6b5a",
    "\\u934f\\u62bd\\u656d\\u7487\\u5d8f\\u7d30",
    "nearby\\u59dd\\uff46\\u6783",
    "\\u7039\\u5b29\\u7d8b",
    "\\u699b\\u621c\\u7d8b",
    "\\u95b8\\u5fcb\\u528d\\u93cb\\u51ae\\u5f3d\\u9413\\u5ea3\\u7840",
    "\\u95bb?   \\u745c\\u7248\\u69eb",
    "\\u6924\\u572d\\u6d30",
    "\\u9369\\u8f70\\u7c2c",
    "\\u93c8\\u54c4\\u6ad2",
    "\\u7459\\u55da",
    "\\u59e3\\u66da\\u7b1f",
    "\\u7481\\u6350",
    "\\u93b8\\u590b\\u5270",
    "\\u5a34\\u72c5\\u7d7f\\u9416?1",
    "\\u599e\\u3087\\u6578\\u5a40\\u4f79\\u3044\\u6d63\\u51a8\\u58d6",
    "\\u9420\\u56e5\\u5131\\u5a34\\u6a3c\\u4ee6\\u93c7\\u72ae\\u4edb",
    "\\u93b8\\u56e7\\u56ad",
    "\\u741b\\u3126\\u69d1",
    "\\u9352\\u766725",
)
SUSPICIOUS_TOKENS = [
    token.encode("ascii").decode("unicode_escape")
    for token in SUSPICIOUS_TOKEN_ESCAPES
] + ["?" * 4]


def is_active_text_file(skill_root: Path, path: Path) -> bool:
    rel = path.relative_to(skill_root).as_posix()
    if rel.startswith("references/archive"):
        return False
    if ".bak" in path.name or ".backup-" in path.name or "pre-clean" in path.name:
        return False
    return path.suffix.lower() in TEXT_EXTENSIONS


def check_file(skill_root: Path, path: Path) -> dict | None:
    rel = path.relative_to(skill_root).as_posix()
    data = path.read_bytes()
    issues: list[str] = []

    if data.startswith(b"\xef\xbb\xbf"):
        issues.append("bom")

    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError as exc:
        return {"file": rel, "issues": ["decode_error"], "detail": str(exc)}

    found_tokens = [token for token in SUSPICIOUS_TOKENS if token in text]
    private_use_chars = sorted({f"U+{ord(ch):04X}" for ch in text if 0xE000 <= ord(ch) <= 0xF8FF})

    if found_tokens or private_use_chars:
        issues.append("mojibake")

    if not issues:
        return None

    result = {"file": rel, "issues": issues}
    if found_tokens:
        result["tokens"] = found_tokens
    if private_use_chars:
        result["private_use_chars"] = private_use_chars
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=Path(__file__).resolve().parents[1], type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    skill_root: Path = args.root.resolve()
    findings: list[dict] = []
    checked = 0

    for path in skill_root.rglob("*"):
        if not path.is_file():
            continue
        if not is_active_text_file(skill_root, path):
            continue
        checked += 1
        finding = check_file(skill_root, path)
        if finding:
            findings.append(finding)

    payload = {"checked": checked, "issues": findings}

    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(f"Checked active text files: {checked}")
        if not findings:
            print("No UTF-8/BOM/mojibake issues found.")
        else:
            for finding in findings:
                print(json.dumps(finding, ensure_ascii=False))

    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
