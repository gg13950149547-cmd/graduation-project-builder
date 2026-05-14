"""Bundle-level checks for validate_skill_gate."""

from __future__ import annotations

import json
import re
from pathlib import Path

__all__ = ["check_skill_bundle"]

try:
    from .validate_skill_gate_registry_core import (
        FINAL_ACCEPTANCE_SCHEMA,
        FORMAT_REPAIR_TASK_SCHEMA,
        REVIEW_EVIDENCE_SCHEMA,
        TEXT_EXTENSIONS,
    )
    from .validate_skill_gate_registry_bundle import (
        COMPATIBILITY_EXTERNAL_AUDIT_RECORD_DATE,
        COMPATIBILITY_EXTERNAL_AUDIT_SCOPE,
        COMPATIBILITY_EXTERNAL_AUDIT_RECORD,
        COMPATIBILITY_EXTERNAL_RETIREMENT_STATUSES,
        COMPATIBILITY_EXTERNAL_AUDIT_NOTE,
        COMPATIBILITY_RETENTION_TIERS,
        COMPATIBILITY_RETIREMENT_NOTE,
        COMPATIBILITY_ONLY_EXPORTS,
        ACTIVE_SCRIPT_POLICY_ALLOWLIST,
        ACTIVE_SCRIPT_BROAD_REWRITE_PATTERNS,
        DUPLICATE_REGISTRY_NAMES_BY_FILE,
        NUMBERED_RULE_DIRS,
        REQUIRED_FILES,
        REQUIRED_HEADINGS_BY_FILE,
        REQUIRED_RULE_LINES_BY_FILE,
        REQUIRED_VISUAL_FILES,
        RULE_OWNER_MANIFEST,
        ROUTER_FILES,
        SEMANTIC_ONLY_RULE_FILES,
        RETIRED_THICK_THESIS_SCRIPTS,
        SCRIPT_RUNTIME_POLICY_BY_FILE,
        SCRIPT_RUNTIME_FORBIDDEN_TOKENS_BY_FILE,
        SELFTEST_FORBIDDEN_TOKENS,
        SEMANTIC_RULE_GROUPS_BY_FILE,
        SKILL_BOUNDARY_FORBIDDEN_TOKENS,
        SUSPICIOUS_TOKENS,
        USER_FEEDBACK_ROUTER,
    )
    from .validate_skill_gate_utils import find_lines_with_prefix, normalize, normalized_text, read_lines, read_text
except ImportError:
    from validate_skill_gate_registry_core import (
        FINAL_ACCEPTANCE_SCHEMA,
        FORMAT_REPAIR_TASK_SCHEMA,
        REVIEW_EVIDENCE_SCHEMA,
        TEXT_EXTENSIONS,
    )
    from validate_skill_gate_registry_bundle import (
        COMPATIBILITY_EXTERNAL_AUDIT_RECORD_DATE,
        COMPATIBILITY_EXTERNAL_AUDIT_SCOPE,
        COMPATIBILITY_EXTERNAL_AUDIT_RECORD,
        COMPATIBILITY_EXTERNAL_RETIREMENT_STATUSES,
        COMPATIBILITY_EXTERNAL_AUDIT_NOTE,
        COMPATIBILITY_RETENTION_TIERS,
        COMPATIBILITY_RETIREMENT_NOTE,
        COMPATIBILITY_ONLY_EXPORTS,
        ACTIVE_SCRIPT_POLICY_ALLOWLIST,
        ACTIVE_SCRIPT_BROAD_REWRITE_PATTERNS,
        DUPLICATE_REGISTRY_NAMES_BY_FILE,
        NUMBERED_RULE_DIRS,
        REQUIRED_FILES,
        REQUIRED_HEADINGS_BY_FILE,
        REQUIRED_RULE_LINES_BY_FILE,
        REQUIRED_VISUAL_FILES,
        RULE_OWNER_MANIFEST,
        ROUTER_FILES,
        SEMANTIC_ONLY_RULE_FILES,
        RETIRED_THICK_THESIS_SCRIPTS,
        SCRIPT_RUNTIME_POLICY_BY_FILE,
        SCRIPT_RUNTIME_FORBIDDEN_TOKENS_BY_FILE,
        SELFTEST_FORBIDDEN_TOKENS,
        SEMANTIC_RULE_GROUPS_BY_FILE,
        SKILL_BOUNDARY_FORBIDDEN_TOKENS,
        SUSPICIOUS_TOKENS,
        USER_FEEDBACK_ROUTER,
    )
    from validate_skill_gate_utils import find_lines_with_prefix, normalize, normalized_text, read_lines, read_text


TEMPLATE_SCHEMA_POLICIES = (
    {
        "rel_path": "assets/final-acceptance-template.md",
        "label": "final acceptance template",
        "schema": FINAL_ACCEPTANCE_SCHEMA,
        "heading_keys": ("headings", "template_only_headings"),
        "heading_noun": "required marker",
        "single_prefix_keys": ("single_prefixes",),
        "repeated_prefix_keys": ("repeated_prefix_counts",),
    },
    {
        "rel_path": "assets/review-evidence-template.md",
        "label": "review evidence template",
        "schema": REVIEW_EVIDENCE_SCHEMA,
        "heading_keys": ("headings",),
        "heading_noun": "heading",
        "single_prefix_keys": ("single_prefixes",),
        "repeated_prefix_keys": (),
    },
    {
        "rel_path": "assets/format-repair-task-template.md",
        "label": "format-repair template",
        "schema": FORMAT_REPAIR_TASK_SCHEMA,
        "heading_keys": ("headings",),
        "heading_noun": "heading",
        "single_prefix_keys": ("single_prefixes",),
        "repeated_prefix_keys": (),
    },
)

