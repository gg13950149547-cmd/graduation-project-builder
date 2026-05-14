#!/usr/bin/env python3
"""Validate project-local thesis adapter manifests.

Local adapters are allowed to describe a specific template, project, and run.
They must not become reusable thesis-generation engines or carry business-format
policy that belongs in the canonical skill scripts.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


SCHEMA = "graduation-project-builder.local-thesis-adapter.v1"
ALLOWED_ADAPTER_TYPES = {
    "template-profile",
    "project-content-manifest",
    "thin-wrapper-manifest",
    "run-manifest",
}
REQUIRED_KEYS = {
    "schema",
    "adapter_type",
    "canonical_scripts",
    "template_specific",
    "allowed_scope",
}
FORBIDDEN_KEYS = {
    "generic_engine",
    "business_format_policy",
    "global_font_policy",
    "heading_policy",
    "toc_policy",
    "abstract_policy",
    "table_policy",
    "figure_policy",
    "citation_policy",
    "reference_policy",
    "pagination_policy",
    "acceptance_verdict",
    "success_verdict",
}
FORBIDDEN_TEXT_TOKENS = {
    "paragraph.clear(",
    "clear_paragraph(",
    "set_paragraph_text(",
    "replace_paragraph_text(",
    "doc.paragraphs[",
    "Document(",
    "add_picture(",
    "InlineShapes.AddPicture",
    "ParagraphFormat.LineSpacingRule",
    "Heading 1",
    "Heading 2",
    "Heading 3",
    "Times New Roman",
    "Arial",
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path) -> tuple[dict[str, Any] | None, list[str]]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return None, [f"adapter manifest is not valid UTF-8 JSON: {exc}"]
    if not isinstance(data, dict):
        return None, ["adapter manifest root must be a JSON object"]
    return data, []


def iter_keys(value: Any) -> list[str]:
    keys: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            keys.append(str(key))
            keys.extend(iter_keys(child))
    elif isinstance(value, list):
        for child in value:
            keys.extend(iter_keys(child))
    return keys


def canonical_script_ok(script: str, skill_root: Path | None) -> bool:
    normalized = script.replace("\\", "/")
    if not normalized.startswith("scripts/"):
        return False
    if ".." in Path(normalized).parts:
        return False
    if skill_root is not None:
        return (skill_root / normalized).exists()
    return True


def validate_adapter_data(data: dict[str, Any], *, skill_root: Path | None = None) -> list[str]:
    issues: list[str] = []
    missing = sorted(REQUIRED_KEYS - set(data))
    if missing:
        issues.append("missing required keys: " + ", ".join(missing))

    if data.get("schema") != SCHEMA:
        issues.append(f"schema must be {SCHEMA}")

    adapter_type = data.get("adapter_type")
    if adapter_type not in ALLOWED_ADAPTER_TYPES:
        issues.append("adapter_type must be one of: " + ", ".join(sorted(ALLOWED_ADAPTER_TYPES)))

    if data.get("template_specific") is not True:
        issues.append("template_specific must be true")

    if not (data.get("template_path") or data.get("template_fingerprint")):
        issues.append("template_path or template_fingerprint is required")
    template_path = str(data.get("template_path") or "").strip()
    template_fingerprint = str(data.get("template_fingerprint") or "").strip().lower()
    if template_path:
        resolved_template = Path(template_path).expanduser()
        if not resolved_template.is_absolute():
            issues.append("template_path must be absolute so template identity cannot drift by cwd")
        elif not resolved_template.exists():
            issues.append(f"template_path does not exist: {resolved_template}")
        elif template_fingerprint:
            actual_fingerprint = sha256_file(resolved_template).lower()
            if actual_fingerprint != template_fingerprint:
                issues.append(
                    "template_fingerprint does not match template_path: "
                    f"expected {template_fingerprint}; actual {actual_fingerprint}"
                )
    if not (data.get("project_root") or data.get("run_root")):
        issues.append("project_root or run_root is required")

    canonical_scripts = data.get("canonical_scripts")
    if not isinstance(canonical_scripts, list) or not canonical_scripts:
        issues.append("canonical_scripts must be a non-empty list")
    else:
        for item in canonical_scripts:
            if not isinstance(item, str) or not canonical_script_ok(item, skill_root):
                issues.append(f"canonical script is not under the canonical skill scripts directory: {item}")

    allowed_scope = data.get("allowed_scope")
    if not isinstance(allowed_scope, list) or not all(isinstance(item, str) and item.strip() for item in allowed_scope):
        issues.append("allowed_scope must be a non-empty list of strings")

    present_forbidden_keys = sorted(FORBIDDEN_KEYS.intersection(iter_keys(data)))
    if present_forbidden_keys:
        issues.append("forbidden generic-policy keys present: " + ", ".join(present_forbidden_keys))

    serialized = json.dumps(data, ensure_ascii=False, sort_keys=True)
    lowered = serialized.lower()
    forbidden_tokens = sorted(token for token in FORBIDDEN_TEXT_TOKENS if token.lower() in lowered)
    if forbidden_tokens:
        issues.append("forbidden implementation/policy tokens present: " + ", ".join(forbidden_tokens))

    return issues


def validate_adapter_file(path: Path, *, skill_root: Path | None = None) -> list[str]:
    data, issues = load_json(path)
    if data is None:
        return issues
    return issues + validate_adapter_data(data, skill_root=skill_root)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--adapter", required=True, help="Project-local adapter manifest JSON")
    parser.add_argument("--skill-root", help="Canonical graduation-project-builder skill root")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    adapter = Path(args.adapter).resolve()
    skill_root = Path(args.skill_root).resolve() if args.skill_root else Path(__file__).resolve().parents[1]
    issues = validate_adapter_file(adapter, skill_root=skill_root)
    result = {
        "adapter": str(adapter),
        "skill_root": str(skill_root),
        "result": "pass" if not issues else "fail",
        "issues": issues,
    }
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print("# Thesis Local Adapter Validation")
        print("")
        print(f"- adapter: {adapter}")
        print(f"- skill root: {skill_root}")
        print(f"- result: {result['result']}")
        print("")
        print("## Issues")
        if issues:
            for issue in issues:
                print(f"- {issue}")
        else:
            print("- none")
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
