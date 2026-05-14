#!/usr/bin/env python3
"""Regenerate validate_skill_gate split registry files with ASCII-safe literals."""

from __future__ import annotations

import importlib.util
from pathlib import Path

try:
    from .generate_compatibility_export_notes import regenerate_notes
except ImportError:
    from generate_compatibility_export_notes import regenerate_notes


ROOT = Path(__file__).resolve().parent
TARGETS = [
    "validate_skill_gate_registry_core.py",
    "validate_skill_gate_registry_bundle.py",
    "validate_skill_gate_registry_records.py",
]
QUAD_QUESTION_MARK = "?" * 4


def load_module(path: Path):
    spec = importlib.util.spec_from_file_location(path.stem, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"could not load module from {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def render_string(value: str) -> str:
    if QUAD_QUESTION_MARK not in value:
        return ascii(value)

    parts: list[str] = []
    remaining = value
    while QUAD_QUESTION_MARK in remaining:
        prefix, remaining = remaining.split(QUAD_QUESTION_MARK, 1)
        if prefix:
            parts.append(ascii(prefix))
        parts.append("'?' * 4")
    if remaining:
        parts.append(ascii(remaining))
    return " + ".join(parts) if parts else "''"


def render(value, indent: int = 0) -> str:
    pad = " " * indent
    child = " " * (indent + 4)

    if isinstance(value, str):
        return render_string(value)
    if value is None or isinstance(value, (bool, int, float)):
        return repr(value)
    if isinstance(value, list):
        if not value:
            return "[]"
        items = [f"{child}{render(item, indent + 4)}," for item in value]
        return "[\n" + "\n".join(items) + "\n" + pad + "]"
    if isinstance(value, tuple):
        if not value:
            return "()"
        items = [f"{child}{render(item, indent + 4)}," for item in value]
        return "(\n" + "\n".join(items) + "\n" + pad + ")"
    if isinstance(value, set):
        if not value:
            return "set()"
        items = [f"{child}{render(item, indent + 4)}," for item in sorted(value, key=ascii)]
        return "{\n" + "\n".join(items) + "\n" + pad + "}"
    if isinstance(value, dict):
        if not value:
            return "{}"
        items = []
        for key, item in value.items():
            items.append(f"{child}{render(key, indent + 4)}: {render(item, indent + 4)},")
        return "{\n" + "\n".join(items) + "\n" + pad + "}"

    raise TypeError(f"unsupported value type: {type(value)!r}")


def regenerate_registry(path: Path) -> None:
    module = load_module(path)
    names = list(getattr(module, "__all__", []))
    lines = [
        '"""Registry constants for validate_skill_gate."""',
        "",
        "from __future__ import annotations",
        "",
        f"__all__ = {render(names)}",
        "",
    ]
    for name in names:
        lines.append(f"{name} = {render(getattr(module, name))}")
        lines.append("")
    text = "\n".join(lines)
    text.encode("ascii")
    path.write_text(text, encoding="utf-8")


def main() -> int:
    for filename in TARGETS:
        regenerate_registry(ROOT / filename)
    regenerate_notes()
    print("validate gate registries regenerated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
