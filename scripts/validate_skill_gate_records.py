"""Compatibility aggregator for record checks in validate_skill_gate."""

from __future__ import annotations

__all__ = [
    "validate_gate_single_prefix",
    "detect_format_repair_surfaces",
    "detect_review_evidence_surfaces",
    "check_thesis_citation_audit_report",
    "check_docx_font_audit_report",
    "format_repair_task_touches_surface",
    "check_format_repair_task_record",
    "check_review_evidence_record",
    "check_effective_font_evidence_record",
    "check_gate_record",
]

try:
    from .validate_skill_gate_record_core import *
    from .validate_skill_gate_record_format import *
    from .validate_skill_gate_record_evidence import *
    from .validate_skill_gate_record_gate import *
except ImportError:
    from validate_skill_gate_record_core import *
    from validate_skill_gate_record_format import *
    from validate_skill_gate_record_evidence import *
    from validate_skill_gate_record_gate import *
