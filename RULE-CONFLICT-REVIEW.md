# Rule Conflict Review

Current date: 2026-04-11

This file records rule conflicts that required an explicit user decision.

Current status:

- all items below were resolved by user choice on 2026-04-11

## 1. Default citation placement inside thesis body

Conflict:

- `references/thesis/thesis-production-workflow.md` says final QA should verify citations are placed on appropriate in-sentence technical anchors rather than default paragraph tails.
- `references/user-feedback-persistence.md` says that when the strict sentence-based rule is active, the citation marker should be placed at the end of the claim-bearing sentence, immediately before the sentence-ending punctuation mark.

Why this is a real conflict:

- "in-sentence technical anchor" and "sentence-end before punctuation" are different default placement strategies.
- Both can be defensible, but they produce visibly different citation behavior.

Decision options:

- Option A: default to sentence-end citation placement before punctuation
- Option B: default to in-sentence technical-anchor placement
- Option C: use sentence-end by default, but switch to in-sentence anchors only when the user explicitly requests anchor-level citation placement

Resolved choice:

- Option C

## 2. Packaging strictness for non-web or lighter-weight projects

Conflict:

- `references/program/workflow-standard.md` treats deployment path as an operations surface to add when useful.
- `references/program/packaging-rules.md` currently treats one-click deploy script, one-click start script, manual deployment guide, startup-and-usage guide, separated source code, and separated build output as required package deliverables by default.

Why this is a real conflict:

- The skill claims to cover graduation projects across common software workflows, not only deployment-heavy frontend-backend web systems.
- The packaging file is currently stricter than the general program workflow and may over-constrain lighter projects.

Decision options:

- Option A: keep the current strict package bundle as the default for every project
- Option B: make deploy/start/build-output requirements conditional on project type, while keeping source code, startup guidance, and usage guidance universal
- Option C: keep strict packaging only for web delivery projects and define a lighter default bundle for scripts, desktop tools, and local-only analysis systems

Resolved choice:

- Option C

## 3. Canonical sink for future durable rule promotion

Conflict:

- The skill architecture now treats `memory.md` as a short cross-project summary and sends detailed durable rules to focused references.
- Historical behavior often wrote detailed durable fixes into `memory.md` as well, causing duplication with `references/user-feedback-persistence.md` and thesis-specific references.

Why this is a real conflict:

- If both remain active sinks, rule drift will return.
- If only one sink is canonical, maintenance becomes much easier, but that choice should stay explicit.

Decision options:

- Option A: `memory.md` stays summary-only; detailed durable corrections go to focused references
- Option B: dual-write detailed durable rules to both `memory.md` and the focused reference
- Option C: move almost all durable corrections into `references/user-feedback-persistence.md` and keep `memory.md` minimal enough to be read in one glance

Resolved choice:

- Option C, with explicit permission to keep splitting focused markdown files further when a detailed rule file becomes too heavy

## 4. Runtime screenshot truthfulness vs. code screenshot crop style

Conflict:

- `references/thesis/figure-rules/baseline-and-sourcing.md` treats authentic runtime screenshots as full-page evidence assets captured from the real running system.
- This conversation established a separate accepted figure family for code screenshots: real project code, line numbers visible, enough code context, and code-pane-only crops when the user explicitly requested no editor border.

Why this is a real conflict:

- If both are treated as one generic "screenshot" rule, the builder can falsely reject valid code-pane-only code screenshots or wrongly accept cropped UI fragments as runtime evidence.

Decision options:

- Option A: force every screenshot-like figure to keep full window chrome
- Option B: force every screenshot-like figure to be tightly cropped
- Option C: split runtime screenshots and code screenshots into separate figure families with different crop rules

Resolved choice:

- Option C

## 5. Generic sequential formula numbering vs. template chapter numbering

Conflict:

- Earlier automation temporarily normalized formulas into simple sequential numbering such as `(1) ... (8)`.
- The accepted template style in this conversation requires chapter-based numbering such as `(2-1) ... (2-7), (5-1)`.

Why this is a real conflict:

- Both are common academic patterns, but they are not interchangeable once the template family is already visible in the accepted manuscript.

Decision options:

- Option A: keep generic sequential numbering for easier automation
- Option B: always rewrite everything to chapter numbering
- Option C: follow the active template or accepted manuscript numbering family, with chapter numbering required when that family is already present

Resolved choice:

- Option C

## 6. Legacy sample wording vs. upgraded real screenshots

Conflict:

- Earlier manuscript figures and surrounding prose could still call a figure `示意图` or `样例图`.
- During this conversation, several figure slots were upgraded to real screenshots and authentic captures.

Why this is a real conflict:

- Leaving schematic wording beside a real screenshot creates a truthfulness mismatch and weakens thesis credibility.

Decision options:

- Option A: leave legacy captions alone if the image itself looks better
- Option B: update only the caption but ignore alt text and nearby prose
- Option C: whenever a figure switches from sample/schematic to real screenshot, update caption, alt text, and nearby prose in the same pass

Resolved choice:

- Option C

## 7. Humanizer usage in thesis writing vs. optional polish

Conflict:

- `references/thesis/thesis-production-workflow.md` and `references/thesis/thesis-companion.md` historically treated `humanizer-zh` / `humanizer` as recommended smoothing passes.
- Repeated thesis sessions showed that when this stayed optional,正文重写 often skipped language cleanup entirely, leaving obviously templated or AI-sounding prose in final review copies.

Why this is a real conflict:

- If humanizer routing stays optional, the workflow cannot reliably tell whether the omission was intentional or an unnoticed skip.
- If it becomes mandatory everywhere, it can wrongly pollute pure formatting repair work, captions, references, or code/field text.

Decision options:

- Option A: keep humanizer as a soft recommendation only
- Option B: force humanizer in every thesis-related run, including pure format repair
- Option C: force explicit humanizer routing for thesis content writing and rewriting, while forbidding it in pure format-repair-only runs

Resolved choice:

- Option C
- Mandatory interpretation:
  - Chinese abstract/body drafting or rewriting must route through `humanizer-zh`
  - English abstract/body drafting or rewriting must route through `humanizer`
  - mixed-language thesis writing may route through `both`
  - pure format-repair-only work must explicitly record `none`
