#!/usr/bin/env python3
"""Generate a thesis-writing blueprint from a software project."""

from __future__ import annotations

import argparse
from pathlib import Path


def gather_text(root: Path, rels: list[str]) -> str:
    parts: list[str] = []
    for rel in rels:
        path = root / rel
        if path.exists():
            try:
                parts.append(path.read_text(encoding="utf-8", errors="ignore"))
            except Exception:
                pass
    return "\n".join(parts)


def detect_title(root: Path) -> str:
    for rel in ["README.md", "README.txt"]:
        path = root / rel
        if path.exists():
            try:
                first = path.read_text(encoding="utf-8", errors="ignore").splitlines()[0].strip()
                if first.startswith("#"):
                    return first.lstrip("#").strip()
                if first:
                    return first
            except Exception:
                pass
    return root.name


def infer_modules(root: Path) -> list[str]:
    modules: list[str] = []
    for child in root.iterdir():
        if child.is_dir() and child.name not in {"docs", "dist", "build", "target", ".git", "__pycache__", "node_modules"}:
            modules.append(child.name)
    return modules[:12]


def infer_figures(modules: list[str]) -> list[str]:
    figures = [
        "系统总体架构图",
        "系统功能结构图",
    ]
    if any(name in modules for name in ["backend", "app", "server"]):
        figures.append("系统主要业务流程图")
    if any(name in modules for name in ["frontend", "templates", "static"]):
        figures.append("系统主要页面展示图")
    figures.append("数据库设计图或 ER 图")
    figures.append("系统测试结果图或截图")
    return figures


def infer_tables() -> list[str]:
    return [
        "功能需求分析表",
        "数据库主要数据表设计表",
        "测试用例与测试结果表",
    ]


def read_template_skeleton(path: Path | None) -> list[str]:
    if path is None or not path.exists():
        return []
    lines = [line.strip() for line in path.read_text(encoding="utf-8", errors="ignore").splitlines() if line.strip()]
    return [line[2:].strip() for line in lines if line.startswith("- ")]


def build_template_section(template_items: list[str]) -> str:
    if not template_items:
        return "- 待提供模板骨架"
    return "\n".join(f"- {item}" for item in template_items)


def build_markdown(root: Path, template_hint: str | None, template_skeleton_path: Path | None) -> str:
    title = detect_title(root)
    modules = infer_modules(root)
    figures = infer_figures(modules)
    tables = infer_tables()
    context = gather_text(root, ["README.md", "DEPLOYMENT.md", "docs/project-blueprint.md"])
    template_items = read_template_skeleton(template_skeleton_path)

    module_lines = "\n".join(f"- {item}" for item in modules) if modules else "- 待补充"
    figure_lines = "\n".join(f"- {item}" for item in figures)
    table_lines = "\n".join(f"- {item}" for item in tables)
    template_line = template_hint or "待提供"
    template_lines = build_template_section(template_items)

    return f"""# Thesis Blueprint

## Project Title

- {title}

## Template Input

- {template_line}

## Learned Template Skeleton

{template_lines}

## Real Project Modules

{module_lines}

## Recommended Chapter Skeleton

1. 摘要
2. Abstract
3. 第一章 绪论
4. 第二章 系统分析
5. 第三章 系统设计
6. 第四章 系统实现
7. 第五章 系统测试
8. 第六章 总结与展望
9. 参考文献
10. 致谢

## Chapter-to-Project Mapping

- 第一章 绪论：郑州市大型商场数据分析背景、研究意义、国内外研究现状、本文工作内容
- 第二章 系统分析：可行性分析、需求分析、业务流程分析，围绕数据采集、预处理、存储、分析、展示五层结构展开
- 第三章 系统设计：系统架构设计、功能模块设计、数据库设计、接口设计；重点安排图3-x和表3-x
- 第四章 系统实现：开发环境搭建、前端展示实现、后端与数据处理实现、核心代码实现
- 第五章 系统测试：测试环境、功能测试、性能测试、安全性测试、兼容性测试
- 第六章 总结与展望：总结当前实验验证成果，说明未来可扩展到真实数据和更复杂平台

## Chapter 3 Figure/Table Mapping

- 3.1 系统架构设计：系统总体架构图、技术架构图
- 3.2 功能模块设计：原始数据导入流程图、数据预处理流程图、统计分析流程图、可视化展示流程图
- 3.3.1 数据流程分析：DFD 顶层图、DFD 一层图
- 3.3.2 数据字典：数据项定义表、数据结构定义表、数据流定义表、数据存储定义表
- 3.4 接口设计：关键页面或数据接口说明表

## Figure Plan

{figure_lines}

## Table Plan

{table_lines}

## Writing Constraints

- 论文内容必须以真实代码和真实功能为基础
- 如果项目采用轻量化或模拟实现，论文中需要如实写成“实验验证版本”或“演示实现版本”
- 若用户提供模板或样例，必须跟随其标题层级、编号、图表样式和章节顺序

## Repository Context Snapshot

```text
{context[:1500]}
```
"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate a thesis blueprint for a software project.")
    parser.add_argument("--root", default=".", help="Project root")
    parser.add_argument("--template-hint", default=None, help="Template or sample paper hint/path")
    parser.add_argument("--template-skeleton", default=None, help="Path to extracted thesis template skeleton markdown")
    parser.add_argument("--output", default="docs/thesis-blueprint.md")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    output = Path(args.output)
    if not output.is_absolute():
        output = root / output
    output.parent.mkdir(parents=True, exist_ok=True)
    template_skeleton_path = Path(args.template_skeleton) if args.template_skeleton else None
    output.write_text(build_markdown(root, args.template_hint, template_skeleton_path), encoding="utf-8")
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
