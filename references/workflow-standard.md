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

## 2. Delivery backlog

Convert the brief into a backlog with these minimum categories:

- entry flow
- main dashboard or main list page
- core business modules
- search or recommendation logic if relevant
- data initialization
- tests
- deployment and packaging

## 3. Feature-complete development

Each important module should have:

- data model or schema
- business logic
- route or API surface
- user-facing page or consumer
- error handling
- validation

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

## 6. Verification readiness

Minimum standard:

- framework or configuration sanity check
- test for main route or key service behavior
- proof that startup command is correct

Better standard:

- targeted regression tests for key flows
- build or compile validation
- documented known limitations
