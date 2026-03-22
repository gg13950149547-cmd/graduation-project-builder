# Thesis Troubleshooting Log

Use this note as persistent operational memory for thesis production.

## 1. Thesis and deployment docs must stay separate

- Thesis Word files must contain thesis content only.
- Deployment/startup/manual deployment docs must remain outside the thesis.

## 2. Maintain one authoritative manuscript source

- Keep one main manuscript source for Word generation.
- Rebuild Word from the clean manuscript instead of repeatedly patching broken DOCX outputs.

## 3. Enforce subsection minimum length

- Check every `###` and `####` subsection.
- Expand any subsection under the required threshold immediately.
- Do not leave one-sentence subsection placeholders in the final manuscript.

## 4. Use UTF-8 script files for Chinese-heavy Word generation

- Avoid relying on long ad-hoc inline shell snippets for Chinese titles and captions.
- Prefer dedicated UTF-8 Python builder scripts.

## 5. Verify image embedding directly

- Inspect the DOCX package directly.
- Count `word/media/*`.
- Do not assume figures were embedded correctly without checking.

## 6. Rebuild instead of blindly patching broken Word files

- If title text, figure captions, or figure placement break, rebuild from clean sources.
- Do not keep iterating on a corrupted file if a fresh build is safer.

## 7. Match figure insertion by normalized or numbered headings

- Direct Chinese heading matching can fail silently.
- Prefer matching by normalized title text or stable numbered prefixes such as `3.2.1` and `4.2.3`.

## 8. Thesis design figures should default to black-and-white print style

- black borders
- black connector lines
- white fills

## 9. Prefer real page screenshots when possible

- If the real app can run, capture real login, home, query, dashboard, and map pages.
- Use generated layout diagrams only as a fallback.

## 10. Browser capture lesson

What worked in this project:

- use the local installed Edge browser directly
- allow browser execution outside restrictive sandboxing when needed
- run the real application locally first
- capture login directly and capture authenticated pages via saved local HTML snapshots when appropriate

## 11. Tables should be generated from dedicated markdown sources

- Keep chapter-3 and chapter-5 tables in dedicated markdown files.
- Convert them into Word tables during final DOCX assembly.

## 12. Visible directory requirement

- If the user wants an immediately visible directory, generate a manual visible directory.
- Do not rely only on a Word TOC field.

## 13. Every function needs real core code

- If the thesis describes a concrete function, insert a matching code snippet from the real codebase.
- Do not invent code.

## 14. Per-change benchmark rule

- After every meaningful file change, compare the result against the currently accepted best artifact.
- If the new result regresses, repair it immediately.

## 15. End-to-end autopilot rule

- Continue automatically through the next obvious step.
- Stop only when:
  - only template formatting remains, or
  - a real blocker appears.

## 16. User-feedback persistence rule

When the user points out a concrete problem in the thesis artifacts:

- summarize the complaint into a reusable rule
- store that rule in the skill references or generator scripts
- make it part of the default workflow for future theses