ROUTER_CHILD_PATTERN = re.compile(
    r"^-\s+`(references/[^`]+)`(?:\:\s*(?:rules\s+`([^`]+)`|.*))?$",
    flags=re.M,
)
SKILL_MD_MAX_LINES = 380

COMPATIBILITY_EXPORT_VALUES_BY_NAME = {
    "SCRIPT_RUNTIME_FORBIDDEN_TOKENS_BY_FILE": SCRIPT_RUNTIME_FORBIDDEN_TOKENS_BY_FILE,
    "SEMANTIC_ONLY_RULE_FILES": SEMANTIC_ONLY_RULE_FILES,
}
EXPECTED_COMPATIBILITY_RETENTION_TIERS = {
    "SCRIPT_RUNTIME_FORBIDDEN_TOKENS_BY_FILE": "short-term-required",
    "SEMANTIC_ONLY_RULE_FILES": "conditional-removal-candidate",
}
ALLOWED_EXTERNAL_RETIREMENT_STATUSES_BY_TIER = {
    "short-term-required": {
        "not-applicable-while-short-term-required",
        "pending-external-audit",
    },
    "conditional-removal-candidate": {
        "pending-external-audit",
        "external-callers-retired",
    },
}
REQUIRED_COMPATIBILITY_EXPORT_FIELDS = (
    "kind",
    "active_source",
    "retention_tier",
    "external_retirement_status",
    "external_retirement_evidence",
    "known_direct_local_importers",
    "compatibility_surfaces",
    "retirement_checklist",
    "removal_condition",
)


def is_active_text_file(skill_root: Path, path: Path) -> bool:
    rel = path.relative_to(skill_root).as_posix()
    if rel.startswith("references/archive/"):
        return False
    name = path.name
    if ".bak" in name or ".backup-" in name or "pre-clean" in name:
        return False
    return path.suffix.lower() in TEXT_EXTENSIONS


def check_active_text_health(skill_root: Path) -> list[str]:
    issues: list[str] = []
    for path in skill_root.rglob("*"):
        if not path.is_file():
            continue
        if not is_active_text_file(skill_root, path):
            continue
        rel = path.relative_to(skill_root).as_posix()
        data = path.read_bytes()
        if data.startswith(b"\xef\xbb\xbf"):
            issues.append(f"active text file has UTF-8 BOM: {rel}")
        try:
            text = data.decode("utf-8")
        except UnicodeDecodeError as exc:
            issues.append(f"active text file is not valid UTF-8: {rel} ({exc})")
            continue
        found = [token for token in SUSPICIOUS_TOKENS if token in text]
        if found:
            issues.append(
                f"active text file contains suspicious mojibake tokens: {rel} -> {', '.join(found)}"
            )
    return issues


def check_skill_md_budget(skill_root: Path) -> list[str]:
    skill_path = skill_root / "SKILL.md"
    if not skill_path.exists():
        return []
    line_count = len(read_lines(skill_path))
    if line_count > SKILL_MD_MAX_LINES:
        return [
            f"SKILL.md exceeds structural budget: {line_count} lines > {SKILL_MD_MAX_LINES}; move durable detail into references/"
        ]
    return []


def check_bundle_boundary_rules(skill_root: Path) -> list[str]:
    issues: list[str] = []

    skill_path = skill_root / "SKILL.md"
    if skill_path.exists():
        skill_text = read_text(skill_path)
        for token, owner in SKILL_BOUNDARY_FORBIDDEN_TOKENS.items():
            if token in skill_text:
                issues.append(
                    f"SKILL.md contains execution-layer tool detail '{token}' that belongs in {owner}"
                )

    selftest_path = skill_root / "scripts" / "selftest_skill_flow.py"
    if selftest_path.exists():
        selftest_text = read_text(selftest_path)
        for token, message in SELFTEST_FORBIDDEN_TOKENS.items():
            if token in selftest_text:
                issues.append(message)

    for rel_path, policy in SCRIPT_RUNTIME_POLICY_BY_FILE.items():
        target = skill_root / rel_path
        if not target.exists():
            continue
        text = read_text(target)
        if any(token in text for token in policy["tokens"]):
            issues.append(policy["message"])

    return issues


RETIRED_THICK_THESIS_REFERENCE_EXEMPTIONS = {
    "scripts/selftest_skill_flow.py",
    "scripts/validate_skill_gate_bundle.py",
    "scripts/validate_skill_gate_registry.py",
    "scripts/validate_skill_gate_registry_bundle.py",
}


def check_retired_thick_thesis_scripts(skill_root: Path) -> list[str]:
    issues: list[str] = []
    retired_names = {rel_path: Path(rel_path).name for rel_path in RETIRED_THICK_THESIS_SCRIPTS}
    retired_stems = {rel_path: Path(rel_path).stem for rel_path in RETIRED_THICK_THESIS_SCRIPTS}

    for rel_path, reason in RETIRED_THICK_THESIS_SCRIPTS.items():
        if (skill_root / rel_path).exists():
            issues.append(f"retired thick thesis rewrite helper remains active: {rel_path}; {reason}")

    scripts_dir = skill_root / "scripts"
    if not scripts_dir.exists():
        return issues
    for path in sorted(scripts_dir.glob("*.py")):
        rel = path.relative_to(skill_root).as_posix()
        if rel in RETIRED_THICK_THESIS_REFERENCE_EXEMPTIONS:
            continue
        text = read_text(path)
        for retired_rel, retired_name in retired_names.items():
            retired_stem = retired_stems[retired_rel]
            if retired_name in text or retired_stem in text:
                issues.append(
                    f"active script references retired thick thesis helper {retired_name}: {rel}; {RETIRED_THICK_THESIS_SCRIPTS[retired_rel]}"
                )
    return issues


