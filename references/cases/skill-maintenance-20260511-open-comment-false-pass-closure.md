# Skill Maintenance Case: Open Comment False-Pass Closure

- date: 2026-05-11
- scope: canonical `graduation-project-builder` skill maintenance plus project repair validation
- authorization: current conversation grants multi-agent collaboration; existing read-only audit agents reviewed DOCX/SHA/comment evidence, skill gate coverage, and source-to-final ledger closure
- trigger: a candidate thesis copy claimed all teacher comments were fixed while `word/commentsExtended.xml` still left every comment open in Word/WPS
- root cause: `scripts/audit_thesis_comment_resolution.py` accepted detector-bound fixed ledger rows as final closure without requiring the final DOCX open-comment count to be zero
- skill change: all-comments-resolved claims now fail when the exact final DOCX still has open comments; comment-driven gate records use the same strict assertion
- helper change: `scripts/close_docx_comments_from_ledger.py` can close comment done states in a new DOCX path after a source-bound fixed ledger exists, while preserving comment text, anchors, relationships, tracked changes, media, and document body content
- regression coverage: `case_comment_resolution_fixed_ledger_open_final_rejected` covers the false-pass pattern where a fixed ledger row tries to pass while the final DOCX still has an open comment
- required validation: py_compile changed scripts; targeted comment selftests; JSON owner-map parse; UTF-8 clean; skill gate validation
- residual risk: final thesis acceptance still needs fresh detector reports bound to the post-closure DOCX SHA because changing `commentsExtended.xml` changes the package hash
