from __future__ import annotations

import argparse
from pathlib import Path

import fitz


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("pdf_path")
    parser.add_argument("output_dir")
    parser.add_argument("--dpi", type=int, default=144)
    args = parser.parse_args()

    pdf_path = Path(args.pdf_path).resolve()
    output_dir = Path(args.output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    for stale_image in output_dir.glob("page-*.png"):
        stale_image.unlink()

    zoom = args.dpi / 72.0
    matrix = fitz.Matrix(zoom, zoom)

    with fitz.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf, start=1):
            pix = page.get_pixmap(matrix=matrix, alpha=False)
            out_path = output_dir / f"page-{page_num:03d}.png"
            pix.save(out_path)
            print(out_path)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
