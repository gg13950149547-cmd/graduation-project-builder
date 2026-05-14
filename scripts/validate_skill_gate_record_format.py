"""Format-repair task checks for validate_skill_gate."""

from __future__ import annotations

__all__ = ["check_format_repair_task_record"]

from pathlib import Path

try:
    from .validate_skill_gate_registry_core import EXPLICIT_VALUES, FORMAT_REPAIR_TASK_SCHEMA, TEXT_EVIDENCE_EXTENSIONS
    from .validate_skill_gate_registry_records import (
        ABSTRACT_SURFACE_TOKENS,
        FORMAT_REPAIR_TASK_EXPLICIT_OR_NONE_PREFIXES,
        FORMAT_REPAIR_TASK_EXPLICIT_REQUIRED_PREFIXES,
        FORMAT_REPAIR_TASK_HELPER_LOCK_PREFIXES,
        FORMAT_REPAIR_TASK_PATH_OPTIONAL_FILE_PREFIXES,
        FORMAT_REPAIR_TASK_PATH_VALIDATION_PREFIXES,
        FORMAT_REPAIR_TASK_SURFACE_REQUIRED_PREFIXES,
    )
    from .validate_skill_gate_record_core import (
        check_thesis_citation_audit_report,
        detect_format_repair_surfaces,
        validate_project_local_helper_preflight_fields,
        validate_template_lock_fields,
    )
    from .validate_skill_gate_utils import (
        append_missing_explicit_prefix_issues,
        contains_any,
        find_lines_with_prefix,
        is_explicit,
        is_explicit_none,
        is_explicit_or_none,
        normalize,
        parse_line_value,
        raw_line_value,
        read_lines,
        resolve_record_path,
        split_path_values,
        validate_existing_path,
    )
except ImportError:
    from validate_skill_gate_registry_core import EXPLICIT_VALUES, FORMAT_REPAIR_TASK_SCHEMA, TEXT_EVIDENCE_EXTENSIONS
    from validate_skill_gate_registry_records import (
        ABSTRACT_SURFACE_TOKENS,
        FORMAT_REPAIR_TASK_EXPLICIT_OR_NONE_PREFIXES,
        FORMAT_REPAIR_TASK_EXPLICIT_REQUIRED_PREFIXES,
        FORMAT_REPAIR_TASK_HELPER_LOCK_PREFIXES,
        FORMAT_REPAIR_TASK_PATH_OPTIONAL_FILE_PREFIXES,
        FORMAT_REPAIR_TASK_PATH_VALIDATION_PREFIXES,
        FORMAT_REPAIR_TASK_SURFACE_REQUIRED_PREFIXES,
    )
    from validate_skill_gate_record_core import (
        check_thesis_citation_audit_report,
        detect_format_repair_surfaces,
        validate_project_local_helper_preflight_fields,
        validate_template_lock_fields,
    )
    from validate_skill_gate_utils import (
        append_missing_explicit_prefix_issues,
        contains_any,
        find_lines_with_prefix,
        is_explicit,
        is_explicit_none,
        is_explicit_or_none,
        normalize,
        parse_line_value,
        raw_line_value,
        read_lines,
        resolve_record_path,
        split_path_values,
        validate_existing_path,
    )


NON_PROMOTION_TOKENS = {
    "candidate-only",
    "candidate only",
    "audit-only",
    "audit only",
    "blocked",
    "not promoted",
    "not-promoted",
    "unverified",
    "unresolved",
    "stale",
    "pending",
    "not baseline",
    "not a baseline",
}


def _pass_shaped(value: str) -> bool:
    lowered = normalize(value).lower()
    return "pass" in lowered and not contains_any(
        lowered,
        {"fail", "failed", "missing", "not checked", "pending", "blocked", "unresolved", "drift"},
    )


