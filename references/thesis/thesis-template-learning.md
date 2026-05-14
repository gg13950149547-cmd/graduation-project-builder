# Thesis Template Learning

This note captures the thesis-writing conventions learned from the local sample set and teacher-provided template materials.

## Routing Note

- This file is the sample-extraction and template-learning layer.
- Use it to understand what the sample set teaches about structure, chapter emphasis, naming habits, and sample-derived expectations.
- It does not replace the canonical rule sources for thesis formatting, TOC repair, front-matter repair, or figure-generation execution.
- For canonical execution and rule ownership, use:
  - `references/thesis/thesis-format-sop.md`
  - `references/thesis/thesis-format-rules.md`
  - `references/user-feedback/template-and-layout.md`
  - `references/thesis/thesis-figure-generation-rules.md`

## What the sample set teaches

The paper is not a short technical report. It is a standard graduation thesis with:

- school cover and title page
- Chinese abstract and English abstract
- multi-level numbered chapters
- chapter 3 centered on system design and diagrams
- chapter 4 centered on implementation
- chapter 5 centered on testing
- chapter 6 for conclusion and outlook

If the provided school file is a formatting specification rather than a finished sample paper, extract it as a rule sheet:

- page setup requirements
- paragraph spacing and line spacing rules
- TOC rules
- abstract and keyword rules
- figure and table caption rules
- formula layout rules
- reference formatting rules

Do not mistake an explanatory rules document for a visual style source that should be copied page by page.

## Additional Lessons From Template-Following Revision Failures

Use these as sample-derived interpretation reminders after the canonical formatting rules have already been loaded.

These issues repeatedly caused thesis formatting regressions and should be checked proactively:

- updating fields is not equivalent to finishing the TOC
- page-class comparison against the local sample is a required acceptance action, not optional reassurance
- TOC title style, TOC body font, line spacing, tab leader, visible page numbers, and the page break after TOC are separate concerns
- front-matter numbering chains must be verified through real section/page-number state, not only by editing visible TOC strings
- citation hyperlinks can appear structurally present in the DOCX while still leaking anchor names into rendered body text
- runtime screenshot slots can silently drift away from their intended routes if the caption-to-media mapping is not locked
- bibliography heading formatting and bibliography entry formatting must be checked independently
- heading paragraph style alone is not enough; run-level bold can still be wrong
- copied or rewritten body text can silently fall back to default fonts if the template body style is not reapplied carefully
- deleting text without deleting the paragraph node leaves false blank lines that look like random spacing bugs
- a finished sample thesis is useful for visual comparison, but the school's formatting rules document remains the authority for what must be true

## Extracted chapter pattern

Recommended top-level structure learned from the sample:

1. 绪论
2. 系统分析 / 需求分析
3. 系统设计
4. 系统实现
5. 系统测试
6. 总结与展望

## Extracted second-level pattern

Common second-level headings from the sample:

- 1.1 研究背景与意义
- 1.2 国内外研究现状
- 1.3 研究内容与方法
- 1.4 论文组织结构
- 2.1 可行性分析
- 2.2 需求分析
- 2.3 业务流程分析
- 3.1 系统架构设计
- 3.2 功能模块设计
- 3.3 数据库设计
- 3.4 接口设计
- 4.1 开发环境搭建
- 4.2 前端功能实现
- 4.3 后端功能实现
- 4.4 核心代码实现
- 5.1 测试环境
- 5.2 功能测试
- 5.3 性能测试
- 5.4 安全性测试
- 5.5 兼容性测试
- 6.1 工作总结
- 6.2 展望

## Chapter 3 rule

The sample set strongly emphasizes chapter 3.

Expected content:

- architecture diagram
- function module design
- database design
- data flow analysis
- data dictionary
- interface design

The sample guidance also expects:

- fixed figure numbering like `图 3-1`, `图 3-2`
- fixed table numbering like `表 3-1`, `表 3-2`
- text paragraphs before or after each figure/table explaining the business meaning

## Writing rule

When following this template:

- imitate structure and heading style
- imitate figure and table placement logic
- imitate chapter granularity
- do not copy the original business content
- rewrite everything for the current project

Treat this as a template-shape learning note, not as a replacement for the canonical thesis workflow or thesis-format rule files.

## Diagram rule

The sample set includes or expects:

- system architecture figure
- top-level DFD
- first-level DFD
- data dictionary tables

Use `references/thesis/thesis-figure-generation-rules.md` as the canonical production rule source for these figures.
This section records what the sample appears to expect, not the full execution rule set for drawing and validating them.

Formatting habit learned from template checking:

