# Executable Automation

This skill should prefer creating real helper artifacts when the repository lacks operational surfaces.

## Generate when missing

- `docs/project-blueprint.md`
- `docs/acceptance-report.md`
- `docs/manual-deployment.md`
- deploy script
- start script
- package script
- test script

## Naming preference on Windows-heavy repos

Prefer PowerShell files in `scripts/`:

- `scripts/codex_deploy.ps1`
- `scripts/codex_start.ps1`
- `scripts/codex_package.ps1`
- `scripts/codex_test.ps1`

If the repo already uses `.bat`, `.sh`, npm scripts, Maven wrappers, Gradle wrappers, or Python utilities, match the existing style instead of forcing a new one.

## Generation rule

Generated scripts should:

- be minimal and readable
- call the real stack commands
- avoid destructive behavior
- print the next step clearly
- be safe to inspect and edit by a student

## Acceptance report rule

The acceptance report should answer:

- what stack was detected
- what operations surfaces already exist
- what the likely demo path is
- what verification path exists
- what is still missing for a defendable submission

## Packaging rule

When generating or updating a final delivery bundle, include these artifacts together:

- one-click deploy script
- one-click start script
- manual deployment guide

The guide should mirror the generated scripts but also explain how to run the project step by step if the scripts fail.