def check_active_script_policy(skill_root: Path) -> list[str]:
    issues: list[str] = []
    scripts_dir = skill_root / "scripts"
    if not scripts_dir.exists():
        return issues
    for path in sorted(scripts_dir.glob("*.py")):
        rel = path.relative_to(skill_root).as_posix()
        if rel in ACTIVE_SCRIPT_POLICY_ALLOWLIST:
            continue
        text = read_text(path)
        for label, pattern in ACTIVE_SCRIPT_BROAD_REWRITE_PATTERNS.items():
            if re.search(pattern, text):
                issues.append(
                    f"active script violates thesis helper policy ({label}): {rel}; "
                    "move broad DOCX thesis behavior into a bounded canonical helper with an allowlist owner"
                )
        if "ImageDraw" in text and "add_picture(" in text and "figure asset manifest" not in text.lower():
            issues.append(
                f"active script violates thesis figure policy (ImageDraw + add_picture without manifest route): {rel}"
            )
    return issues


def discover_direct_local_importers(skill_root: Path, export_name: str) -> list[str]:
    direct_importers: list[str] = []
    for path in sorted((skill_root / "scripts").glob("*.py")):
        rel_path = path.relative_to(skill_root).as_posix()
        if rel_path == "scripts/validate_skill_gate_registry_bundle.py":
            continue
        text = read_text(path)
        if export_name in text:
            direct_importers.append(rel_path)
    return direct_importers


def render_compatibility_note_list(values: list[str]) -> str:
    return "; ".join(values)


def get_compatibility_external_audit_roots() -> list[Path]:
    home = Path.home()
    return [
        home / ".agents",
        home / ".codex" / "skills",
        home / "Documents" / "Codex",
    ]


def is_compatibility_external_audit_candidate(skill_root: Path, path: Path) -> bool:
    if not path.is_file() or path.suffix.lower() != ".py":
        return False
    try:
        path.relative_to(skill_root)
        return False
    except ValueError:
        pass
    for parent in path.parents:
        if parent.name != "graduation-project-builder":
            continue
        if (parent / "SKILL.md").exists() and (parent / "scripts" / "validate_skill_gate.py").exists():
            return False
    rel = path.as_posix().lower()
    blocked_segments = (
        "/.git/",
        "/node_modules/",
        "/.codex/",
        "/sessions/",
        "/archived_sessions/",
        "/ambient-suggestions/",
    )
    if any(segment in rel for segment in blocked_segments):
        return False
    name = path.name.lower()
    if name.endswith(".bak") or ".bak-" in name or ".backup-" in name:
        return False
    return True


def build_expected_compatibility_note_lines(export_name: str, metadata: dict[str, object]) -> list[str]:
    return [
        f"### {export_name}",
        f"- kind: {metadata['kind']}",
        f"- retention tier: {metadata['retention_tier']}",
        f"- active source: {metadata['active_source']}",
        f"- external caller retirement status: {metadata['external_retirement_status']}",
        f"- external caller retirement evidence: {metadata['external_retirement_evidence']}",
        f"- known direct local importers: {render_compatibility_note_list(metadata['known_direct_local_importers'])}",
        f"- compatibility surfaces: {render_compatibility_note_list(metadata['compatibility_surfaces'])}",
        f"- retirement checklist: {render_compatibility_note_list(metadata['retirement_checklist'])}",
        f"- removal condition: {metadata['removal_condition']}",
    ]


def build_expected_external_audit_note_lines(export_name: str, metadata: dict[str, object]) -> list[str]:
    return [
        f"### {export_name}",
        f"- retention tier at audit time: {metadata['retention_tier']}",
        f"- audited local direct importers: {render_compatibility_note_list(metadata['known_direct_local_importers'])}",
        f"- audited compatibility surfaces: {render_compatibility_note_list(metadata['compatibility_surfaces'])}",
        f"- external caller retirement status: {metadata['external_retirement_status']}",
        f"- external caller retirement evidence: {metadata['external_retirement_evidence']}",
    ]


def build_expected_external_audit_note_preamble_lines() -> list[str]:
    return [
        f"- audit record date: {COMPATIBILITY_EXTERNAL_AUDIT_RECORD_DATE}",
        f"- audit scope: {COMPATIBILITY_EXTERNAL_AUDIT_SCOPE}",
    ]


def discover_external_compatibility_hits(skill_root: Path, export_name: str) -> list[str]:
    hits: list[str] = []
    for root in get_compatibility_external_audit_roots():
        if not root.exists():
            continue
        for path in root.rglob("*.py"):
            if not is_compatibility_external_audit_candidate(skill_root, path):
                continue
            text = read_text(path)
            if export_name in text:
                hits.append(str(path))
    return sorted(dict.fromkeys(hits))


def build_expected_external_audit_record_preamble_lines() -> list[str]:
    return [
        f"- audit record date: {COMPATIBILITY_EXTERNAL_AUDIT_RECORD_DATE}",
        f"- audit scope: {COMPATIBILITY_EXTERNAL_AUDIT_SCOPE}",
        f"- audited code roots: {render_compatibility_note_list([str(path) for path in get_compatibility_external_audit_roots()])}",
    ]


def build_expected_external_audit_record_lines(
    skill_root: Path, export_name: str, metadata: dict[str, object]
) -> list[str]:
    hits = discover_external_compatibility_hits(skill_root, export_name)
    return [
        f"### {export_name}",
        f"- expected external retirement status: {metadata['external_retirement_status']}",
        f"- audited external caller hits: {render_compatibility_note_list(hits) if hits else 'none'}",
        f"- recorded evidence: {metadata['external_retirement_evidence']}",
    ]


