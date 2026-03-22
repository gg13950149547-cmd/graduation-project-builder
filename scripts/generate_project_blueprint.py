#!/usr/bin/env python3
"""Inspect a project and generate a stack-aware delivery blueprint."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


STACK_MARKERS = [
    ("Django", ["manage.py"]),
    ("Flask", ["app.py"]),
    ("Python", ["requirements.txt", "pyproject.toml"]),
    ("Spring Boot/Maven", ["pom.xml"]),
    ("Java/Gradle", ["build.gradle", "build.gradle.kts"]),
    ("Node.js", ["package.json"]),
    ("Docker", ["Dockerfile", "docker-compose.yml", "docker-compose.yaml"]),
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


def infer_modules(root: Path) -> list[str]:
    candidates: list[str] = []
    banned_parts = {
        ".git",
        ".idea",
        ".vscode",
        "__pycache__",
        "node_modules",
        "dist",
        "build",
        "tools",
        "downloads",
        "site-packages",
        "share",
        "doc",
        "docs",
        "apidocs",
        "metadata",
        "class-use",
        "main",
        "test",
        "target",
        "src",
        "run-logs",
        ".m2",
    }
    top_level_skip = {
        ".git",
        ".idea",
        ".vscode",
        "__pycache__",
        "node_modules",
        "dist",
        "build",
        "static",
        "templates",
        "scripts",
        "docs",
        "config",
        "public",
        "assets",
        "tools",
        "downloads",
        "dist",
        "target",
        "src",
        "run-logs",
        ".m2",
    }
    for child in root.iterdir():
        if child.is_dir() and child.name not in top_level_skip and not child.name.startswith("."):
            candidates.append(child.name)
    common_roots = ["apps", "modules", "services", "src", "backend", "frontend"]
    for root_name in common_roots:
        for path in root.rglob(root_name):
            if path.is_dir() and not any(part in banned_parts for part in path.parts):
                for child in path.iterdir():
                    if (
                        child.is_dir()
                        and not child.name.startswith((".", "__", "node_modules", "dist", "build"))
                        and not any(part in banned_parts for part in child.parts)
                    ):
                        name = child.name.strip()
                        if name and name not in candidates:
                            candidates.append(name)
    return candidates[:12]


def infer_primary_project_root(root: Path) -> str:
    candidates = []
    for rel, score in [
        ("backend", 100),
        ("frontend", 80),
        ("app", 70),
        ("server", 60),
        ("src", 40),
    ]:
        path = root / rel
        if path.exists() and path.is_dir():
            candidates.append((score, rel))

    if (root / "backend" / "pom.xml").exists():
        candidates.append((120, "backend"))
    if (root / "backend" / "README.md").exists():
        candidates.append((110, "backend"))
    if (root / "app.py").exists() or (root / "manage.py").exists() or (root / "pom.xml").exists():
        candidates.append((90, "."))

    if not candidates:
        return "."
    candidates.sort(key=lambda item: (-item[0], item[1]))
    return candidates[0][1]


def infer_run_commands_for_root(root: Path, stacks: list[str]) -> list[str]:
    commands: list[str] = []
    for rel in [
        "deploy-oneclick.ps1",
        "deploy-oneclick.bat",
        "backend/scripts/start-backend.ps1",
        "scripts/start_project.ps1",
        "start_dashboard.ps1",
        "start_dashboard.cmd",
    ]:
        if (root / rel).exists():
            commands.append(rel)
    if "Django" in stacks:
        commands.extend(
            [
                "py -m pip install -r requirements.txt",
                "py manage.py migrate",
                "py manage.py runserver",
            ]
        )
    if "Flask" in stacks and "Django" not in stacks:
        commands.extend(
            [
                "py -m pip install -r requirements.txt",
                "py run_pipeline.py",
                "py app\\app.py",
            ]
        )
    if "Pipeline" in stacks and "py run_pipeline.py" not in commands:
        commands.append("py run_pipeline.py")
    if "Hadoop" in stacks:
        commands.append("py scripts\\upload_to_hdfs.py")
    if "Spring Boot/Maven" in stacks:
        commands.extend(["mvn test", "mvn spring-boot:run"])
    if "Java/Gradle" in stacks:
        commands.extend(["gradlew test", "gradlew bootRun"])
    if "Node.js" in stacks:
        commands.extend(["npm install", "npm run build", "npm run dev"])
    return commands or ["[待补充实际启动命令]"]


def build_markdown(root: Path, project_name: str | None) -> str:
    stacks = detect_stacks(root)
    modules = infer_modules(root)
    run_commands = infer_run_commands_for_root(root, stacks)
    primary_root = infer_primary_project_root(root)

    module_lines = "\n".join(f"- {name}" for name in modules) if modules else "- 待从仓库结构补充"
    stack_lines = "\n".join(f"- {name}" for name in stacks)
    run_lines = "\n".join(f"- `{cmd}`" for cmd in run_commands)

    return f"""# {project_name or root.name} Project Blueprint

## Repository Summary

- Root: `{root}`
- Primary app root: `{primary_root}`
- Detected stacks:
{stack_lines}

## Inferred Delivery Targets

- Summarize requirements into a stable brief
- Complete missing core modules
- Add or fix data initialization flow
- Add or fix verification flow
- Ensure startup and packaging steps are documented

## Candidate Modules

{module_lines}

## Suggested Backlog

- Confirm user roles and entry flows
- Confirm core business entities and data tables
- Complete one end-to-end slice per main module
- Add seed, import, or demo-data path
- Add or verify pipeline, analysis, and export path if the repo is analytics-oriented
- Add narrow regression tests for critical paths
- Add deploy, start, and packaging guidance

## Candidate Commands

{run_lines}

## Open Questions

- Which module is the main demo path?
- Which data source is authoritative?
- Which checks already pass, and which are missing?
"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate a stack-aware project blueprint.")
    parser.add_argument("--root", default=".", help="Project root to inspect")
    parser.add_argument("--project-name", default=None)
    parser.add_argument("--output", default="docs/project-blueprint.md")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    output_path = Path(args.output)
    if not output_path.is_absolute():
        output_path = root / output_path

    output_path.parent.mkdir(parents=True, exist_ok=True)
    content = build_markdown(root=root, project_name=args.project_name)
    output_path.write_text(content, encoding="utf-8")

    meta = {
        "root": str(root),
        "output": str(output_path),
        "stacks": detect_stacks(root),
        "modules": infer_modules(root),
        "primary_root": infer_primary_project_root(root),
    }
    print(json.dumps(meta, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
