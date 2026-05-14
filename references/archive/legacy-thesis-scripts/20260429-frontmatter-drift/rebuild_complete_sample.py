#!/usr/bin/env python3
"""Rebuild a complete thesis sample from a template, source manuscript, and assets."""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
import time
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

from docx_apply_table_family import patch_table
from python_runtime import resolve_python_exe


SCRIPTS_DIR = Path(__file__).resolve().parent
NS = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
W = "{%s}" % NS["w"]
HEADING_COLLECTION_TIMEOUT = 600
TOC_SYNC_TIMEOUT = 600

PYTHON_EXE = resolve_python_exe()
CAPTION_MARKER_RE = re.compile(r"(?:图|表)\s*[0-9一二三四五六七八九十]+(?:[-.．][0-9一二三四五六七八九十]+)?")
TABLE_CAPTION_RE = re.compile(r"^\s*(?:表|续表)\s*[0-9一二三四五六七八九十]+")


def run(cmd: list[str], *, workdir: Path | None = None, timeout: int = 1200, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd,
        check=check,
        cwd=str(workdir) if workdir else None,
        timeout=timeout,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )


def copy_locked(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    run([str(PYTHON_EXE), str(SCRIPTS_DIR / "copy_locked_docx.py"), str(src), str(dst)])


def export_pdf(input_docx: Path, output_pdf: Path) -> None:
    output_pdf.parent.mkdir(parents=True, exist_ok=True)
    run(
        [
            "powershell",
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            str(SCRIPTS_DIR / "wps_export_pdf.ps1"),
            "-InputDocx",
            str(input_docx),
            "-OutputPdf",
            str(output_pdf),
        ]
    )


def fallback_copy(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)


def media_count(docx_path: Path) -> int:
    with zipfile.ZipFile(docx_path) as zf:
        return sum(1 for name in zf.namelist() if name.startswith("word/media/"))


def document_xml_text(docx_path: Path) -> str:
    with zipfile.ZipFile(docx_path) as zf:
        return zf.read("word/document.xml").decode("utf-8", errors="ignore")


def read_with_retry(reader, docx_path: Path, *, retries: int = 30, delay_s: float = 0.5):
    """Retry transient locked/incomplete DOCX reads on Windows file handoff."""
    last_error: Exception | None = None
    for _ in range(retries):
        try:
            return reader(docx_path)
        except (PermissionError, OSError, zipfile.BadZipFile) as exc:
            last_error = exc
            time.sleep(delay_s)
    if last_error:
        raise last_error
    raise RuntimeError(f"unexpected retry state for {docx_path}")


def enriched_output_usable(base_docx: Path, candidate_docx: Path, returncode: int) -> bool:
    if not candidate_docx.exists():
        return False
    if returncode == 0:
        return True
    try:
        base_media = read_with_retry(media_count, base_docx) if base_docx.exists() else 0
        candidate_media = read_with_retry(media_count, candidate_docx)
        candidate_text = read_with_retry(document_xml_text, candidate_docx)
    except (PermissionError, OSError, zipfile.BadZipFile):
        if not base_docx.exists():
            return candidate_docx.stat().st_size > 0
        return candidate_docx.stat().st_size > base_docx.stat().st_size
    return candidate_media > base_media or bool(CAPTION_MARKER_RE.search(candidate_text))


def rendered_table_indices(docx_path: Path) -> list[int]:
    with zipfile.ZipFile(docx_path) as zf:
        root = ET.fromstring(zf.read("word/document.xml"))
    body = root.find("w:body", NS)
    if body is None:
        return []

    indices: list[int] = []
    total_tables = 0
    previous_text = ""
    for child in list(body):
        if child.tag == W + "p":
            text = "".join((node.text or "") for node in child.findall(".//w:t", NS)).strip()
            if text:
                previous_text = text
        elif child.tag == W + "tbl":
            total_tables += 1
            if TABLE_CAPTION_RE.match(previous_text.replace("\xa0", " ")):
                indices.append(total_tables)
    if indices:
        return indices
    return list(range(1, total_tables + 1))


def apply_rendered_table_family(docx_path: Path) -> None:
    for table_index in rendered_table_indices(docx_path):
        patch_table(docx_path, table_index, "wps_second_three_line_rendered")


def main() -> int:
    parser = argparse.ArgumentParser(description="Rebuild one complete thesis sample and emit PDF plus self-check.")
    parser.add_argument("--template", required=True, help="Template/reference DOCX path")
    parser.add_argument("--source", required=True, help="Source manuscript DOCX path")
    parser.add_argument("--assets-root", required=True, help="Asset root directory containing asset_manifest.json")
    parser.add_argument("--output-docx", required=True, help="Final rebuilt DOCX path")
    parser.add_argument("--output-pdf", required=True, help="Final rendered PDF path")
    parser.add_argument("--self-check", required=True, help="Self-check markdown output path")
    parser.add_argument("--run-root", help="Optional working directory; defaults to a timestamped sibling directory")
    parser.add_argument("--smoke-acceptance", action="store_true", help="Relax acceptance generation for smoke integration only")
    args = parser.parse_args()

    template = Path(args.template).resolve()
    source = Path(args.source).resolve()
    assets_root = Path(args.assets_root).resolve()
    output_docx = Path(args.output_docx).resolve()
    output_pdf = Path(args.output_pdf).resolve()
    self_check = Path(args.self_check).resolve()

    if args.run_root:
        run_root = Path(args.run_root).resolve()
    else:
        run_root = output_docx.parent / f"gpb_rebuild_{time.strftime('%Y%m%d_%H%M%S')}"

    run_root.mkdir(parents=True, exist_ok=True)
    (run_root / "meta").mkdir(parents=True, exist_ok=True)
    (run_root / "pages").mkdir(parents=True, exist_ok=True)
    (run_root / "reports").mkdir(parents=True, exist_ok=True)

    source_copy = run_root / "source_copy.docx"
    template_copy = run_root / "template_copy.docx"
    aligned_doc = run_root / "aligned.docx"
    enriched_doc = run_root / "enriched.docx"
    heading_pages = run_root / "meta" / "heading-pages.json"
    citation_audit = run_root / "reports" / "citation-audit.md"
    font_audit = run_root / "reports" / "font-audit.md"
    body_style_audit = run_root / "reports" / "body-style-audit.md"
    acceptance_record = run_root / "reports" / "acceptance-record.md"
    hardfield_inputs = {
        "surface_geometry": run_root / "reports" / "surface-geometry-required.json",
        "surface_paragraph_typography": run_root / "reports" / "surface-paragraph-typography-required.json",
        "toc_geometry": run_root / "reports" / "toc-geometry-required.json",
        "toc_paragraph_typography": run_root / "reports" / "toc-paragraph-typography-required.json",
        "whole_pagination": run_root / "reports" / "whole-pagination-required.json",
    }
    for path in hardfield_inputs.values():
        path.write_text(
            '{\n  "verdict": "blocked",\n  "reason": "measured hard-field producer has not supplied this required acceptance input"\n}\n',
            encoding="utf-8",
        )

    copy_locked(source, source_copy)
    copy_locked(template, template_copy)

    # Step 1: align source into a cleaner review copy.
    try:
        run([str(PYTHON_EXE), str(SCRIPTS_DIR / "align_target_thesis.py"), "--input", str(source_copy), "--output", str(aligned_doc)])
    except subprocess.CalledProcessError:
        fallback_copy(source_copy, aligned_doc)

    working_doc = aligned_doc

    # Step 2: optionally enrich with asset-manifest-driven figures/tables if compatible.
    asset_manifest = assets_root / "asset_manifest.json"
    if asset_manifest.exists():
        enrich = run(
            [
                str(PYTHON_EXE),
                str(SCRIPTS_DIR / "build_pass4_docx.py"),
                "--base-docx",
                str(aligned_doc),
                "--asset-manifest",
                str(asset_manifest),
                "--output-docx",
                str(enriched_doc),
            ],
            check=False,
            timeout=1800,
        )
        if enriched_output_usable(aligned_doc, enriched_doc, enrich.returncode):
            working_doc = enriched_doc
            if enrich.returncode != 0:
                print(
                    "warning: build_pass4_docx returned non-zero, but enriched.docx passed artifact checks and will be used",
                    file=sys.stderr,
                )

    # Step 3: collect heading pages and attempt TOC synchronization if the lane supports it.
    toc_target = output_docx
    try:
        collected = run(
            [
                str(PYTHON_EXE),
                str(SCRIPTS_DIR / "collect_heading_pages_word.py"),
                "--input",
                str(working_doc),
                "--output",
                str(heading_pages),
            ],
            check=False,
            timeout=HEADING_COLLECTION_TIMEOUT,
        )
    except subprocess.TimeoutExpired as exc:
        print(
            f"warning: heading page collection timed out after {int(exc.timeout)}s; skipping TOC page synchronization",
            file=sys.stderr,
        )
        collected = subprocess.CompletedProcess(exc.cmd, 124, exc.stdout or "", exc.stderr or "")
    if collected.returncode == 0 and heading_pages.exists():
        try:
            toc_sync = run(
                [
                    str(PYTHON_EXE),
                    str(SCRIPTS_DIR / "update_static_toc.py"),
                    "--input",
                    str(working_doc),
                    "--mapping",
                    str(heading_pages),
                    "--output",
                    str(output_docx),
                    "--reference-toc",
                    str(template_copy),
                ],
                check=False,
                timeout=TOC_SYNC_TIMEOUT,
            )
        except subprocess.TimeoutExpired as exc:
            print(
                f"warning: TOC synchronization timed out after {int(exc.timeout)}s; falling back to the current working DOCX",
                file=sys.stderr,
            )
            toc_sync = subprocess.CompletedProcess(exc.cmd, 124, exc.stdout or "", exc.stderr or "")
        media_before = media_count(working_doc) if working_doc.exists() else 0
        media_after = media_count(output_docx) if output_docx.exists() else 0
        if (
            toc_sync.returncode != 0
            or not output_docx.exists()
            or (media_before > 0 and media_after < media_before)
        ):
            fallback_copy(working_doc, output_docx)
    else:
        fallback_copy(working_doc, output_docx)

    run(
        [str(PYTHON_EXE), str(SCRIPTS_DIR / "normalize_thesis_citation_chain.py"), "--docx", str(output_docx)],
        check=False,
        timeout=1800,
    )
    try:
        apply_rendered_table_family(output_docx)
    except Exception as exc:
        print(f"warning: rendered table family fallback skipped: {exc}", file=sys.stderr)

    export_pdf(output_docx, output_pdf)
    run([str(PYTHON_EXE), str(SCRIPTS_DIR / "pdf_to_pages.py"), str(output_pdf), str(run_root / "pages")], timeout=1800)
    run([str(PYTHON_EXE), str(SCRIPTS_DIR / "audit_thesis_citations.py"), "--docx", str(output_docx), "--report", str(citation_audit)], check=False)
    run(
        [
            str(PYTHON_EXE),
            str(SCRIPTS_DIR / "audit_docx_font_encoding.py"),
            str(output_docx),
            "--reference-docx",
            str(template_copy),
            "--report",
            str(font_audit),
        ],
        check=False,
    )
    run(
        [
            str(PYTHON_EXE),
            str(SCRIPTS_DIR / "audit_docx_body_style.py"),
            "--reference-docx",
            str(template_copy),
            "--final-docx",
            str(output_docx),
            "--report",
            str(body_style_audit),
        ],
        check=False,
    )
    run(
        [
            str(PYTHON_EXE),
            str(SCRIPTS_DIR / "sample_self_check.py"),
            "--reference-docx",
            str(template_copy),
            "--final-docx",
            str(output_docx),
            "--final-pdf",
            str(output_pdf),
            "--citation-audit",
            str(citation_audit),
            "--font-audit",
            str(font_audit),
            "--body-style-audit",
            str(body_style_audit),
            "--asset-manifest",
            str(asset_manifest),
            "--output",
            str(self_check),
            "--fail-on-issues",
            *(["--smoke-acceptance"] if args.smoke_acceptance else []),
        ],
        timeout=1800,
    )
    run(
        [
            str(PYTHON_EXE),
            str(SCRIPTS_DIR / "generate_thesis_acceptance_record.py"),
            "--template",
            str(template_copy),
            "--final-docx",
            str(output_docx),
            "--final-pdf",
            str(output_pdf),
            "--self-check",
            str(self_check),
            "--citation-audit",
            str(citation_audit),
            "--font-audit",
            str(font_audit),
            "--body-style-audit",
            str(body_style_audit),
            "--surface-geometry-json",
            str(hardfield_inputs["surface_geometry"]),
            "--surface-paragraph-typography-json",
            str(hardfield_inputs["surface_paragraph_typography"]),
            "--toc-geometry-json",
            str(hardfield_inputs["toc_geometry"]),
            "--toc-paragraph-typography-json",
            str(hardfield_inputs["toc_paragraph_typography"]),
            "--whole-pagination-json",
            str(hardfield_inputs["whole_pagination"]),
            "--validator",
            f"{PYTHON_EXE} {SCRIPTS_DIR / 'validate_skill_gate.py'}",
            "--selftest-command",
            f"{PYTHON_EXE} {SCRIPTS_DIR / 'selftest_skill_flow.py'} --include-integration",
            "--helper-scripts-planned",
            "rebuild_complete_sample.py",
            "--delegated-canonical-helper-paths",
            str((SCRIPTS_DIR / "rebuild_complete_sample.py").resolve()),
            *(["--smoke-acceptance"] if args.smoke_acceptance else []),
            "--output",
            str(acceptance_record),
        ],
        timeout=1800,
    )
    if not args.smoke_acceptance:
        run(
            [str(PYTHON_EXE), str(SCRIPTS_DIR / "validate_skill_gate.py"), "--gate-record", str(acceptance_record)],
            timeout=1800,
        )

    print(f"run_root={run_root}")
    print(f"final_doc={output_docx}")
    print(f"final_pdf={output_pdf}")
    print(f"self_check={self_check}")
    print(f"acceptance_record={acceptance_record}")
    return 0


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    raise SystemExit(main())