def check_format_repair_task_record(task_path: Path) -> list[str]:
    issues: list[str] = []
    issues.extend(validate_existing_path(task_path, require_nonempty_file=True))
    if issues:
        return issues
    if task_path.suffix.lower() not in TEXT_EVIDENCE_EXTENSIONS:
        return [f"format-repair task record must be a text file (.md or .txt): {task_path}"]

    try:
        lines = read_lines(task_path)
    except UnicodeDecodeError as exc:
        return [f"format-repair task record is not valid UTF-8: {task_path} ({exc})"]

    normalized_lines = {normalize(line) for line in lines if normalize(line)}
    for heading in FORMAT_REPAIR_TASK_SCHEMA["headings"]:
        if heading not in normalized_lines:
            issues.append(f"format-repair task record missing heading in {task_path}: {heading}")

    for prefix in FORMAT_REPAIR_TASK_SCHEMA["single_prefixes"]:
        matched = find_lines_with_prefix(lines, prefix)
        if len(matched) != 1:
            issues.append(
                f"format-repair task record must contain exactly one '{prefix}' line: {task_path}"
            )

    if issues:
        return issues

    values = {
        prefix: parse_line_value(find_lines_with_prefix(lines, prefix)[0])
        for prefix in FORMAT_REPAIR_TASK_SCHEMA["single_prefixes"]
    }
    raw_values = {
        prefix: raw_line_value(find_lines_with_prefix(lines, prefix)[0])
        for prefix in FORMAT_REPAIR_TASK_SCHEMA["single_prefixes"]
    }

    issues.extend(
        validate_template_lock_fields(
            record_path=task_path,
            values=values,
            raw_values=raw_values,
            record_kind="format-repair task record",
            explicit_source_text=raw_values.get("- explicit user rule:", ""),
        )
    )

    for prefix in FORMAT_REPAIR_TASK_EXPLICIT_REQUIRED_PREFIXES:
        if prefix == "- canonical source restart required?:":
            empty_value = not is_explicit(values[prefix]) or (
                values[prefix] in EXPLICIT_VALUES and values[prefix] != "no"
            )
        else:
            empty_value = not is_explicit(values[prefix]) or values[prefix] in EXPLICIT_VALUES
        if empty_value:
            issues.append(
                f"format-repair task record field must not be empty in {task_path}: {prefix}"
            )

    for prefix in FORMAT_REPAIR_TASK_EXPLICIT_OR_NONE_PREFIXES:
        if not is_explicit_or_none(values[prefix]):
            issues.append(
                f"format-repair task record field is incomplete in {task_path}: {prefix}"
            )

    surface_flags = detect_format_repair_surfaces(values, raw_values)
    toc_touched = surface_flags["toc"]
    table_touched = surface_flags["table"]
    tail_block_touched = surface_flags["tail_block"]
    abstract_touched = surface_flags["abstract"]
    caption_touched = surface_flags["caption"]
    header_footer_touched = surface_flags["header_footer"]
    runtime_screenshot_touched = surface_flags["runtime_screenshot"]
    heading_touched = surface_flags["heading"]
    style_blast_radius_touched = surface_flags.get("style_blast_radius", False)
    pagination_context = "\n".join(
        raw_values[prefix]
        for prefix in (
            "- touched blocks this round:",
            "- specific format classes to verify:",
            "- explicit user rule:",
            "- helper scripts planned this round:",
            "- rendered pages to inspect:",
        )
    )
    whole_pagination_required = (
        toc_touched
        or tail_block_touched
        or header_footer_touched
        or heading_touched
        or style_blast_radius_touched
        or contains_any(
            pagination_context.lower(),
            {
                "pagination",
                "page flow",
                "page number",
                "section break",
                "section boundary",
                "field refresh",
                "toc page",
                "whole thesis",
                "whole-paper",
                "full-paper",
                "full thesis",
                "\u5206\u9875",
                "\u9875\u7801",
                "\u76ee\u5f55",
                "\u5206\u8282",
                "\u5168\u6587",
            },
        )
    )

    helper_planned = values["- helper scripts planned this round:"]
    helper_preflight_summary = values["- project-local helper script preflight summary:"]
    helper_preflight_report = values["- project-local helper preflight report path:"]
    helper_risk_count = values["- project-local helper risk count:"]
    helper_disposition = values["- project-local helper disposition:"]
    canonical_restart_required = values["- canonical source restart required?:"]
    contaminated_disposition = values["- contaminated-baseline disposition:"]
    issues.extend(
        validate_project_local_helper_preflight_fields(
            record_path=task_path,
            values=values,
            raw_values=raw_values,
            record_kind="format-repair task record",
            task_mode=values["- task mode:"],
        )
    )
    if helper_planned in EXPLICIT_VALUES or not is_explicit(helper_planned):
        issues.append(f"format-repair task record must name helper scripts planned this round: {task_path}")
    else:
        append_missing_explicit_prefix_issues(
            values=values,
            prefixes=FORMAT_REPAIR_TASK_HELPER_LOCK_PREFIXES,
            issues=issues,
            location=task_path,
            message="format-repair task record must lock helper-script target / ownership / smoke-audit data when helper scripts are planned",
        )
    if contains_any(helper_preflight_summary, {"failed", "contaminated", "thick", "risky project-local"}):
        completed_restart = (
            helper_disposition == "clean-source-restart-completed"
            or canonical_restart_required in {"completed", "clean-source-restart-completed"}
        )
        if completed_restart:
            if helper_disposition != "clean-source-restart-completed":
                issues.append(
                    f"format-repair task record project-local helper disposition must be clean-source-restart-completed when restart is completed: {task_path}"
                )
            if canonical_restart_required not in {"completed", "clean-source-restart-completed"}:
                issues.append(
                    f"format-repair task record canonical source restart status must be completed when restart is completed: {task_path}"
                )
            if not contains_any(contaminated_disposition, {"completed", "clean source", "clean-source", "not used"}):
                issues.append(
                    f"format-repair task record must record completed clean-source restart and non-use of contaminated helpers: {task_path}"
                )
        elif helper_disposition not in {"audit-only", "clean-source-restart-required"}:
            issues.append(
                f"format-repair task record project-local helper disposition must be audit-only or clean-source-restart-required when risky project-local thesis helper scripts were detected: {task_path}"
            )
        if not completed_restart and canonical_restart_required not in {"yes", "required", "clean-source-restart-required"}:
            issues.append(
                f"format-repair task record canonical source restart must be required when risky project-local thesis helper scripts were detected: {task_path}"
            )
        if not contains_any(contaminated_disposition, {"restart", "clean source", "clean-source", "audit-only", "blocked", "completed", "not used"}):
            issues.append(
                f"format-repair task record must require clean-source restart or audit-only when risky project-local thesis helper scripts were detected: {task_path}"
            )
    elif (
        helper_risk_count == "0"
        and "not-applicable" not in helper_preflight_report
        and contains_any(contaminated_disposition, {"restart", "clean source", "clean-source", "audit-only", "blocked"})
    ):
        issues.append(
            f"format-repair task record contamination disposition conflicts with a clean project-local helper preflight: {task_path}"
        )

    baseline_promotion_gate = values["- baseline promotion gate:"]
    release_blocker_ledger_path = values["- release blocker ledger path:"]
    unresolved_release_blocker_count = values["- unresolved release blocker count:"]
    scoped_next_baseline_verdict = values["- scoped artifact next-baseline verdict:"]
    if not unresolved_release_blocker_count.isdigit():
        issues.append(
            f"format-repair task record unresolved release blocker count must be a nonnegative integer: {task_path}"
        )
    elif int(unresolved_release_blocker_count) > 0 and _pass_shaped(baseline_promotion_gate):
        issues.append(
            f"format-repair task record cannot close baseline promotion while unresolved release blockers remain: {task_path}"
        )
    if _pass_shaped(baseline_promotion_gate):
        if not is_explicit(release_blocker_ledger_path) or is_explicit_none(release_blocker_ledger_path):
            issues.append(
                f"format-repair task record release blocker ledger path is required for baseline promotion: {task_path}"
            )
        if not _pass_shaped(scoped_next_baseline_verdict) or contains_any(scoped_next_baseline_verdict, NON_PROMOTION_TOKENS):
            issues.append(
                f"format-repair task record scoped artifact next-baseline verdict blocks baseline promotion: {task_path}"
            )
        helper_risky = (
            helper_risk_count.isdigit()
            and int(helper_risk_count) > 0
            or contains_any(helper_preflight_summary, {"failed", "contaminated", "thick", "risky project-local"})
        )
        completed_restart = (
            helper_disposition == "clean-source-restart-completed"
            or canonical_restart_required in {"completed", "clean-source-restart-completed"}
        )
        if helper_risky and not completed_restart:
            issues.append(
                f"format-repair task record baseline promotion must be blocked until clean-source restart completes when risky project-local helpers are detected: {task_path}"
            )

    active_references = values["- active references:"]
    routed_child_files = values["- routed child files:"]
    if is_explicit(active_references) and "SKILL.md" in raw_values["- active references:"]:
        if routed_child_files in EXPLICIT_VALUES or not is_explicit(routed_child_files):
            issues.append(
                f"format-repair task record must name routed child files when thesis work is being executed under graduation-project-builder: {task_path}"
            )

    smoke_rule = values["- post-script smoke-audit rule active?:"]
    if smoke_rule not in {"yes", "active"}:
        issues.append(f"format-repair task record must explicitly activate post-script smoke-audit: {task_path}")
    if values["- custom/builder/default font usage allowed?:"] != "no":
        issues.append(
            f"format-repair task record must reject custom/builder/default fonts for thesis template-owned surfaces: {task_path}"
        )
    effective_font_required = values["- effective font chain baseline required?:"]
    if effective_font_required not in {"yes", "required", "active"}:
        issues.append(
            f"format-repair task record must require effective font-chain baseline resolution: {task_path}"
        )
    theme_alias_policy = values["- theme/default font alias policy:"]
    if not contains_any(theme_alias_policy, {"reject", "baseline", "explicit template"}) or contains_any(
        theme_alias_policy,
        {"always allow", "allowed by default", "ignore"},
    ):
        issues.append(
            f"format-repair task record must reject theme/default font aliases unless the locked baseline proves the same alias: {task_path}"
        )

    if toc_touched:
        append_missing_explicit_prefix_issues(
            values=values,
            prefixes=FORMAT_REPAIR_TASK_SURFACE_REQUIRED_PREFIXES["toc"]["prefixes"],
            issues=issues,
            location=task_path,
            message=FORMAT_REPAIR_TASK_SURFACE_REQUIRED_PREFIXES["toc"]["message"],
        )

    if whole_pagination_required:
        append_missing_explicit_prefix_issues(
            values=values,
            prefixes=(
                "- whole-document pagination surface active?:",
                "- whole-document pagination baseline source:",
                "- package baseline manifest path:",
                "- pre-mutation page map path:",
                "- section break numbering baseline path:",
                "- page-number restart baseline path:",
                "- header/footer link-to-previous baseline path:",
                "- hard page-break / section-break baseline path:",
                "- field-refresh baseline state:",
                "- TOC-to-heading page sync baseline path:",
                "- logical-physical page map baseline path:",
                "- rendered page count baseline:",
                "- blank-page scan baseline path:",
                "- whole-document pagination evidence record path:",
                "- package drift report path:",
                "- post-mutation page map path:",
                "- whole-document pagination diff path:",
                "- section break numbering map path:",
                "- chapter start owner map path:",
                "- tail-block owner map path:",
                "- TOC-to-heading page sync map path:",
                "- logical-physical page map path:",
                "- blank-page scan evidence path:",
                "- whole-document pagination checkpoints:",
                "- whole-document pagination verdict:",
            ),
            issues=issues,
            location=task_path,
            message="format-repair task record must lock whole-document pagination evidence when pagination-sensitive surfaces are touched",
        )

    sample_targets_value = values["- page-class sample comparison targets:"]
    if sample_targets_value in EXPLICIT_VALUES or not is_explicit(sample_targets_value):
        issues.append(
            f"format-repair task record must lock page-class sample comparison targets: {task_path}"
        )
    else:
        full_alignment_context = "\n".join(
            raw_values[prefix]
            for prefix in (
                "- explicit user rule:",
                "- touched blocks this round:",
                "- specific format classes to verify:",
            )
        )
        if contains_any(
            full_alignment_context,
            {
                "1:1",
                "whole thesis",
                "whole-paper",
                "full-paper",
                "full thesis",
                "template alignment",
                "template-aligned",
                "整篇",
                "全篇",
                "整篇论文",
                "全篇论文",
                "模板对齐",
            },
        ):
            sample_targets_lower = sample_targets_value.lower()
            required_targets = {
                "cover": "cover",
                "chinese abstract": "Chinese abstract",
                "english abstract": "English abstract",
                "toc": "TOC",
                "references": "references",
                "acknowledgement": "acknowledgement",
            }
            missing_targets = [
                label for token, label in required_targets.items()
                if token not in sample_targets_lower
            ]
            if missing_targets:
                issues.append(
                    f"format-repair task record narrows a full-template-alignment run but omits required page-class targets in {task_path}: {', '.join(missing_targets)}"
                )

    if runtime_screenshot_touched:
        value = values["- runtime screenshot route-caption-asset map path:"]
        if value in EXPLICIT_VALUES or not is_explicit(value):
            issues.append(
                f"format-repair task record must lock a runtime screenshot route-caption-asset map when runtime screenshots are touched: {task_path}"
            )

    if table_touched:
        append_missing_explicit_prefix_issues(
            values=values,
            prefixes=FORMAT_REPAIR_TASK_SURFACE_REQUIRED_PREFIXES["table"]["prefixes"],
            issues=issues,
            location=task_path,
            message=FORMAT_REPAIR_TASK_SURFACE_REQUIRED_PREFIXES["table"]["message"],
        )
        wps_target_value = values["- WPS table preset target:"]
        if not is_explicit_or_none(wps_target_value):
            issues.append(
                f"format-repair task record field is incomplete in {task_path}: - WPS table preset target:"
            )

    if style_blast_radius_touched:
        append_missing_explicit_prefix_issues(
            values=values,
            prefixes=FORMAT_REPAIR_TASK_SURFACE_REQUIRED_PREFIXES["style_blast_radius"]["prefixes"],
            issues=issues,
            location=task_path,
            message=FORMAT_REPAIR_TASK_SURFACE_REQUIRED_PREFIXES["style_blast_radius"]["message"],
        )
        if values["- TOC underline pollution detector required?:"] not in {"yes", "required", "active"}:
            issues.append(
                f"format-repair task record must require TOC underline pollution detector for style-blast-radius repair: {task_path}"
            )
        if values["- table style regression detector required?:"] not in {"yes", "required", "active"}:
            issues.append(
                f"format-repair task record must require table style regression detector for style-blast-radius repair: {task_path}"
            )

    if tail_block_touched:
        append_missing_explicit_prefix_issues(
            values=values,
            prefixes=FORMAT_REPAIR_TASK_SURFACE_REQUIRED_PREFIXES["tail_block"]["prefixes"],
            issues=issues,
            location=task_path,
            message=FORMAT_REPAIR_TASK_SURFACE_REQUIRED_PREFIXES["tail_block"]["message"],
        )

    if heading_touched:
        linked_lane = values["- heading / TOC / chapter-start linked lane active?:"]
        if linked_lane in EXPLICIT_VALUES or not is_explicit(linked_lane):
            issues.append(
                f"format-repair task record must explicitly lock the heading / TOC / chapter-start linked lane when heading-like surfaces are touched: {task_path}"
            )
        chapter_checkpoints = values["- chapter-start pagination checkpoints:"]
        if chapter_checkpoints in EXPLICIT_VALUES or not is_explicit(chapter_checkpoints):
            issues.append(
                f"format-repair task record must record chapter-start pagination checkpoints when heading-like surfaces are touched: {task_path}"
            )

    if abstract_touched:
        task_mode = values["- task mode:"]
        transaction_workflow = values["- selected mutation transaction workflow:"]
        local_format_repair_scope = task_mode == "format-repair-only" or transaction_workflow == "local-surface-repair"
        surfaces_text = raw_values["- abstract surfaces locked:"]
        if parse_line_value(find_lines_with_prefix(lines, "- abstract surfaces locked:")[0]) in EXPLICIT_VALUES:
            issues.append(
                f"format-repair task record must lock abstract surfaces when abstract is touched: {task_path}"
            )
        missing_surfaces = [
            token for token in ABSTRACT_SURFACE_TOKENS if token not in surfaces_text.lower()
        ]
        if missing_surfaces:
            issues.append(
                f"format-repair task record abstract surface lock is incomplete in {task_path}: {', '.join(sorted(missing_surfaces))}"
            )
        baseline_value = parse_line_value(
            find_lines_with_prefix(lines, "- abstract baseline source file path:")[0]
        )
        if baseline_value in EXPLICIT_VALUES or not is_explicit(baseline_value):
            issues.append(
                f"format-repair task record must name an abstract baseline source when abstract is touched: {task_path}"
            )
        toc_repair_value = values["- TOC repair included this round?:"]
        live_toc_value = values["- live TOC required this round?:"]
        if local_format_repair_scope and (
            toc_repair_value in {"yes", "active", "required", "true"}
            or live_toc_value in {"yes", "active", "required", "true"}
        ):
            issues.append(
                f"format-repair task record must not mix abstract repair with TOC refresh/rebuild in the same pass: {task_path}"
            )
        abstract_lane_context = "\n".join(
            raw_values[prefix]
            for prefix in (
                "- touched blocks this round:",
                "- specific format classes to verify:",
                "- explicit user rule:",
                "- helper scripts planned this round:",
            )
        )
        if local_format_repair_scope and contains_any(
            abstract_lane_context,
            {
                "citation-bearing body paragraphs",
                "bibliography numbering",
                "bibliography order",
                "superscript markers",
                "normalize_thesis_citation_chain.py",
                "citation normalizer",
                "field refresh",
                "fields.update",
                "word/document.xml",
                "body helper",
                "正文 helper",
                "body rewrite lane",
                "body chapter",
            },
        ):
            issues.append(
                f"format-repair task record mixes abstract repair with body/citation mutation in one pass: {task_path}"
            )

    citation_or_bibliography_context = "\n".join(
        raw_values[prefix]
        for prefix in (
            "- touched blocks this round:",
            "- specific format classes to verify:",
            "- explicit user rule:",
            "- helper scripts planned this round:",
        )
    )
    citation_or_bibliography_touched = contains_any(
        citation_or_bibliography_context,
        {
            "citation",
            "citations",
            "citation-bearing body paragraphs",
            "bibliography",
            "references",
            "reference list",
            "superscript marker",
            "superscript markers",
            "正文引用",
            "参考文献",
            "引文",
        },
    )
    if citation_or_bibliography_touched:
        citation_report_value = values["- citation audit report path:"]
        if is_explicit_none(citation_report_value) or not is_explicit(citation_report_value):
            issues.append(
                f"format-repair task record must provide a citation audit report path when citation/bibliography surfaces are touched: {task_path}"
            )
        touched_blocks_value = parse_line_value(find_lines_with_prefix(lines, "- touched blocks this round:")[0])
        if contains_any(
            touched_blocks_value,
            {"body page review", "chapter rewrite", "body family normalization", "body paragraph formatting"},
        ) and not contains_any(
            citation_or_bibliography_context,
            {"citation lane", "bibliography lane", "references lane", "normalize_thesis_citation_chain.py", "citation normalizer", "参考文献专项", "引文专项"},
        ):
            issues.append(
                f"format-repair task record routes citation/bibliography work through a generic body-only lane instead of a dedicated citation/bibliography lane: {task_path}"
            )

    if caption_touched:
        append_missing_explicit_prefix_issues(
            values=values,
            prefixes=FORMAT_REPAIR_TASK_SURFACE_REQUIRED_PREFIXES["caption"]["prefixes"],
            issues=issues,
            location=task_path,
            message=FORMAT_REPAIR_TASK_SURFACE_REQUIRED_PREFIXES["caption"]["message"],
        )

    if header_footer_touched:
        append_missing_explicit_prefix_issues(
            values=values,
            prefixes=FORMAT_REPAIR_TASK_SURFACE_REQUIRED_PREFIXES["header_footer"]["prefixes"],
            issues=issues,
            location=task_path,
            message=FORMAT_REPAIR_TASK_SURFACE_REQUIRED_PREFIXES["header_footer"]["message"],
        )

    for prefix in FORMAT_REPAIR_TASK_PATH_VALIDATION_PREFIXES:
        matched_lines = find_lines_with_prefix(lines, prefix)
        if len(matched_lines) != 1:
            issues.append(f"format-repair task record must contain exactly one '{prefix}' line: {task_path}")
            continue
        value = parse_line_value(matched_lines[0])
        if is_explicit_none(value) or not is_explicit(value):
            continue
        for raw_path in split_path_values(raw_values.get(prefix, raw_line_value(matched_lines[0]))):
            resolved = resolve_record_path(raw_path, task_path)
            require_file = prefix not in FORMAT_REPAIR_TASK_PATH_OPTIONAL_FILE_PREFIXES
            issues.extend(validate_existing_path(resolved, require_nonempty_file=require_file))

    citation_audit_value = values["- citation audit report path:"]
    output_manuscript_value = values["- output manuscript paths:"]
    if is_explicit(citation_audit_value) and not is_explicit_none(citation_audit_value):
        expected_docx_path: Path | None = None
        if is_explicit(output_manuscript_value) and not is_explicit_none(output_manuscript_value):
            output_paths = split_path_values(raw_values["- output manuscript paths:"])
            if output_paths:
                expected_docx_path = resolve_record_path(output_paths[0], task_path)
        citation_report_path = resolve_record_path(raw_values["- citation audit report path:"], task_path)
        issues.extend(check_thesis_citation_audit_report(citation_report_path, expected_docx_path=expected_docx_path))

    return issues
