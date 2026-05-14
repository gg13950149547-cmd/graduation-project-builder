# Skill Maintenance Case: pass041 front-matter and page-number helper closure

- date: 2026-05-11
- scope: canonical `graduation-project-builder` maintenance during the campus abnormal-behavior thesis repair lane
- authorization: user granted default multi-agent collaboration in this session
- changed files:
  - `scripts/repair_front_matter_page_numbering.py`
  - `scripts/selftest_skill_flow.py`
  - `references/rule-owner-map.json`
  - `references/thesis/format-rules/front-matter-and-toc.md`
  - `FILE-ROLE-INDEX.md`

## Problem

The pass041 helper chain fixed the visible signature-residual page and front-matter/body page-number split, but the canonical skill bundle did not yet have regression coverage for those helper behaviors. This allowed the bundle gate to pass even when `frontmatter-signature-residual` and `repair_front_matter_page_numbering.py` were not represented in selftests or active helper ownership documentation.

## Durable Rule

- `repair_thesis_frontmatter_toc_structure.py` operation `frontmatter-signature-residual` is a locked front-matter operation. It may remove only unanchored blank declaration spacer paragraphs and tighten declaration-title spacing; it must preserve bookmarks, fields, comments, drawings, section breaks, signature text, and all non-declaration front-matter content.
- `repair_thesis_frontmatter_toc_structure.py` operation `duplicate-page-breaks` must cover later level-1 body headings, not only the first body opener. It may remove explicit page-break runs from a level-1 body heading that already owns `w:pageBreakBefore`, while preserving the paragraph-owned break.
- `repair_front_matter_page_numbering.py` is the canonical helper for front-matter/body page-number section repair. It must write a new review-copy path, replace only `word/document.xml`, bind input/output SHA256 values, fail closed when the Chinese abstract or first body heading cannot be located, and preserve the source package while establishing lower-roman front matter and arabic body restart semantics.

## Validation Plan

- `py -3 -m py_compile scripts/repair_thesis_frontmatter_toc_structure.py scripts/repair_front_matter_page_numbering.py scripts/selftest_skill_flow.py`
- Targeted selftests: `repair_frontmatter_toc_structure_chapter_heading_duplicate_page_break_valid`, `repair_frontmatter_toc_structure_signature_residual_valid`, `repair_frontmatter_toc_structure_signature_residual_preserves_protected_anchors_valid`, `repair_front_matter_page_numbering_inserts_frontmatter_section_valid`, `repair_front_matter_page_numbering_updates_existing_frontmatter_sections_valid`, `repair_front_matter_page_numbering_same_path_rejected`, `repair_front_matter_page_numbering_missing_chinese_abstract_rejected`, `repair_front_matter_page_numbering_missing_body_start_rejected`
- `py -3 -m json.tool references/rule-owner-map.json`
- `py -3 scripts/validate_skill_gate.py --skill-root .`
- `py -3 scripts/check_utf8_clean.py --root . --json`
