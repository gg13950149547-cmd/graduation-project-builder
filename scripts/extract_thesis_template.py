#!/usr/bin/env python3
"""Extract a simple heading skeleton from a thesis sample file."""

from __future__ import annotations

import argparse
import re
from pathlib import Path
from zipfile import ZipFile


def read_docx_text(path: Path) -> str:
    with ZipFile(path) as zf:
        xml = zf.read("word/document.xml").decode("utf-8", errors="ignore")
    text = re.sub(r"</w:p>", "\n", xml)
    text = re.sub(r"<[^>]+>", "", text)
    return (
        text.replace("&lt;", "<")
        .replace("&gt;", ">")
        .replace("&amp;", "&")
        .replace("\xa0", " ")
    )


def read_text(path: Path) -> str:
    if path.suffix.lower() == ".docx":
        return read_docx_text(path)
    return path.read_text(encoding="utf-8", errors="ignore")


def extract_headings(text: str) -> list[str]:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    found: list[str] = []
    for line in lines:
        if re.fullmatch(r"[0-9.]+", line):
            continue
        if "_" in line and re.fullmatch(r"[0-9A-Za-z._-]+", line):
            continue
        if (
            line in {"摘要", "Abstract", "结论", "参考文献", "致谢"}
            or line.startswith("第")
            or re.match(r"^[0-9]+\.[0-9]+(\.[0-9]+)?", line)
        ):
            if line not in found:
                found.append(line)
    return found


def main() -> int:
    parser = argparse.ArgumentParser(description="Extract heading skeleton from a thesis sample.")
    parser.add_argument("--input", required=True, help="Path to docx/txt/md sample")
    parser.add_argument("--output", default=None, help="Optional markdown output path")
    args = parser.parse_args()

    path = Path(args.input)
    headings = extract_headings(read_text(path))

    markdown = "# Thesis Template Skeleton\n\n" + "\n".join(f"- {item}" for item in headings) + "\n"

    if args.output:
        out = Path(args.output)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(markdown, encoding="utf-8")
        print(out)
    else:
        print(markdown)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
