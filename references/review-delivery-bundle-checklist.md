# Delivery Bundle Review Checklist

Use this checklist before claiming the program delivery bundle is complete.

## Required Artifacts
- [ ] editable source code exists
- [ ] startup or usage guidance exists
- [ ] required configuration or initialization guidance exists
- [ ] project-class-specific bundle requirements were checked against `references/program/packaging-rules.md`

## Web Delivery Additions
- [ ] frontend source code
- [ ] backend source code
- [ ] final build output / compiled artifacts
- [ ] startup scripts
- [ ] deployment guide

## When Applicable
- [ ] configuration files
- [ ] database scripts
- [ ] packaged runtime output for build-producing systems
- [ ] lightweight local launcher or start command for non-deployment projects
- [ ] demo-data or initialization instructions when business or analysis data is required

## Packaging Rules
- [ ] source and build outputs are clearly separated when the project actually has build output
- [ ] a reviewer can both run the system and continue modifying it
- [ ] delivery is more than a plain source archive

## Final Rule
If any artifact required by the project class is missing, the delivery bundle is incomplete.