def check_compatibility_exports(skill_root: Path) -> list[str]:
    issues: list[str] = []
    note_validated_exports: dict[str, dict[str, object]] = {}
    for export_name, metadata in COMPATIBILITY_ONLY_EXPORTS.items():
        metadata_ok = True
        if export_name not in COMPATIBILITY_EXPORT_VALUES_BY_NAME:
            issues.append(f"compatibility metadata references unknown export: {export_name}")
            continue
        if not isinstance(metadata, dict):
            issues.append(f"compatibility metadata for {export_name} must be a mapping")
            continue
        missing_fields = [field for field in REQUIRED_COMPATIBILITY_EXPORT_FIELDS if not metadata.get(field)]
        if missing_fields:
            issues.append(
                f"compatibility metadata for {export_name} missing required fields: {', '.join(missing_fields)}"
            )
            continue
        retention_tier = metadata["retention_tier"]
        if retention_tier not in COMPATIBILITY_RETENTION_TIERS:
            issues.append(
                f"compatibility metadata for {export_name} uses unknown retention_tier: {retention_tier}"
            )
            continue
        expected_tier = EXPECTED_COMPATIBILITY_RETENTION_TIERS.get(export_name)
        if expected_tier and retention_tier != expected_tier:
            issues.append(
                f"compatibility metadata for {export_name} must use retention_tier {expected_tier}, found {retention_tier}"
            )
            metadata_ok = False
        external_retirement_status = metadata["external_retirement_status"]
        if external_retirement_status not in COMPATIBILITY_EXTERNAL_RETIREMENT_STATUSES:
            issues.append(
                f"compatibility metadata for {export_name} uses unknown external_retirement_status: {external_retirement_status}"
            )
            continue
        allowed_statuses = ALLOWED_EXTERNAL_RETIREMENT_STATUSES_BY_TIER.get(retention_tier, set())
        if external_retirement_status not in allowed_statuses:
            issues.append(
                f"compatibility metadata for {export_name} must use an external_retirement_status allowed for {retention_tier}, found {external_retirement_status}"
            )
            metadata_ok = False
        external_hits = discover_external_compatibility_hits(skill_root, export_name)
        if external_retirement_status == "external-callers-retired" and external_hits:
            issues.append(
                f"compatibility metadata for {export_name} cannot claim external-callers-retired while audited external hits remain: {external_hits}"
            )
            metadata_ok = False
        if not metadata["external_retirement_evidence"]:
            issues.append(
                f"compatibility metadata for {export_name} must provide external_retirement_evidence"
            )
            metadata_ok = False
        recorded_importers = metadata["known_direct_local_importers"]
        if not isinstance(recorded_importers, list):
            issues.append(
                f"compatibility metadata for {export_name} must store known_direct_local_importers as a list"
            )
            continue
        actual_importers = discover_direct_local_importers(skill_root, export_name)
        if recorded_importers != actual_importers:
            issues.append(
                f"compatibility metadata for {export_name} direct importer inventory drift: recorded={recorded_importers} actual={actual_importers}"
            )
            metadata_ok = False
        compatibility_surfaces = metadata["compatibility_surfaces"]
        if not isinstance(compatibility_surfaces, list) or not compatibility_surfaces:
            issues.append(
                f"compatibility metadata for {export_name} must provide at least one compatibility_surfaces entry"
            )
            metadata_ok = False
        else:
            for rel_path in compatibility_surfaces:
                if not (skill_root / rel_path).exists():
                    issues.append(
                        f"compatibility metadata for {export_name} references missing compatibility surface: {rel_path}"
                    )
                    metadata_ok = False
        retirement_checklist = metadata["retirement_checklist"]
        if not isinstance(retirement_checklist, list) or not retirement_checklist:
            issues.append(
                f"compatibility metadata for {export_name} must provide a non-empty retirement_checklist"
            )
            metadata_ok = False

        if metadata_ok:
            note_validated_exports[export_name] = metadata

    note_path = skill_root / COMPATIBILITY_RETIREMENT_NOTE
    if note_path.exists():
        normalized_lines = {normalize(line) for line in read_lines(note_path) if normalize(line)}
        for export_name, metadata in note_validated_exports.items():
            for expected_line in build_expected_compatibility_note_lines(export_name, metadata):
                if normalize(expected_line) not in normalized_lines:
                    issues.append(
                        f"compatibility retirement note missing line for {export_name}: {expected_line}"
                    )

    audit_note_path = skill_root / COMPATIBILITY_EXTERNAL_AUDIT_NOTE
    if audit_note_path.exists():
        normalized_lines = {normalize(line) for line in read_lines(audit_note_path) if normalize(line)}
        for expected_line in build_expected_external_audit_note_preamble_lines():
            if normalize(expected_line) not in normalized_lines:
                issues.append(f"compatibility external audit note missing line: {expected_line}")
        for export_name, metadata in note_validated_exports.items():
            for expected_line in build_expected_external_audit_note_lines(export_name, metadata):
                if normalize(expected_line) not in normalized_lines:
                    issues.append(
                        f"compatibility external audit note missing line for {export_name}: {expected_line}"
                    )

    audit_record_path = skill_root / COMPATIBILITY_EXTERNAL_AUDIT_RECORD
    if audit_record_path.exists():
        normalized_lines = {normalize(line) for line in read_lines(audit_record_path) if normalize(line)}
        for expected_line in build_expected_external_audit_record_preamble_lines():
            if normalize(expected_line) not in normalized_lines:
                issues.append(f"compatibility external audit record missing line: {expected_line}")
        for export_name, metadata in note_validated_exports.items():
            for expected_line in build_expected_external_audit_record_lines(skill_root, export_name, metadata):
                if normalize(expected_line) not in normalized_lines:
                    issues.append(
                        f"compatibility external audit record missing line for {export_name}: {expected_line}"
                    )

    expected_runtime_tokens = {
        rel_path: policy["tokens"] for rel_path, policy in SCRIPT_RUNTIME_POLICY_BY_FILE.items()
    }
    if SCRIPT_RUNTIME_FORBIDDEN_TOKENS_BY_FILE != expected_runtime_tokens:
        issues.append(
            "compatibility export drift: SCRIPT_RUNTIME_FORBIDDEN_TOKENS_BY_FILE must mirror SCRIPT_RUNTIME_POLICY_BY_FILE token lists"
        )
    return issues


