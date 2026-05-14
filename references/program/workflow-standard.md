# Workflow Standard

Use this as the target pattern for turning an unfinished project into a defendable deliverable.

The standard is derived from a complete delivery example with these characteristics:

- clear README describing the product and modules
- documented startup steps
- seed or import path for demo data
- admin or management surface
- scripted deployment and startup
- packaging script for delivery
- regression tests for core flows

## 1. Requirement summary

Before editing, summarize the project in a form that another engineer could continue from:

- what the system does
- who uses it
- which modules matter for the demo
- what data is required
- how the project is started
- how correctness is verified

If the repository lacks a brief, generate one and keep it short and concrete.

Graduation-project continuation rule:

- when the task includes both the system and the thesis, re-check the entire delivery chain from zero before continuing
- if the runnable system is still incomplete, continue building the system before more thesis polishing
- do not draft the final thesis before the program reaches a runnable, screenshot-ready, acceptance-ready state unless the user explicitly requests thesis-only work
- capture real system evidence such as pages, tables, charts, and test outcomes before turning implementation content into thesis chapters
- for Chinese graduation-project web systems, default the product UI copy to Chinese unless the user explicitly asks for another language
- keep the login page separate from the business-function pages
- keep admin and normal-user or courier pages separate instead of mixing them on one screen
- before login, do not expose business-function pages; enforce pre-login access control in the frontend flow and, where possible, in the backend/session logic

Program conditional-requirement lock:

- before backlog and implementation work, explicitly classify at minimum:
  - auth required or not required
  - persistence required or not required
  - admin surface required or not required
  - analytics/reporting required or not required
  - build output / delivery bundle required or not required
  - screenshot-ready runtime evidence required or not required
- every `not required` decision must be backed by repo evidence, project class, or an explicit user override
- if a condition is still unknown, treat it as unresolved rather than silently skipping it
- do not bypass these conditions just because a simpler prototype path already runs

## Program Execution Order

Use this ordered sequence when the current run is in `program-only` mode or in the program phase of `program-plus-thesis`:

1. inspect the repo and startup path
2. summarize purpose, roles, modules, data path, startup path, and verification path
3. turn missing work into a backlog
4. build incomplete modules in vertical slices:
   - data or schema layer
   - business logic
   - route, API, or controller layer
   - page, CLI, or consumer layer
   - validation and error handling
5. add operations surfaces:
   - start script
   - deployment path
   - demo data path
   - packaging path
   - README
6. add analytics, admin operations, and persistence when the project still looks prototype-level
7. verify:
   - startup
   - one main user flow
   - one admin flow
   - one analytics or reporting flow when applicable
8. package the program for delivery

Program verification evidence rule:

- record the artifact path for the runtime proof used in the current run, such as:
  - command output log
  - screenshot path
  - rendered page path
  - packaged output path
- store that proof through a review evidence record file rather than only a raw artifact path
- do not reduce verification to an undocumented claim that the flow was tested

Use `assets/program-gap-checklist.md` as the active backlog scaffold for this flow.

## 2. Delivery backlog

Convert the brief into a backlog with these minimum categories:

- entry flow
- main dashboard or main list page
- core business modules
- search or recommendation logic if relevant
- data initialization
- tests
- deployment and packaging

If the project is a data-analysis or management dashboard, include:

- analytics and visualization
- data import or seed flow
- admin operations

## 3. Feature-complete development

Each important module should have:

- data model or schema
- business logic
- route or API surface
- user-facing page or consumer
- error handling
- validation

For analytics dashboards:

- at least one line chart in the admin statistics area by default

## 4. Data readiness

A project is weak if it cannot demonstrate data. Ensure one of these exists:

- seed command
- import script
- demo SQL
- fixture or JSON seed
- mock data path

## 5. Operations readiness

Where possible, add:

- deploy script
- start script
- README commands
- packaging script

These do not need to be complex. They need to be reliable.

Graduation-project packaging rule:

- every final delivery package must include editable source code
- compiled or built outputs are mandatory for web delivery projects and other build-producing systems, but they are not mandatory for lightweight local-only projects that have no meaningful build artifact
- do not ship a package that contains only jars, binaries, or built static files
- for frontend-backend projects, package at minimum: backend source, frontend source, configuration files, database scripts, startup or deployment notes, and the final compiled artifacts
- the release layout should clearly separate source directories from build output directories so the reviewer can both run the program and continue modifying it

## 6. Verification readiness

Minimum standard:

- framework or configuration sanity check
- test for main route or key service behavior
- proof that startup command is correct

Better standard:

- targeted regression tests for key flows
- build or compile validation
- documented known limitations
