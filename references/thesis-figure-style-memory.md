# Thesis Figure Style Memory

This file stores durable figure-style rules learned from user-provided thesis samples.

## Current learned style

- Overall visual language is academic and restrained, not slide-like and not infographic-like.
- Images do not contain figure names or figure numbers inside the canvas.
- Figure names are placed below the image as DOCX caption text.
- Images do not contain long explanatory sentences inside the canvas.
- Images should not be clipped, cropped, or partially visible after insertion.
- Typical styling:
  - white background
  - black or dark-gray outlines
  - very limited color usage, usually none
  - uniform border thickness
  - simple rectangles, rounded rectangles, ellipses, diamonds, actor/lifeline elements
  - no internal title banner
  - no decorative gradients, shadows, icons, or colored panels
- Layout habits:
  - diagram centered on page
  - generous whitespace around the drawing body
  - nodes aligned cleanly
  - arrows and connectors are explicit and readable
  - text sits inside shapes only for node labels, not for the figure caption or narrative explanation

## User-provided sample categories remembered on 2026-03-25

- ER-style relationship figure with central entity and surrounding attribute ellipses
- layered architecture figure with stacked rectangular modules
- warehouse/storage layering figure with centered module boxes
- sequence diagram with actor, lifelines, and red-outlined activation blocks
- system function model tree with left-to-right branching boxes
- token workflow figure using flowchart diamonds and process rectangles

## Operational rule

- Before generating or redrawing a thesis figure, compare the planned output against this style memory.
- If the result looks like a presentation graphic, reject it and redraw in thesis style.
- If the user provides newer figure examples, append the delta here in the same turn.
- When the figure sample exists as an actual image file, store it under `references/visual-style-samples/figures` for future visual comparison.
- If the user provides explicit figure samples, thesis screenshots, or template page captures, those visual samples override the generic defaults in this file. Use them as the primary style source for line weight, shape style, spacing, label placement, and overall composition.
- Default to draw.io for thesis structural figures, flowcharts, data-flow diagrams, and sequence diagrams; only fall back to code-generated images when draw.io is not suitable.

## Additional ER / Entity-Attribute sample recorded on 2026-03-26

- ER and entity-attribute figures may use a classic textbook Chen-style structure: rectangles for entities, ellipses for attributes, diamonds for relationships, and direct line connections.
- Cardinality markers such as `1` and `n` may be placed directly on connecting lines near the relationship edges.
- Entity boxes should remain plain white with thin dark borders and centered labels.
- Attribute ellipses should stay simple, unfilled, and evenly spaced around the related entity.
- Relationship diamonds should be small, centered on the relation line, and visually lighter than entity boxes.
- The whole ER figure should remain monochrome, sparse, and symmetric enough to read like a thesis textbook diagram rather than a software product graphic.
- Prefer broad canvas spacing and avoid compact clustering when multiple entities and relationships appear on one page.

## Additional system architecture tree sample recorded on 2026-03-26

- Overall system structure diagrams may use a centered tree layout with one top-level system box, second-level role boxes, and third-level module boxes.
- Boxes should remain plain rectangular containers with white fill, thin dark borders, and centered labels.
- Child modules may use narrow vertical rectangles when the sample shows a vertical stacked label style.
- Connectors should be straight, orthogonal, and visually even, with no decorative arrows or heavy styling.
- Horizontal branching should remain balanced so both sides of the structure feel symmetrical and easy to scan.
- The whole figure should stay monochrome, sparse, and textbook-like, with no icons, colors, shadows, or product-style decoration.
- This sample should be treated as a default reference for overall system architecture trees or role-module structure diagrams when the template does not impose another style.

## Additional layered architecture sample recorded on 2026-04-19

- When the user provides a screenshot reference for an architecture diagram that uses a large outer frame with aligned inner rectangles, that screenshot becomes the primary style lock for architecture-family figures.
- This layered architecture sample is now the mandatory default reference for architecture-family thesis figures unless the user explicitly provides a newer stronger sample for the same figure family.
- Treat this style as overriding the older tree-style architecture default for overall system architecture diagrams, data-acquisition architecture diagrams, and other grouped module architecture figures.
- For this architecture family, prefer grouped compartments over a loose tree with long directional arrows.
- The preferred composition is:
  - one large outer boundary frame
  - one short top-centered system or architecture label inside the outer frame when the sample itself shows that label
  - one centered inner module area with aligned rectangular submodules
  - optional left and right narrow vertical side modules when the sample shows side pillars
  - one or two wide horizontal layer boxes for data layers, processing layers, or output layers