def check_semantic_rule_groups(skill_root: Path) -> list[str]:
    issues: list[str] = []
    for rel_path, groups in SEMANTIC_RULE_GROUPS_BY_FILE.items():
        target = skill_root / rel_path
        if not target.exists():
            continue
        text = normalized_text(target)
        for description, tokens in groups:
            if not all(token.lower() in text for token in tokens):
                issues.append(f"missing semantic rule in {rel_path}: {description}")
    return issues


def collect_schema_markers(schema: dict[str, object], keys: tuple[str, ...]) -> list[str]:
    markers: list[str] = []
    for key in keys:
        markers.extend(schema.get(key, []))
    return markers


def check_template_schema_policy(skill_root: Path, policy: dict[str, object]) -> list[str]:
    issues: list[str] = []
    rel_path = str(policy["rel_path"])
    target = skill_root / rel_path
    if not target.exists():
        return issues

    label = str(policy["label"])
    schema = policy["schema"]
    heading_noun = str(policy["heading_noun"])
    heading_keys = tuple(policy["heading_keys"])
    single_prefix_keys = tuple(policy["single_prefix_keys"])
    repeated_prefix_keys = tuple(policy["repeated_prefix_keys"])

    lines = read_lines(target)
    normalized_lines = {normalize(line) for line in lines if normalize(line)}

    for marker in collect_schema_markers(schema, heading_keys):
        if marker not in normalized_lines:
            issues.append(f"{label} missing {heading_noun} '{marker}' in {rel_path}")

    for key in single_prefix_keys:
        for prefix in schema.get(key, []):
            matches = find_lines_with_prefix(lines, prefix)
            if len(matches) != 1:
                issues.append(f"{label} must contain exactly one '{prefix}' line in {rel_path}")

    for key in repeated_prefix_keys:
        for prefix, expected_count in schema.get(key, {}).items():
            matches = find_lines_with_prefix(lines, prefix)
            if len(matches) != expected_count:
                issues.append(
                    f"{label} must contain {expected_count} occurrences of '{prefix}' in {rel_path}"
                )

    return issues


def check_template_schema_files(skill_root: Path) -> list[str]:
    issues: list[str] = []
    for policy in TEMPLATE_SCHEMA_POLICIES:
        issues.extend(check_template_schema_policy(skill_root, policy))
    return issues


def parse_rule_ids(text: str) -> list[str]:
    return re.findall(r"^###\s+([0-9]+[A-Z]?)\.", text, flags=re.M)


def parse_manifest_rule_ids(text: str) -> list[str]:
    return re.findall(r"^###\s+((?:CORE|FMT|QA|EXEC|FB|AGENT)-[A-Z0-9]+-\d{3}[A-Z]?)\.", text, flags=re.M)


RULE_OWNER_ID_PATTERN = re.compile(r"^(?:CORE|FMT|QA|EXEC|FB|AGENT)-[A-Z0-9]+-\d{3}[A-Z]?$")
RULE_ENFORCEMENT_OWNER_FIELDS = (
    "validator_owner",
    "selftest_owner",
    "template_owner",
    "generator_owner",
)
RULE_ENFORCEMENT_COVERAGE_FIELDS = ("validator_owner", "selftest_owner")
REQUIRED_RULE_OWNER_CLOSURES = {
    "EXEC-MAINT-072": {
        "validator_owner": {"scripts/validate_skill_gate_record_gate.py::validate_skill_invocation_lock"},
        "selftest_owner": {
            "scripts/selftest_skill_flow.py::case_explicit_invocation_bootstrap_first_documented_valid",
            "scripts/selftest_skill_flow.py::case_explicit_invocation_bootstrap_non_control_before_lock_rejected",
        },
        "acceptance_fields": {"no non-control action before lock?"},
    },
    "FMT-TOC-002": {
        "validator_owner": {"scripts/audit_toc_rendered_page_sync.py::audit_toc_rendered_page_sync"},
        "selftest_owner": {"scripts/selftest_skill_flow.py::case_toc_rendered_page_sync_mismatch_rejected"},
        "required_keywords": {"scripts/audit_toc_rendered_page_sync.py", "rendered page sync"},
    },
    "FB-LAYOUT-069": {
        "validator_owner": {"scripts/repair_docx_font_alias_slots.py"},
        "selftest_owner": {"scripts/selftest_skill_flow.py::case_font_alias_slots_repair_valid"},
        "required_load_modes": {"thesis-only", "format-repair-only", "skill-maintenance"},
    },
}
RULE_ALLOWED_LOAD_MODES = {
    "program-only",
    "thesis-only",
    "program-plus-thesis",
    "format-repair-only",
    "skill-maintenance",
}
RULE_OWNER_ACCEPTANCE_FIELD_COVERAGE_FILES = (
    "assets/final-acceptance-template.md",
    "assets/agents/agent-run-manifest-template.md",
    "assets/agents/agent-task-card-template.md",
    "scripts/validate_skill_gate_record_core.py",
    "scripts/validate_skill_gate_record_gate.py",
    "scripts/validate_skill_gate_record_evidence.py",
    "scripts/validate_skill_gate_bundle.py",
)
RULE_HEADING_SCAN_DIRS = ("references",)


