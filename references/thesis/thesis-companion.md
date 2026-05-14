# Thesis Companion

Use this guidance when the user expects the generated program to come with a matching thesis, dissertation, or graduation report.

This skill should not stop at code delivery. It should connect the implementation to a paper-ready narrative.

## Primary rule

When the user provides a template, sample paper, school format, or prior thesis:

- follow the format
- follow the chapter order
- follow the heading depth and numbering style
- follow the figure and table caption style
- do not copy the original text content
- write fresh content based on the actual generated project

Paragraph-level review override:

- every newly written thesis paragraph and every modified thesis paragraph must be followed immediately by a local rendered-page machine-vision review
- that review must confirm both template compliance and content correctness before the next paragraph is touched
- do not postpone this review to the end of the subsection or end of the chapter

## Working order

1. Read the project and reconstruct the real system.
2. Read the template or sample.
3. Infer the required paper skeleton:
   - abstract
   - introduction
   - requirements analysis
   - system design
   - database design
   - implementation
   - testing
   - conclusion
   - references
   - appendices when needed
4. Map the actual program to each chapter.
5. Plan the figures and tables before drafting large sections.
6. Draft the paper with consistent terminology.

## Language polishing policy

Use language-polishing skills only after the chapter or abstract already matches the real project.

Chinese thesis prose:

- for Chinese abstract drafting, Chinese abstract rewriting, and Chinese body-section rewriting, use `humanizer-zh`
- keep the result formal, specific, and thesis-appropriate
- never use this pass to invent evidence, fabricate analysis, or pad length with generic conclusions
- do not skip this pass for Chinese thesis prose simply because the text looks roughly acceptable on first inspection

English abstract:

- the English abstract must be produced from the finalized Chinese abstract
- after translation, use `humanizer` to smooth stiff English or obvious AI phrasing
- this pass must preserve claim scope and technical meaning exactly
- the English abstract is still a translation artifact, not a separate marketing summary
- if the current run intentionally writes or rewrites English thesis prose outside the abstract, that English prose must also go through `humanizer`

Scope boundary:

- do not apply `humanizer-zh` or `humanizer` to pure formatting repair work
- do not use them as a substitute for content consistency review
- content truth comes first, language smoothing comes second
- when the run is formatting-only, record the humanizer route explicitly as `none` rather than leaving it unstated
- when a humanizer route is active, the acceptance record must point to `assets/humanizer-evidence-template.md`-style evidence with the actual before text, after text, target language, processed paragraph ID, and skill name (`humanizer-zh` or `humanizer`)
- a path-only humanizer note is not evidence; if the before/after text or paragraph ID is missing, the content pass is incomplete

Read `references/thesis-production-workflow.md` when you need the full repeatable workflow from program analysis through Word assembly.

## Subsection writing rule

Do not let a subsection collapse into a single sentence or a caption placeholder.

Each subsection should normally contain:

- one lead-in paragraph that explains the purpose of the subsection
- one or more body paragraphs that explain the real project content
- figure or table references inserted into running text when relevant

Default minimum:

- each subsection should normally contain at least 300 Chinese characters
- if a subsection is too short, expand it with purpose, method, process, result, and significance sentences before finalizing

This applies especially to:

- 3.x design subsections
- 4.x implementation subsections
- 5.x testing subsections

## Figure and table policy

Generate or plan figures that reflect the real project:

- architecture diagram
- functional structure diagram
- database ER diagram
- key workflow diagrams
- main page screenshots
- test result tables

For every figure and every table inserted into the thesis body:

- add a dedicated explanatory body paragraph after the caption
- the explanation must normally be no less than 200 Chinese characters
- the explanation should describe what the reader should observe, how the figure or table supports the current subsection, and what conclusion can be drawn from it
- do not treat a caption as a substitute for the required explanatory paragraph
- if a figure or table appears without a sufficient explanatory paragraph below it, the subsection is incomplete

If the template or sample uses a specific naming pattern such as "图 3-1" or "Table 4-2", preserve that style.

If the user has accepted the black-and-white thesis style, prefer:

- black borders
- black lines
- white fills

for generated design diagrams.

## Content policy

The paper must match the program:

- module names should match the real implementation
- technology stack should match the real implementation or documented simplified path
- database description should match the schema or init SQL
- testing chapter should match actual checks, smoke tests, and run results

Do not claim features that the codebase does not support unless they are explicitly marked as design-only or planned work.

Do not let language-polishing passes erase concrete module names, implementation details, measured outcomes, or explicit limitations that are needed for thesis credibility.

## Input expectations

Best-case inputs from the user:

- thesis template path
- sample paper path
- school formatting guide
- expected word count or chapter count

If these are missing, start by generating a thesis blueprint from the repository and wait for the template before final formatting.

Default thesis length rule:

- unless the user explicitly sets another target, thesis production should default to a full manuscript length of no less than 10000 Chinese characters

## Feedback persistence rule

After the user reviews the delivered thesis files and points out concrete issues:

- convert the feedback into reusable production rules
- write those rules into the skill references or generator scripts
- treat the new rules as default behavior in future runs

