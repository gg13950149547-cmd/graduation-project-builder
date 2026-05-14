#!/usr/bin/env python3
"""Export a thesis structural figure from draw.io with safe defaults."""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
from pathlib import Path


KNOWN_DRAWIO_PATHS = [
    Path(r"C:\Program Files\draw.io\draw.io.exe"),
]
FALLBACK_TEXT = "Text is not SVG - cannot display"


def locate_drawio() -> Path:
    found = shutil.which("draw.io") or shutil.which("drawio") or shutil.which("draw.io.exe")
    if found:
        return Path(found)
    for candidate in KNOWN_DRAWIO_PATHS:
        if candidate.exists():
            return candidate
    raise FileNotFoundError("draw.io executable not found")


def export(drawio_exe: Path, input_path: Path, output_path: Path, *, width: int | None) -> None:
    cmd = [str(drawio_exe), "-x", "-o", str(output_path), str(input_path)]
    if width is not None:
        cmd.extend(["--width", str(width)])
    subprocess.run(cmd, check=True, timeout=300)


def sanitize_svg(svg_path: Path) -> None:
    text = svg_path.read_text(encoding="utf-8")
    text = re.sub(
        r'<switch><g requiredFeatures="http://www\.w3\.org/TR/SVG11/feature#Extensibility"/><a transform="translate\(0,-5\)" xlink:href="https://www\.drawio\.com/doc/faq/svg-export-text-problems" target="_blank"><text text-anchor="middle" font-size="10px" x="50%" y="100%">Text is not SVG - cannot display</text></a></switch>',
        "",
        text,
    )
    svg_path.write_text(text, encoding="utf-8")
    if FALLBACK_TEXT in svg_path.read_text(encoding="utf-8"):
        raise RuntimeError(f"draw.io SVG fallback text still present in {svg_path}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-drawio", required=True)
    parser.add_argument("--output-svg", required=True)
    parser.add_argument("--output-png")
    parser.add_argument("--width", type=int, default=900)
    args = parser.parse_args()

    drawio_exe = locate_drawio()
    input_drawio = Path(args.input_drawio).resolve()
    output_svg = Path(args.output_svg).resolve()
    output_svg.parent.mkdir(parents=True, exist_ok=True)
    export(drawio_exe, input_drawio, output_svg, width=args.width)
    sanitize_svg(output_svg)

    if args.output_png:
        output_png = Path(args.output_png).resolve()
        output_png.parent.mkdir(parents=True, exist_ok=True)
        export(drawio_exe, input_drawio, output_png, width=args.width)

    print(f"drawio={drawio_exe}")
    print(f"input={input_drawio}")
    print(f"svg={output_svg}")
    if args.output_png:
        print(f"png={Path(args.output_png).resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