def normalize_acceptance_field(value: str) -> str:
    return re.sub(r"[^0-9A-Za-z\u4e00-\u9fff]+", "", value).lower()


def acceptance_field_coverage_text(skill_root: Path) -> str:
    chunks: list[str] = []
    for rel_path in RULE_OWNER_ACCEPTANCE_FIELD_COVERAGE_FILES:
        path = skill_root / rel_path
        if path.exists():
            chunks.append(read_text(path))
    return normalize_acceptance_field("\n".join(chunks))


def scan_markdown_rule_headings(skill_root: Path) -> list[tuple[str, str, str]]:
    found: list[tuple[str, str, str]] = []
    for rel_dir in RULE_HEADING_SCAN_DIRS:
        directory = skill_root / rel_dir
        if not directory.exists():
            continue
        for path in sorted(directory.rglob("*.md")):
            rel_path = path.relative_to(skill_root).as_posix()
            for line in read_lines(path):
                match = re.match(r"^###\s+((?:CORE|FMT|QA|EXEC|FB|AGENT)-[A-Z0-9]+-\d{3}[A-Z]?)\b", line)
                if match:
                    found.append((match.group(1), rel_path, normalize(line)))
    return found


def iter_manifest_values(value: object) -> list[object]:
    if isinstance(value, list):
        return value
    if value is None:
        return []
    return [value]


def check_rule_enforcement_owner_ref(
    skill_root: Path,
    *,
    rule_id: str,
    field_name: str,
    value: object,
) -> list[str]:
    issues: list[str] = []
    if not isinstance(value, str) or not value.strip():
        return [f"rule owner manifest entry {rule_id} {field_name} must be a non-empty string"]

    rel_path, _, anchor = value.partition("::")
    rel_path = rel_path.strip()
    anchor = anchor.strip()
    if not rel_path:
        return [f"rule owner manifest entry {rule_id} {field_name} missing path before ::"]
    if Path(rel_path).is_absolute() or ".." in Path(rel_path).parts:
        return [f"rule owner manifest entry {rule_id} {field_name} must be a skill-relative path: {value}"]

    target = skill_root / rel_path
    if not target.exists():
        return [f"rule owner manifest entry {rule_id} {field_name} path missing: {rel_path}"]
    if anchor:
        text = read_text(target)
        if target.suffix.lower() == ".py":
            pattern = re.compile(rf"^(?:def|class)\s+{re.escape(anchor)}\b", flags=re.M)
            if not pattern.search(text):
                issues.append(
                    f"rule owner manifest entry {rule_id} {field_name} anchor not found in {rel_path}: {anchor}"
                )
        elif anchor not in text:
            issues.append(
                f"rule owner manifest entry {rule_id} {field_name} anchor not found in {rel_path}: {anchor}"
            )
    return issues


def check_required_rule_owner_closures(rule_by_id: dict[str, dict[str, object]]) -> list[str]:
    issues: list[str] = []
    for rule_id, requirements in REQUIRED_RULE_OWNER_CLOSURES.items():
        rule = rule_by_id.get(rule_id)
        if not rule:
            issues.append(f"rule owner manifest missing hard-required rule closure: {rule_id}")
            continue
        for field_name, expected_values in requirements.items():
            actual_values = {str(item) for item in iter_manifest_values(rule.get(field_name))}
            missing = sorted(str(value) for value in expected_values if str(value) not in actual_values)
            for value in missing:
                issues.append(f"rule owner manifest entry {rule_id} missing hard-required {field_name}: {value}")
    return issues


