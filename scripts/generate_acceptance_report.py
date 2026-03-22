#!/usr/bin/env python3
"""Generate a simple acceptance report for a project."""

from __future__ import annotations

import argparse
from pathlib import Path


STACK_MARKERS = [
    ("Django", ["manage.py"]),
    ("Flask", ["app.py"]),
    ("Python", ["requirements.txt", "pyproject.toml"]),
    ("Spring Boot/Maven", ["pom.xml"]),
    ("Java/Gradle", ["build.gradle", "build.gradle.kts"]),
    ("Node.js", ["package.json"]),
    ("Pipeline", ["run_pipeline.py"]),
    ("Hadoop", ["upload_to_hdfs.py", "start-hadoop.cmd", "verify-hadoop.cmd"]),
]


def find_files(root: Path, names: list[str]) -> list[Path]:
    found: list[Path] = []
    for name in names:
        found.extend(root.rglob(name))
    return found


def detect_stacks(root: Path) -> list[str]:
    stacks: list[str] = []
    for stack, markers in STACK_MARKERS:
        if find_files(root, markers):
            stacks.append(stack)
    return stacks or ["Unknown"]


def check_exists(root: Path, rels: list[str]) -> list[str]:
    return [rel for rel in rels if (root / rel).exists()]


def filtered_find_files(root: Path, names: list[str], banned_parts: set[str]) -> list[Path]:
    results: list[Path] = []
    for name in names:
        for path in root.rglob(name):
            if not any(part in banned_parts for part in path.parts):
                results.append(path)
    return results


def collect_existing(root: Path, rels: list[str]) -> list[str]:
    found: list[str] = []
    for rel in rels:
        if (root / rel).exists() and rel not in found:
            found.append(rel)
    return found


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate a defendability acceptance report.")
    parser.add_argument("--root", default=".", help="Project root")
    parser.add_argument("--output", default="docs/acceptance-report.md")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    output = Path(args.output)
    if not output.is_absolute():
        output = root / output
    output.parent.mkdir(parents=True, exist_ok=True)

    stacks = detect_stacks(root)
    banned_parts = {"tools", "downloads", "dist", "site-packages", "__pycache__", "node_modules", "target", ".m2"}
    docs = collect_existing(
        root,
        [
            "README.md",
            "README.txt",
            "DEPLOYMENT.md",
            "PACKAGE_MANUAL.md",
            "docs/project-blueprint.md",
            "backend/README.md",
            "backend/db-switch.md",
        ],
    )
    scripts = collect_existing(
        root,
        [
            "deploy-oneclick.ps1",
            "deploy-oneclick.bat",
            "deploy.bat",
            "start.bat",
            "scripts/deploy_project.ps1",
            "scripts/start_project.ps1",
            "scripts/package_release.ps1",
            "scripts/codex_deploy.ps1",
            "scripts/codex_start.ps1",
            "scripts/codex_test.ps1",
            "scripts/codex_package.ps1",
            "backend/scripts/start-backend.ps1",
            "backend/scripts/smoke-test.ps1",
            "backend/scripts/smoke-user.ps1",
            "backend/scripts/smoke-admin.ps1",
            "run_pipeline.cmd",
            "run_pipeline.py",
            "start_dashboard.cmd",
            "start_dashboard.ps1",
            "scripts/upload_to_hdfs.py",
            "scripts/sync_to_mysql.py",
        ],
    )
    tests = filtered_find_files(root, ["tests.py", "test_*.py", "*.spec.ts", "*.test.ts", "*.test.js"], banned_parts)
    smoke_scripts = collect_existing(
        root,
        [
            "backend/scripts/smoke-test.ps1",
            "backend/scripts/smoke-user.ps1",
            "backend/scripts/smoke-admin.ps1",
        ],
    )
    data_signals = filtered_find_files(root, ["*.sql", "fixtures.json", "seed*.py", "seed*.js", "manage.py"], banned_parts)
    pipeline_signals = check_exists(
        root,
        [
            "run_pipeline.py",
            "scripts/generate_data.py",
            "scripts/clean_data.py",
            "scripts/analyze_data.py",
            "scripts/upload_to_hdfs.py",
            "scripts/sync_to_mysql.py",
            "scripts/sync_to_mongodb.py",
        ],
    )

    missing: list[str] = []
    if not docs:
        missing.append("No obvious README or blueprint file was found.")
    if not scripts:
        missing.append("No startup, deployment, packaging, or generated helper scripts were found.")
    if not tests and not smoke_scripts:
        missing.append("No obvious automated test files were found.")
    if not data_signals:
        missing.append("No seed, SQL, or initialization signals were found.")
    if "Pipeline" in stacks and not pipeline_signals:
        missing.append("The repo looks pipeline-oriented but no clear pipeline stages were found.")

    doc_lines = [f"- `{item}`" for item in docs] if docs else ["- None found"]
    script_lines = [f"- `{item}`" for item in scripts] if scripts else ["- None found"]
    if tests:
        test_lines = [f"- `{path.relative_to(root)}`" for path in tests[:20]]
    elif smoke_scripts:
        test_lines = [f"- `{item}`" for item in smoke_scripts]
    else:
        test_lines = ["- None found"]
    data_lines = [f"- `{path.relative_to(root)}`" for path in data_signals[:20]] if data_signals else ["- None found"]
    readiness_lines = (
        [f"- {item}" for item in missing]
        if missing
        else ["- The repository has the minimum visible surfaces for a defendable software delivery pass."]
    )

    content = "\n".join(
        [
            "# Acceptance Report",
            "",
            "## Detected Stack",
            "",
            *[f"- {stack}" for stack in stacks],
            "",
            "## Existing Documentation",
            "",
            *doc_lines,
            "",
            "## Existing Operations Surfaces",
            "",
            *script_lines,
            "",
            "## Existing Test Signals",
            "",
            *test_lines,
            "",
            "## Existing Data Initialization Signals",
            "",
            *data_lines,
            "",
            "## Existing Pipeline Signals",
            "",
            *([f"- `{item}`" for item in pipeline_signals] if pipeline_signals else ["- None found"]),
            "",
            "## Readiness Assessment",
            "",
            *readiness_lines,
            "",
            "## Next Actions",
            "",
            "- Verify the main demo path manually.",
            "- Run the narrowest relevant automated checks for the detected stack.",
            "- Fill any missing deployment, startup, packaging, or test surfaces.",
            "- Document blockers explicitly if the project is still not defendable.",
            "",
        ]
    )
    output.write_text(content, encoding="utf-8")
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
