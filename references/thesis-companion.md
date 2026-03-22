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

## Input expectations

Best-case inputs from the user:

- thesis template path
- sample paper path
- school formatting guide
- expected word count or chapter count

If these are missing, start by generating a thesis blueprint from the repository and wait for the template before final formatting.

## Feedback persistence rule

After the user reviews the delivered thesis files and points out concrete issues:

- convert the feedback into reusable production rules
- write those rules into the skill references or generator scripts
- treat the new rules as default behavior in future runs