def check_rule_owner_manifest(skill_root: Path) -> list[str]:
    issues: list[str] = []
    manifest_path = skill_root / RULE_OWNER_MANIFEST
    if not manifest_path.exists():
        return [f"missing rule owner manifest: {RULE_OWNER_MANIFEST}"]

    try:
        manifest = json.loads(read_text(manifest_path))
    except json.JSONDecodeError as exc:
        return [f"rule owner manifest is not valid JSON: {exc}"]

    rules = manifest.get("rules")
    if not isinstance(rules, list) or not rules:
        return ["rule owner manifest must contain a non-empty rules list"]

    ids: list[str] = []
    rule_by_id: dict[str, dict[str, object]] = {}
    owner_files: set[str] = set()
    acceptance_coverage = acceptance_field_coverage_text(skill_root)
    for index, rule in enumerate(rules):
        if not isinstance(rule, dict):
            issues.append(f"rule owner manifest entry {index} must be an object")
            continue

        rule_id = str(rule.get("id", ""))
        if rule_id:
            rule_by_id[rule_id] = rule
        owner_file = str(rule.get("owner_file", ""))
        heading = str(rule.get("heading", ""))
        router_file = str(rule.get("router_file", ""))
        required_keywords = rule.get("required_keywords", [])
        enforcement_required = rule.get("enforcement_required", False)

        if not RULE_OWNER_ID_PATTERN.match(rule_id):
            issues.append(f"rule owner manifest entry has invalid id: {rule_id}")
        ids.append(rule_id)

        if not owner_file:
            issues.append(f"rule owner manifest entry {rule_id} missing owner_file")
            continue
        owner_files.add(owner_file)
        owner_path = skill_root / owner_file
        if not owner_path.exists():
            issues.append(f"rule owner manifest entry {rule_id} owner_file missing: {owner_file}")
            continue
        owner_text = read_text(owner_path)
        owner_lines = {normalize(line) for line in read_lines(owner_path) if normalize(line)}

        if not heading:
            issues.append(f"rule owner manifest entry {rule_id} missing heading")
        elif normalize(heading) not in owner_lines:
            issues.append(f"rule owner manifest entry {rule_id} heading not found in {owner_file}")

        if not isinstance(required_keywords, list) or not required_keywords:
            issues.append(f"rule owner manifest entry {rule_id} must include required_keywords")
        else:
            owner_norm = owner_text.lower()
            for keyword in required_keywords:
                if not isinstance(keyword, str) or not keyword.strip():
                    issues.append(f"rule owner manifest entry {rule_id} has blank required keyword")
                    continue
                if keyword.lower() not in owner_norm:
                    issues.append(
                        f"rule owner manifest entry {rule_id} required keyword not found in {owner_file}: {keyword}"
                    )

        if router_file:
            router_path = skill_root / router_file
            if not router_path.exists():
                issues.append(f"rule owner manifest entry {rule_id} router_file missing: {router_file}")
            else:
                router_text = read_text(router_path)
                if owner_file not in router_text:
                    issues.append(
                        f"rule owner manifest entry {rule_id} owner file is not exposed by router {router_file}: {owner_file}"
                    )
                if RULE_OWNER_MANIFEST not in router_text:
                    issues.append(
                        f"rule owner manifest entry {rule_id} router {router_file} does not reference {RULE_OWNER_MANIFEST}"
                    )
                router_anchor = str(rule.get("router_anchor", "")).strip()
                if enforcement_required and not router_anchor:
                    issues.append(f"rule owner manifest entry {rule_id} enforcement_required needs router_anchor")
                elif router_anchor and normalize(router_anchor) not in {
                    normalize(line) for line in router_text.splitlines() if normalize(line)
                }:
                    issues.append(
                        f"rule owner manifest entry {rule_id} router_anchor not found in {router_file}: {router_anchor}"
                    )

        if enforcement_required is not False and enforcement_required is not True:
            issues.append(f"rule owner manifest entry {rule_id} enforcement_required must be true or false")
        if enforcement_required:
            if not any(rule.get(field) for field in RULE_ENFORCEMENT_COVERAGE_FIELDS):
                issues.append(
                    f"rule owner manifest entry {rule_id} enforcement_required needs validator_owner or selftest_owner"
                )
            if not rule.get("required_load_modes"):
                issues.append(f"rule owner manifest entry {rule_id} enforcement_required needs required_load_modes")
        for field_name in RULE_ENFORCEMENT_OWNER_FIELDS:
            for owner_ref in iter_manifest_values(rule.get(field_name)):
                issues.extend(
                    check_rule_enforcement_owner_ref(
                        skill_root,
                        rule_id=rule_id,
                        field_name=field_name,
                        value=owner_ref,
                    )
                )
        load_modes = rule.get("required_load_modes", [])
        if load_modes:
            if not isinstance(load_modes, list):
                issues.append(f"rule owner manifest entry {rule_id} required_load_modes must be a list")
            else:
                for mode in load_modes:
                    if mode not in RULE_ALLOWED_LOAD_MODES:
                        issues.append(
                            f"rule owner manifest entry {rule_id} has unknown required_load_modes value: {mode}"
                        )
        acceptance_fields = rule.get("acceptance_fields", [])
        if acceptance_fields:
            if not isinstance(acceptance_fields, list):
                issues.append(f"rule owner manifest entry {rule_id} acceptance_fields must be a list")
            elif any(not isinstance(item, str) or not item.strip() for item in acceptance_fields):
                issues.append(f"rule owner manifest entry {rule_id} acceptance_fields must contain non-empty strings")
            else:
                for item in acceptance_fields:
                    if normalize_acceptance_field(item) not in acceptance_coverage:
                        issues.append(
                            f"rule owner manifest entry {rule_id} acceptance_field is not covered by templates or validators: {item}"
                        )

    duplicate_ids = sorted({rule_id for rule_id in ids if ids.count(rule_id) > 1})
    if duplicate_ids:
        issues.append(f"rule owner manifest has duplicate active rule ids: {', '.join(duplicate_ids)}")
    issues.extend(check_required_rule_owner_closures(rule_by_id))

    mapped_ids = set(ids)
    for found_id, owner_file, heading in scan_markdown_rule_headings(skill_root):
        if found_id not in mapped_ids:
            issues.append(
                f"rule owner manifest missing entry for markdown rule {found_id} in {owner_file}: {heading}"
            )

    for owner_file in sorted(owner_files):
        owner_path = skill_root / owner_file
        if not owner_path.exists():
            continue
        legacy_ids = parse_rule_ids(read_text(owner_path))
        if legacy_ids:
            issues.append(
                f"manifest-owned rule file still uses legacy numeric rule headings: {owner_file} -> {', '.join(legacy_ids)}"
            )

    return issues


def check_duplicate_rule_ids(skill_root: Path) -> list[str]:
    issues: list[str] = []
    for rel_dir in NUMBERED_RULE_DIRS:
        directory = skill_root / rel_dir
        if not directory.exists():
            continue
        for path in sorted(directory.glob("*.md")):
            ids = parse_rule_ids(read_text(path))
            duplicates = sorted({rule_id for rule_id in ids if ids.count(rule_id) > 1})
            if duplicates:
                rel = path.relative_to(skill_root).as_posix()
                issues.append(f"duplicate numbered rules in {rel}: {', '.join(duplicates)}")
    return issues