- Keep the whole figure monochrome and white-background, with thin black borders and no colored fills, gradients, icons, title bars, or decorative arrowheads.
- The allowed top-centered label inside the outer frame is a system/container name only, not a figure number, not a caption sentence, and not a decorative banner.
- Internal labels should stay short and centered, and the diagram should read like a printed systems textbook figure rather than a slide or software poster.
- If the architecture semantics can be explained through containment and grouping, do not fall back to a root-node tree or arrow fan-out layout.
- Connectors are secondary in this architecture family. Use them only when the real content requires an explicit relation that cannot be conveyed by grouping alone.
- The outer frame, inner grouped frame, side pillars, and layer boxes should maintain visible padding and strict alignment; no child box may float loosely without belonging to one of these grouped regions.
- Use draw.io source files as the authoritative editable source for this architecture style, and keep exported PNGs visually aligned to the same layered academic layout.

## Additional use-case diagram sample recorded on 2026-03-26

- Use-case diagrams may follow a restrained textbook UML style with a simple actor on the left and oval use-case nodes on the right.
- The actor should remain plain black line art, without color or decorative styling.
- Use-case nodes should be elongated horizontal ellipses with white fill, thin dark outlines, and centered labels.
- Main use-case groupings should default to plain direct arrow routes from the actor toward the target use-case ellipses, while subordinate relations may use dashed arrows when the sample shows that pattern.
- The layout should favor a left-to-right hierarchy: actor first, primary use cases second, derived or subordinate use cases further right.
- By default, do not add an outermost system boundary unless a stronger current-run source explicitly requires it.
- Connectors should remain clean, sparse, and readable; use plain non-decorative arrowheads when arrows are required, and avoid icons, gradients, or shadow effects.
- The whole diagram should stay monochrome and balanced, matching a thesis textbook look rather than a software demo or slide layout.
- This sample should be treated as a default reference for use-case diagrams when the template does not impose another style.

## Required default figure surfaces

- ER / entity-attribute diagrams
- overall system architecture trees
- use-case diagrams

If the template does not define a stronger fixed style, these stored sample categories are default required references for thesis completion.

## Additional vertical flowchart sample recorded on 2026-03-27

- Flowcharts now lock to the stored SVG sample `references/visual-style-samples/figures/figure-flowchart-vertical-sample-01.svg`.
- The overall composition should remain a strict top-down vertical textbook workflow chart.
- For sequential business logic, the default accepted composition is one centered vertical chain from `开始` to `结束`.
- Start and end nodes should use rounded terminators with white fill and dark outlines.
- Decision points should use a centered diamond directly below the start node for single-gate logic.
- Process steps should remain plain white rectangles with dark outlines and centered labels.
- Branch labels such as `真` and `假` should sit beside the outgoing paths rather than inside separate boxes.
- Branches should stay left-right balanced and reconverge through a simple shared merge lane before the downstream central step.
- Connector lines should stay straight, monochrome, and structurally simple, with no decorative routing.
- The overall result should look like a clean textbook thesis flowchart, not a slide, infographic, or software block diagram.

## Additional flowchart correction recorded on 2026-04-18

- Double-row, horizontal, or snake-like thesis flowcharts are not accepted when the process itself is sequential.
- If a flowchart can be expressed as a direct start-to-end process chain, it must be redrawn as a single vertical downward flow rather than being distributed across left-right rows.
- This rule applies to thesis process figures such as data acquisition, parsing, cleaning, preprocessing, and trend-analysis workflows unless the business logic genuinely requires a visible decision branch.

## Additional sequence diagram sample recorded on 2026-03-27

- Sequence diagrams may use a classic monochrome UML academic layout.
- A stick-figure actor may appear on the far left when the sample shows an external user.
- Other participants may use light-gray rectangular headers with thin borders.
- Lifelines should be vertical dashed lines with generous horizontal spacing.
- Message arrows should be straight black horizontal lines with compact labels placed near the line, not oversized callouts.
- Activation bars should remain narrow, light, and unobtrusive.
- Branch logic may be expressed with a large `alt` frame and simple textual branch labels.
- The whole result should stay sparse, white-background, and textbook-like, not product-UI-like.

## Additional screenshot and code-figure lessons recorded on 2026-04-16

- Runtime page screenshots and code screenshots are different thesis figure families and must not share one acceptance rule blindly.
- Runtime page screenshots should remain authentic captures from the running system, with Chrome-based full-page capture as the default browser path when applicable.
- Code screenshots should remain real project code captures with line numbers and enough surrounding context to read the fragment.
- When the approved code-screenshot family is code-pane-only, crop away editor window borders, tabs, sidebars, and outer chrome while keeping the real code area and line numbers.
- Code screenshots must not contain manual in-image labels such as `关键代码`, `核心代码`, or section-number callouts.
- If a figure has been replaced with a real screenshot, its caption and nearby prose must stop calling it `示意图` or `样例图`.
