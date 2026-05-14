#!/usr/bin/env python3
"""Shared Python runtime helpers for graduation-project-builder scripts."""

from __future__ import annotations

import sys
from pathlib import Path


def resolve_python_exe(
    *,
    error_type: type[Exception] = RuntimeError,
    message: str = "current Python interpreter path is unavailable",
) -> Path:
    current = Path(sys.executable).resolve() if sys.executable else None
    if current and current.exists():
        return current
    raise error_type(message)
