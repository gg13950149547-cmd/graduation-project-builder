# Thesis Source Expansion And No-Code Rule

Use this note when the user requires a longer thesis正文 and explicitly does not want code pasted into the manuscript.

## Rules

- If the user says thesis code should be removed, delete code blocks from the authoritative manuscript source itself.
- Do not rely only on the DOCX builder to skip rendering code, because stale code can reappear in later rebuilds.
- When the user gives a target正文 length such as `18000字`, treat that target as a hard completion constraint.
- Expand the manuscript source first, then rebuild DOCX/PDF; do not pad the final Word file manually.
- Prefer expanding system analysis, system design, implementation explanation, testing analysis, and conclusion paragraphs before adding new chapters.
- Keep the expansion consistent with the real system and already accepted screenshots, tables, and diagrams.
- When the user confirms that a thesis repair is effective, promote that successful repair path into the skill immediately and treat it as the new default writing path for the same class of documents.
- Do not fall back to an older broken workflow after a user has explicitly validated a better one; future edits should continue from the validated path and only refine within it.
