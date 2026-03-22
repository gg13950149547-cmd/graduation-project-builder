#!/usr/bin/env python3
"""Generate project-aware delivery helper scripts for a repository."""

from __future__ import annotations

import argparse
import json
import re
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


def first_existing(root: Path, candidates: list[str]) -> str | None:
    for rel in candidates:
        if (root / rel).exists():
            return rel
    return None


def read_text_if_possible(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return ""


def gather_reference_text(root: Path) -> str:
    candidates = [
        "README.md",
        "README.txt",
        "DEPLOYMENT.md",
        "PACKAGE_MANUAL.md",
        "deploy/交付说明.md",
        "docs/project-blueprint.md",
        "backend/README.md",
        "backend/db-switch.md",
    ]
    parts: list[str] = []
    for rel in candidates:
        path = root / rel
        if path.exists():
            parts.append(read_text_if_possible(path))
    return "\n".join(parts)


def extract_urls(text: str) -> list[str]:
    seen: list[str] = []
    for match in re.findall(r"https?://[^\s`'\"<>]+", text):
        if match not in seen:
            seen.append(match)
    return seen


def extract_env_vars(text: str) -> list[str]:
    seen: list[str] = []
    for match in re.findall(r"\b[A-Z][A-Z0-9_]{2,}\b", text):
        if any(token in match for token in ("PATH", "ROOT", "HOST", "PORT", "USER", "PASSWORD", "NAME", "URI", "DB")):
            if match not in seen:
                seen.append(match)
    return seen


def extract_credentials(text: str) -> list[str]:
    found: list[str] = []
    pattern = r"(?:普通用户|管理员|测试账号|演示账号)[^：:\n]*[：:]\s*`?([^\s`/]+)\s*/\s*([^\s`\n]+)`?"
    for match in re.findall(pattern, text):
        found.append(f"username={match[0]}, password={match[1]}")
    return found[:10]


def extract_runtime_paths(text: str) -> list[str]:
    found: list[str] = []
    for match in re.findall(r"[A-Z]:\\[A-Za-z0-9_ .\\\-\(\)]+", text):
        cleaned = match.strip().strip("`'\"").rstrip(".")
        if "<" in cleaned or ">" in cleaned:
            continue
        if len(cleaned) < 4:
            continue
        if cleaned not in found:
            found.append(cleaned)
    return found[:20]


def extract_ports(text: str) -> list[str]:
    found: list[str] = []
    for match in re.findall(r"(?::|\bport\b[= :])(\d{2,5})", text, flags=re.IGNORECASE):
        if match not in found:
            found.append(match)
    return found[:10]


def extract_db_names(text: str) -> list[str]:
    found: list[str] = []
    patterns = [
        r"jdbc:mysql://[^/\s]+/([A-Za-z0-9_\-]+)",
        r"数据库名称[：:]\s*`?([A-Za-z0-9_\-]+)`?",
        r"MALL_DB_NAME[=：:\s]+([A-Za-z0-9_\-]+)",
    ]
    for pattern in patterns:
        for match in re.findall(pattern, text, flags=re.IGNORECASE):
            cleaned = match.strip("`'\" ").rstrip(".")
            if cleaned == "-" or not cleaned:
                continue
            if cleaned not in found:
                found.append(cleaned)
    return found[:10]


def score_candidate(rel: str, content: str, mode: str) -> int:
    rel_lower = rel.lower().replace("\\", "/")
    file_name = Path(rel_lower).name
    text = content.lower()
    score = 0

    if mode == "deploy":
        if "deploy" in file_name or "setup" in file_name or "install" in file_name:
            score += 60
        if "install" in text or "pip install" in text or "migrate" in text or "compile" in text:
            score += 40
        if "start-hadoop" in rel_lower or "start-mongodb" in rel_lower or "verify-hadoop" in rel_lower:
            score -= 50
    elif mode == "start":
        if "start" in file_name or "run" in file_name:
            score += 60
        if "runserver" in text or "spring-boot:run" in text or "npm run" in text or "app.py" in text:
            score += 40
        if "stop-" in rel_lower or "verify-" in rel_lower:
            score -= 50
    elif mode == "package":
        if "package" in file_name or "release" in file_name:
            score += 60
        if "compress-archive" in text or ".zip" in text or "build_delivery" in rel_lower:
            score += 40
    elif mode == "test":
        if "test" in file_name or "check" in file_name:
            score += 60
        if "pytest" in text or "manage.py test" in text or "mvn test" in text or "gradlew.bat test" in text:
            score += 40

    return score


def best_candidate(root: Path, candidates: list[str], mode: str) -> str | None:
    ranked: list[tuple[int, str]] = []
    for rel in candidates:
        path = root / rel
        if not path.exists():
            continue
        score = score_candidate(rel, read_text_if_possible(path), mode)
        ranked.append((score, rel))
    if not ranked:
        return None
    ranked.sort(key=lambda item: (-item[0], item[1]))
    if ranked[0][0] <= 0:
        return None
    return ranked[0][1]


def read_package_scripts(root: Path) -> dict[str, str]:
    package_json = root / "package.json"
    if not package_json.exists():
        return {}
    try:
        data = json.loads(package_json.read_text(encoding="utf-8"))
    except Exception:
        return {}
    scripts = data.get("scripts")
    return scripts if isinstance(scripts, dict) else {}


def path_command(rel: str) -> str:
    normalized = rel.replace("/", "\\")
    lower = rel.lower()
    if lower.endswith(".ps1"):
        return f"powershell -ExecutionPolicy Bypass -File .\\{normalized}"
    if lower.endswith(".cmd") or lower.endswith(".bat"):
        return f".\\{normalized}"
    if lower.endswith(".py"):
        return f"py .\\{normalized}"
    return f".\\{normalized}"


def infer_deploy_command(root: Path, stacks: list[str]) -> str:
    existing = best_candidate(
        root,
        [
            "deploy-oneclick.ps1",
            "deploy-oneclick.bat",
            "scripts/deploy_project.ps1",
            "deploy.bat",
            "deploy.cmd",
            "scripts/deploy.ps1",
            "scripts/install.ps1",
            "scripts/setup.ps1",
            "setup.ps1",
            "setup.cmd",
            "backend/scripts/deploy_project.ps1",
            "deploy/start-hadoop.cmd",
            "deploy/start-hadoop.ps1",
            "deploy/start-mongodb.cmd",
            "deploy/start-mongodb.ps1",
        ],
        "deploy",
    )
    if existing:
        return path_command(existing)
    if "Node.js" in stacks:
        return "npm install"
    if "Django" in stacks:
        return "py -m pip install -r requirements.txt"
    if "Flask" in stacks or "Python" in stacks:
        return "py -m pip install -r requirements.txt"
    if "Spring Boot/Maven" in stacks:
        return "mvn -q -DskipTests compile"
    if "Java/Gradle" in stacks:
        return ".\\gradlew.bat classes"
    return 'Write-Host "No deploy command inferred. Edit this file for the current project."'


def infer_start_command(root: Path, stacks: list[str]) -> str:
    existing = best_candidate(
        root,
        [
            "backend/scripts/start-backend.ps1",
            "scripts/start_project.ps1",
            "start_dashboard.ps1",
            "start_dashboard.cmd",
            "start.bat",
            "start.cmd",
            "scripts/start.ps1",
            "run.cmd",
            "run.bat",
        ],
        "start",
    )
    if existing:
        return path_command(existing)
    package_scripts = read_package_scripts(root)
    if "dev" in package_scripts:
        return "npm run dev"
    if "start" in package_scripts:
        return "npm run start"
    if "Django" in stacks:
        return 'if (Test-Path ".venv\\Scripts\\python.exe") { .\\.venv\\Scripts\\python.exe manage.py runserver 127.0.0.1:8000 --noreload } else { py manage.py runserver 127.0.0.1:8000 --noreload }'
    if (root / "app" / "app.py").exists():
        return "py .\\app\\app.py"
    if (root / "app.py").exists():
        return "py .\\app.py"
    if "Spring Boot/Maven" in stacks:
        return "mvn spring-boot:run"
    if "Java/Gradle" in stacks:
        return ".\\gradlew.bat bootRun"
    return 'Write-Host "No start command inferred. Edit this file for the current project."'


def infer_test_commands(root: Path, stacks: list[str]) -> list[str]:
    package_scripts = read_package_scripts(root)
    commands: list[str] = []
    if "Django" in stacks:
        python_cmd = 'if (Test-Path ".venv\\Scripts\\python.exe") { ".\\.venv\\Scripts\\python.exe" } else { "py" }'
        commands.extend(
            [
                f"$PythonExe = {python_cmd}",
                "& $PythonExe manage.py check",
                "& $PythonExe manage.py test",
            ]
        )
        return commands
    smoke_scripts = [
        rel
        for rel in [
            "backend/scripts/smoke-test.ps1",
            "backend/scripts/smoke-user.ps1",
            "backend/scripts/smoke-admin.ps1",
        ]
        if (root / rel).exists()
    ]
    if smoke_scripts:
        commands.extend(path_command(rel) for rel in smoke_scripts)
        return commands
    if first_existing(root, ["tests.py"]) or find_files(root, ["test_*.py"]):
        commands.append("py -m pytest")
        return commands
    if (root / "run_pipeline.py").exists():
        commands.append("py .\\run_pipeline.py")
    if (root / "app" / "app.py").exists():
        commands.append(
            'py -c "import importlib.util; spec = importlib.util.spec_from_file_location(\'app_probe\', r\'app\\app.py\'); mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod); print(\'App import check passed\')"'
        )
    if "test" in package_scripts:
        commands.append("npm test")
    if "Spring Boot/Maven" in stacks:
        commands.append("mvn test")
    if "Java/Gradle" in stacks:
        commands.append(".\\gradlew.bat test")
    if not commands:
        commands.append('Write-Host "No finite test command inferred. Edit this file for the current project."')
    return commands


def infer_package_command(root: Path, stacks: list[str]) -> str:
    existing = best_candidate(
        root,
        [
            "scripts/build_delivery_package.ps1",
            "scripts/package_release.ps1",
            "package.bat",
            "package.cmd",
        ],
        "package",
    )
    if existing:
        return path_command(existing)
    package_scripts = read_package_scripts(root)
    if "build" in package_scripts:
        return "npm run build"
    if "Spring Boot/Maven" in stacks:
        return "mvn -DskipTests package"
    if "Java/Gradle" in stacks:
        return ".\\gradlew.bat build -x test"
    if "Django" in stacks or "Flask" in stacks or "Python" in stacks:
        return (
            '$DistPath = Join-Path $ProjectRoot "dist"\n'
            'if (-not (Test-Path $DistPath)) { New-Item -ItemType Directory -Path $DistPath | Out-Null }\n'
            '$PackagePath = Join-Path $DistPath "delivery-bundle.zip"\n'
            'if (Test-Path $PackagePath) { Remove-Item $PackagePath -Force }\n'
            '$items = Get-ChildItem -Force | Where-Object { $_.Name -notin @(".git", ".venv", "node_modules", "__pycache__") }\n'
            'Compress-Archive -Path $items.FullName -DestinationPath $PackagePath -Force\n'
            'Write-Host "Package created:" $PackagePath'
        )
    return 'Write-Host "No package command inferred. Edit this file for the current project."'


def package_prelude() -> list[str]:
    return [
        '$ProjectRoot = Split-Path -Parent $PSScriptRoot',
        "Set-Location $ProjectRoot",
        '$RequiredArtifacts = @("scripts\\codex_deploy.ps1", "scripts\\codex_start.ps1", "docs\\manual-deployment.md")',
        '$MissingArtifacts = $RequiredArtifacts | Where-Object { -not (Test-Path $_) }',
        'if ($MissingArtifacts.Count -gt 0) {',
        '    Write-Host "Missing delivery artifacts detected. Regenerating scaffold..."',
        '    py "C:\\Users\\Administrator\\.codex\\skills\\graduation-project-builder\\scripts\\generate_delivery_scaffold.py" --root $ProjectRoot --force',
        '}',
    ]


def build_commands(root: Path, stacks: list[str]) -> dict[str, list[str]]:
    deploy_command = infer_deploy_command(root, stacks)
    start_command = infer_start_command(root, stacks)
    test_commands = infer_test_commands(root, stacks)
    package_command = infer_package_command(root, stacks)

    commands: dict[str, list[str]] = {
        "deploy": [
            '$ProjectRoot = Split-Path -Parent $PSScriptRoot',
            "Set-Location $ProjectRoot",
            deploy_command,
        ],
        "start": [
            '$ProjectRoot = Split-Path -Parent $PSScriptRoot',
            "Set-Location $ProjectRoot",
            start_command,
        ],
        "test": [
            '$ProjectRoot = Split-Path -Parent $PSScriptRoot',
            "Set-Location $ProjectRoot",
            *test_commands,
        ],
        "package": [*package_prelude()],
    }

    if "\n" in package_command:
        commands["package"].extend(package_command.splitlines())
    else:
        commands["package"].append(package_command)
    return commands


def write_ps1(path: Path, lines: list[str]) -> None:
    content = '$ErrorActionPreference = "Stop"\n\n' + "\n".join(lines) + "\n"
    path.write_text(content, encoding="utf-8")


def build_manual_deployment(root: Path, commands: dict[str, list[str]]) -> str:
    stacks = detect_stacks(root)
    deploy_cmd = infer_deploy_command(root, stacks)
    start_cmd = infer_start_command(root, stacks)
    test_preview = [line for line in commands["test"] if not line.startswith("$") and line != "Set-Location $ProjectRoot"]
    reference_text = gather_reference_text(root)
    urls = extract_urls(reference_text)
    env_vars = extract_env_vars(reference_text)
    credentials = extract_credentials(reference_text)
    runtime_paths = extract_runtime_paths(reference_text)
    ports = extract_ports(reference_text)
    db_names = extract_db_names(reference_text)
    optional_steps: list[str] = []

    lines = [
        "# Manual Deployment Guide",
        "",
        "## Purpose",
        "",
        "This guide is generated from the current project structure, not from a fixed stack template.",
        "",
        "## Generated One-Click Files",
        "",
        "- `scripts/codex_deploy.ps1`",
        "- `scripts/codex_start.ps1`",
        "- `scripts/codex_package.ps1`",
        "",
        "## Manual Deployment Steps",
        "",
        "1. Enter the project root.",
    ]

    step_no = 2
    if (root / "requirements.txt").exists() and "requirements.txt" not in deploy_cmd:
        lines.append(f"{step_no}. Install dependencies if needed: `py -m pip install -r requirements.txt`")
        step_no += 1

    lines.append(f"{step_no}. Run the deployment/setup command: `{deploy_cmd}`")
    step_no += 1

    if "Hadoop" in stacks:
        hadoop_start = first_existing(root, ["deploy/start-hadoop.cmd", "deploy/start-hadoop.ps1", "deploy/verify-hadoop.cmd"])
        if hadoop_start:
            optional_steps.append(f"Hadoop-related infrastructure: `{path_command(hadoop_start)}`")

    lines.append(f"{step_no}. Run the startup command: `{start_cmd}`")

    if test_preview:
        lines.extend(
            [
                f"{step_no + 1}. Optional verification commands inferred from the project:",
                *[f"   - `{line}`" for line in test_preview],
            ]
        )

    if urls:
        lines.extend(
            [
                "",
                "## Known Access URLs",
                "",
                *[f"- `{url}`" for url in urls],
            ]
        )

    if env_vars:
        lines.extend(
            [
                "",
                "## Likely Environment Variables",
                "",
                *[f"- `{item}`" for item in env_vars[:20]],
            ]
        )

    if credentials:
        lines.extend(
            [
                "",
                "## Known Demo Credentials",
                "",
                *[f"- `{item}`" for item in credentials],
            ]
        )

    if db_names:
        lines.extend(
            [
                "",
                "## Likely Database Names",
                "",
                *[f"- `{item}`" for item in db_names],
            ]
        )

    if ports:
        lines.extend(
            [
                "",
                "## Likely Runtime Ports",
                "",
                *[f"- `{item}`" for item in ports],
            ]
        )

    if runtime_paths:
        lines.extend(
            [
                "",
                "## Referenced Local Runtime Paths",
                "",
                *[f"- `{item}`" for item in runtime_paths],
            ]
        )

    if optional_steps:
        lines.extend(
            [
                "",
                "## Optional Infrastructure Steps",
                "",
                *[f"- {item}" for item in optional_steps],
            ]
        )

    lines.extend(
        [
            "",
            "## Notes",
            "",
            "- These steps were inferred from the repository's current files and scripts.",
            "- If the project structure changes, regenerate the scaffold so the commands stay aligned.",
            "- If one-click scripts fail, execute the commands above manually and inspect the first failing step.",
            "",
        ]
    )
    return "\n".join(lines) + "\n"


def write_manifest(path: Path, stacks: list[str], commands: dict[str, list[str]]) -> None:
    content = "\n".join(
        [
            "# Delivery Scaffold Manifest",
            "",
            "Generated artifacts:",
            "- scripts/codex_deploy.ps1",
            "- scripts/codex_start.ps1",
            "- scripts/codex_test.ps1",
            "- scripts/codex_package.ps1",
            "- docs/manual-deployment.md",
            "",
            "Detected stacks:",
            *[f"- {stack}" for stack in stacks],
            "",
            "Inference mode:",
            "- Commands are derived from the current repository structure and existing entrypoints.",
            "",
            "Key inferred commands:",
            f"- Deploy: `{next((line for line in commands['deploy'] if not line.startswith('$') and line != 'Set-Location $ProjectRoot'), 'N/A')}`",
            f"- Start: `{next((line for line in commands['start'] if not line.startswith('$') and line != 'Set-Location $ProjectRoot'), 'N/A')}`",
            "",
        ]
    )
    path.write_text(content, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate delivery helper scripts for a project.")
    parser.add_argument("--root", default=".", help="Project root")
    parser.add_argument("--force", action="store_true", help="Overwrite existing codex helper scripts")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    scripts_dir = root / "scripts"
    docs_dir = root / "docs"
    scripts_dir.mkdir(parents=True, exist_ok=True)
    docs_dir.mkdir(parents=True, exist_ok=True)

    stacks = detect_stacks(root)
    commands = build_commands(root, stacks)

    generated: list[str] = []
    for key, lines in commands.items():
        output = scripts_dir / f"codex_{key}.ps1"
        if output.exists() and not args.force:
            continue
        write_ps1(output, lines)
        generated.append(str(output))

    manifest = docs_dir / "delivery-scaffold.md"
    write_manifest(manifest, stacks, commands)
    generated.append(str(manifest))

    manual = docs_dir / "manual-deployment.md"
    manual.write_text(build_manual_deployment(root, commands), encoding="utf-8")
    generated.append(str(manual))

    print("\n".join(generated))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
