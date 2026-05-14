# Canonical Thesis Engine Contract

This file defines the ownership boundary between the canonical skill bundle and
project-local thesis artifacts.

## Engine Ownership

- General thesis-making scripts must live under the canonical skill bundle, especially under `scripts/`.
- `scripts/build_canonical_thesis.py` is the canonical general entry point for template plus adapter/content-manifest thesis generation.
- The canonical skill scripts own DOCX assembly, template-donor extraction, cover/front-matter preservation, abstract surfaces, TOC construction, body insertion, figures, tables, citations, references, rendering, self-check, and acceptance generation.
- The canonical builder owns the generic donor-preserving implementations for cover title replacement, abstract body prefix/content-run replacement, keyword label/content run separation, static TOC paragraph cloning, TOC page-number run updates, and first-level body chapter pagination owners.
- The canonical builder also owns generic mixed-script body-text behavior whenever the run touches Chinese body paragraphs that contain English words, API routes, code identifiers, model names, file names, ASCII punctuation clusters, or digit-heavy tokens. Project-local helpers must not invent their own run-splitting policy, mixed-font policy, or keyword-label/body policy for those surfaces.
- If a general thesis-making behavior is missing, extend the canonical skill script and its regression tests first.
- Do not create a project-local or workspace-local script that becomes a reusable thesis builder for many templates.

## Local Adapter Ownership

Project-local files may exist only as run-specific adapters:

- template profile files extracted from one approved local template or sample
- project content manifests that name real project evidence, screenshots, tables, and bibliography inputs
- thin wrapper manifests that call canonical skill scripts with locked input and output paths
- template-specific override data such as donor paragraph identifiers, surface labels, page-class expectations, or local field mappings

- Project-local adapters must not own general behavior:

- no generic DOCX assembly algorithm
- no broad paragraph rewrite loop
- no paragraph rebuild helper that collapses existing mixed-script runs into one replacement run before later "repair" logic
- no hardcoded global font, heading, abstract, TOC, table, figure, citation, reference, or pagination policy
- no hardcoded keyword-label/content policy
- no hardcoded identifier whitelist that decides which English tokens in Chinese body text should be split into Western-font runs
- no cross-template fallback policy
- no independent success or acceptance verdict

## Required Local Adapter Shape

Every generated project-local thesis adapter manifest must declare:

- `schema`: `graduation-project-builder.local-thesis-adapter.v1`
- `adapter_type`: one of `template-profile`, `project-content-manifest`, `thin-wrapper-manifest`, or `run-manifest`
- `canonical_scripts`: canonical skill script paths used by the adapter
- `template_specific`: `true`
- `template_path` or `template_fingerprint`
- `project_root` or `run_root`
- `allowed_scope`: a list of template/project-specific surfaces or inputs

The adapter must pass `scripts/validate_thesis_local_adapter.py` before it is used
as evidence for a thesis generation or repair run.

## Execution Order

1. Extract or write a project-local adapter/profile for the current template and project.
2. Validate the adapter with `scripts/validate_thesis_local_adapter.py`.
3. Run `scripts/build_canonical_thesis.py` or another canonical skill script for generic thesis-making behavior.
4. Run `scripts/scan_project_local_thesis_helpers.py --project-root <project-root> --fail-on-risk`.
5. Continue to rendering, `sample_self_check`, acceptance-record generation, and skill gate validation on the exact final output.

## Completion Rule

A run is not clean just because it avoids thick local scripts. It is clean only
when the general engine behavior is in the canonical skill bundle, local files
are limited to template/project-specific adapter data or thin wrappers, and the
adapter validation report is recorded with the run evidence.
