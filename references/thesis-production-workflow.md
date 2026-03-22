# Thesis Production Workflow

Use this as the default end-to-end workflow when turning a finished program into a matching graduation thesis.

## Goal

The thesis workflow is complete when the work has progressed from:

1. program understanding
2. chapter drafting
3. figure and table generation
4. code-snippet extraction
5. Word assembly
6. troubleshooting-guided rebuilds when needed
7. final formatting against the user's template

After step 7, the task is considered finished.

## Workflow

### 1. Read the real project first

Before writing the thesis:

- read the repository structure
- read README and docs
- read main app entrypoints
- read data-processing scripts
- read database sync or schema files
- read routes, views, controllers, and key business logic

The thesis must reflect the actual project, not a guessed system.

### 2. Use the remembered default thesis sample first

Use `references/thesis-template-learning.md` as the default remembered sample.

Do not re-discover the same sample each time unless:

- the user provides a different template
- the user explicitly asks to replace the current default structure

If a new template is provided, then extract its chapter skeleton, heading depth, numbering style, and figure/table placement habits.

### 3. Build the thesis skeleton

Create:

- thesis blueprint
- outline
- figure and table plan
- front/back matter notes

At this stage, decide which real project modules map to:

- system analysis
- system design
- system implementation
- system testing

### 4. Draft the thesis text

Write chapter content in order:

- abstract and abstract-en
- chapter 1 introduction
- chapter 2 system analysis
- chapter 3 system design
- chapter 4 system implementation
- chapter 5 system testing
- chapter 6 conclusion and outlook

## Writing constraints

- each subsection must start with a lead-in paragraph
- each subsection should normally be at least 300 Chinese characters
- do not leave sections as one-sentence placeholders
- keep wording consistent with the implemented system

### 5. Generate thesis figures from the real program

Do not stop at prose. Produce the figures the sample expects.

Typical figure sources:

- architecture and technical architecture: derived from repository structure
- workflow diagrams: derived from actual program flow
- DFD diagrams: derived from data movement in scripts and app routes
- ER diagram: derived from schema or database sync code
- chapter 4 images: prefer real page screenshots from the running program
- chapter 5 images: use real charts or test screenshots

Diagram styling rule learned from this project:

- black border
- black connector lines
- white fill

Prefer this style for thesis design figures unless the user overrides it.

### 6. Add core code for each function

For each concrete function discussed in the implementation chapter:

- extract a matching code snippet from the real codebase
- place the snippet near the relevant subsection
- do not invent code

Typical targets:

- login
- home/dashboard
- query page
- map or visualization
- data generation or data import
- data cleaning
- statistical analysis
- database sync

### 7. Assemble a Word draft

Create a Word draft that includes:

- title
- abstract
- abstract-en
- visible directory or TOC
- body chapters
- figures
- tables
- code snippets

Do not mix deployment instructions into the thesis document.

### 8. Apply remembered troubleshooting fixes during assembly

Before finalizing the thesis Word draft, read and apply `references/thesis-troubleshooting-log.md`.

This is now part of the standard workflow, not an optional note.

### 9. Final stage: template-only formatting

Once the thesis content, figures, tables, and code snippets are all in the Word draft, the remaining work should be treated as formatting only:

- adjust according to the user-provided template
- adjust fonts, line spacing, heading styles, page breaks
- adjust figure captions and table captions
- adjust visible directory or TOC layout

At this stage, the task should not reopen content generation unless the user explicitly requests content changes.

## Completion rule

After the thesis has reached the state:

- content drafted
- figures generated
- tables inserted
- code snippets inserted
- Word file assembled
- troubleshooting lessons applied
- only template formatting remains

the workflow is considered complete enough to hand over for final formatting.