- inserted figures should sit in their own centered paragraph
- figure captions remain a separate line from the image itself
- explanatory text about a figure should be written in body-text paragraphs before or after the figure, not by reusing the image paragraph as a normal text paragraph
- TOC pages are not plain heading lists; the sample uses dotted leaders and right-aligned page numbers
- TOC indentation changes with level and should visually communicate hierarchy, not just sequence

If the new project is software-oriented, preserve this habit:

- chapter 3 is diagram-heavy
- chapter 4 is implementation-heavy
- chapter 5 is testing-heavy

## Additional Template Learning From Word-Based Engineering Thesis Work

Use these as template-behavior lessons that refine interpretation of the sample set. They do not replace the canonical front-matter, TOC, end-matter, or pagination rules.

- A school thesis template may be a full administrative packet rather than only the thesis body.
- Before writing into the template, identify which pages are:
  - student-filled front matter
  - teacher/admin signature pages
  - thesis body placeholders
- Keep teacher-signature pages intact and only auto-fill what the student is expected to complete or what can be safely inferred from the project.
- If the user says appendix is unnecessary, do not keep appendix-like filler sections in the body just to increase length; expand the real chapters instead.
- For acceptance, rendered visual checks matter more than object counts:
  - verify cover pages
  - verify body pages
  - verify figure pages
  - verify table pages
  - verify that images are actually visible, not just embedded
- When the template itself explicitly describes formatting in text, those textual instructions override generic academic formatting habits.
- Do not reorder `致谢` and `参考文献` based on generic preference; follow the template's own sequence exactly.
- `致谢` and `参考文献` may require different title formatting:
  - `致谢` can be centered and spaced as `致 谢`
  - `参考文献` can be left-aligned and top-level without added spacing between characters
  - both must be validated against the template text, not inferred
- In template-driven thesis work, `目录` is a first-class structural deliverable. Losing it during body reconstruction is a failure, not optional cleanup.
- Keep `目录`, `致谢`, and `参考文献` as separate final-assembly checkpoints when validating a rebuilt template thesis.
- If the template explicitly uses `结束语` instead of a generic chapter title such as `第六章 总结与展望`, preserve the template wording. Do not normalize it back to a generic six-chapter label.
- If `结束语` is used by the template, treat it as a terminal top-level heading with the same structural weight as a chapter heading, including pagination rules such as "next chapter starts on a new page".
- If the template uses terminal blocks such as `结束语`, `致 谢`, and `参考文献`, validate both their order and their visual separation. Correct order is insufficient if the rendered pages still make them look merged.
- Repair sequence for end matter should be:
  1. clean duplicated reference insertion in the source manuscript
  2. verify explicit page breaks in the source
  3. avoid adding duplicate breaks in template assembly
  4. render the end pages and inspect them visually
- In the final writing round, do not assume the remaining work is only template format. Re-read the experiment tail and `结束语` page for process-status language and rewrite those pages into formal academic prose before the final format pass.
- For repeated thesis continuation on the same `.docx`, heading-text anchors are more reliable than paragraph indices. Use headings such as `结束语`, `致 谢`, and `参考文献` as the main edit anchors.
- If emergency Chinese text repair is performed through shell automation, avoid raw terminal literals; use UTF-8 script files or Unicode-escaped strings to prevent visible question-mark corruption in the manuscript.

## Additional Diagram Style Learning From User Corrections

The user provided explicit thesis figure samples and corrected a failed generated result. The correction establishes the following durable style rules:

- The figure canvas should contain only the diagram body. Do not draw figure titles such as `图 4-1 ...` inside the image.
- The figure caption must be written below the image as normal thesis text, centered as required by the template.
- Prefer monochrome or near-monochrome thesis drawing style: thin dark outlines, white fill, simple arrows, restrained labels, and no presentation-style colored title banners.
- Prefer clean academic spacing: balanced margins, centered composition, even node spacing, and no decorative background elements.
- ER figures should use plain entity/attribute shapes with uniform strokes and no embedded banner text.
- Architecture and module figures should use simple rectangular containers, consistent rounded or square boxes, and restrained grayscale line work matching the thesis examples.
- Sequence or flow figures should keep lifelines/arrows explicit, avoid ornamental styling, and preserve textbook-like diagram readability.
- If a stored style reference exists inside the skill, use that first; if the user provides newer samples, update the skill memory and treat the new samples as higher-priority style guidance for future thesis figure generation.

Use this section as a sample-derived style-learning supplement together with:

- `references/thesis/thesis-figure-generation-rules.md`
- `references/thesis-figure-style-memory.md`