def check_duplicate_registry_keys(skill_root: Path) -> list[str]:
    issues: list[str] = []
    for filename, registry_names in DUPLICATE_REGISTRY_NAMES_BY_FILE.items():
        registry_path = skill_root / "scripts" / filename
        if not registry_path.exists():
            issues.append(f"validator registry file missing: {filename}")
            continue
        text = read_text(registry_path)
        for registry_name in registry_names:
            block = extract_registry_block(text, registry_name)
            if block is None:
                issues.append(f"validator registry missing: {registry_name}")
                continue
            keys = re.findall(r'^\s*[\'"]([^\'"]+)[\'"]:\s+\[', block, flags=re.M)
            duplicates = sorted({key for key in keys if keys.count(key) > 1})
            if duplicates:
                issues.append(
                    f"validator registry has duplicate keys in {registry_name}: {', '.join(duplicates)}"
                )

    return issues


def extract_registry_block(text: str, registry_name: str) -> str | None:
    marker = f"{registry_name} = {{"
    start = text.find(marker)
    if start < 0:
        return None
    pos = start + len(marker)
    depth = 1
    while pos < len(text) and depth > 0:
        ch = text[pos]
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
        pos += 1
    return text[start:pos]


def expand_rule_spec(spec: str) -> set[str]:
    expanded: set[str] = set()
    for raw_part in spec.split(","):
        part = raw_part.strip()
        if not part:
            continue
        if "-" in part:
            start, end = [x.strip() for x in part.split("-", 1)]
            if start.isdigit() and end.isdigit():
                for value in range(int(start), int(end) + 1):
                    expanded.add(str(value))
                continue
            start_alpha = re.fullmatch(r"(\d+)([A-Z])", start)
            end_alpha = re.fullmatch(r"(\d+)([A-Z])", end)
            if start_alpha and end_alpha and start_alpha.group(1) == end_alpha.group(1):
                prefix = start_alpha.group(1)
                start_ord = ord(start_alpha.group(2))
                end_ord = ord(end_alpha.group(2))
                if start_ord <= end_ord:
                    for code in range(start_ord, end_ord + 1):
                        expanded.add(f"{prefix}{chr(code)}")
                    continue
        expanded.add(part)
    return expanded


def parse_router_child_entries(text: str) -> list[tuple[str, str]]:
    return ROUTER_CHILD_PATTERN.findall(text)


def check_router_child_entries(skill_root: Path, rel_path: str) -> list[str]:
    issues: list[str] = []
    router = skill_root / rel_path
    if not router.exists():
        return issues

    matches = parse_router_child_entries(read_text(router))
    if not matches:
        issues.append(f"router has no child-file entries: {rel_path}")
        return issues

    for child_rel, _rule_spec in matches:
        if not (skill_root / child_rel).exists():
            issues.append(f"router child file missing from {rel_path}: {child_rel}")
    return issues


def sort_rule_ids(rule_ids: set[str]) -> list[str]:
    return sorted(rule_ids, key=lambda x: (len(x), x))


def check_user_feedback_router_coverage(skill_root: Path) -> list[str]:
    issues: list[str] = []
    router = skill_root / USER_FEEDBACK_ROUTER
    if not router.exists():
        return issues

    for child_rel, rule_spec in parse_router_child_entries(read_text(router)):
        if not rule_spec:
            continue
        child = skill_root / child_rel
        if not child.exists():
            continue
        file_rule_ids = set(parse_manifest_rule_ids(read_text(child)))
        referenced_ids = expand_rule_spec(rule_spec)
        missing = sort_rule_ids(referenced_ids - file_rule_ids)
        uncovered = sort_rule_ids(file_rule_ids - referenced_ids)
        if missing:
            issues.append(
                f"user-feedback router references missing rule ids in {child_rel}: {', '.join(missing)}"
            )
        if uncovered:
            issues.append(
                f"user-feedback router does not cover rule ids in {child_rel}: {', '.join(uncovered)}"
            )

    return issues


def check_router_integrity(skill_root: Path) -> list[str]:
    issues: list[str] = []
    for rel_path in ROUTER_FILES:
        issues.extend(check_router_child_entries(skill_root, rel_path))
    issues.extend(check_user_feedback_router_coverage(skill_root))
    return issues


def check_skill_bundle(skill_root: Path) -> list[str]:
    issues: list[str] = []
    for rel_path in REQUIRED_FILES + REQUIRED_VISUAL_FILES:
        if not (skill_root / rel_path).exists():
            issues.append(f"missing required file: {rel_path}")

    for rel_path, required_headings in REQUIRED_HEADINGS_BY_FILE.items():
        target = skill_root / rel_path
        if not target.exists():
            continue
        target_lines = read_lines(target)
        for heading in required_headings:
            if heading not in target_lines:
                issues.append(f"missing required heading in {rel_path}: {heading}")

    for rel_path, required_lines in REQUIRED_RULE_LINES_BY_FILE.items():
        target = skill_root / rel_path
        if not target.exists():
            continue
        normalized_lines = {normalize(line) for line in read_lines(target) if normalize(line)}
        for rule_line in required_lines:
            if normalize(rule_line) not in normalized_lines:
                issues.append(f"missing required rule line in {rel_path}: {rule_line}")

    issues.extend(check_active_text_health(skill_root))
    issues.extend(check_skill_md_budget(skill_root))
    issues.extend(check_bundle_boundary_rules(skill_root))
    issues.extend(check_retired_thick_thesis_scripts(skill_root))
    issues.extend(check_active_script_policy(skill_root))
    issues.extend(check_compatibility_exports(skill_root))
    issues.extend(check_semantic_rule_groups(skill_root))
    issues.extend(check_template_schema_files(skill_root))
    issues.extend(check_rule_owner_manifest(skill_root))
    issues.extend(check_duplicate_rule_ids(skill_root))
    issues.extend(check_duplicate_registry_keys(skill_root))
    issues.extend(check_router_integrity(skill_root))
    return issues
