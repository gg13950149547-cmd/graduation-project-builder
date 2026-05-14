#!/usr/bin/env python3
"""Validate the graduation-project-builder skill bundle and acceptance gate."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

try:
    from .validate_skill_gate_bundle import check_skill_bundle
    from .validate_skill_gate_records import check_gate_record
except ImportError:
    from validate_skill_gate_bundle import check_skill_bundle
    from validate_skill_gate_records import check_gate_record


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the graduation-project-builder bundle and acceptance gate."
    )
    default_root = Path(__file__).resolve().parents[1]
    parser.add_argument("--skill-root", default=str(default_root), help="Skill root path")
    parser.add_argument(
        "--gate-record",
        help="Optional acceptance record generated from assets/final-acceptance-template.md",
    )
    args = parser.parse_args()

    skill_root = Path(args.skill_root).resolve()
    issues = check_skill_bundle(skill_root)
    if args.gate_record:
        issues.extend(check_gate_record(Path(args.gate_record).resolve()))

    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

    if issues:
        print("SKILL GATE FAILED")
        for issue in issues:
            print(f"- {issue}")
        return 1

    if args.gate_record:
        print("SKILL GATE PASSED")
    else:
        print("SKILL BUNDLE GATE PASSED")
    print(f"- skill root: {skill_root}")
    if args.gate_record:
        print(f"- gate record: {Path(args.gate_record).resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
