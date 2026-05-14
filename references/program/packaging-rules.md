# Packaging Rules

Use this file when preparing the final program delivery bundle.

## Required Package Deliverables

Treat the package as incomplete unless it contains the required deliverables for the project class.

### Universal baseline for all project types

Every delivery bundle should contain these by default:

1. editable source code
2. startup-and-usage guide
3. any required configuration, dependency, or initialization notes

### Required bundle for web delivery projects

Treat a web graduation project as incomplete unless it also contains all of these:

1. complete separated frontend-backend source code when the architecture is frontend-backend split
2. complete separated build output that can run directly after delivery
3. one-click deploy script
4. one-click start script for the deployed program
5. manual deployment guide
6. startup-and-usage guide

### Default bundle for lighter local projects

For scripts, desktop tools, notebook-style analysis systems, or local-only data-analysis projects, the lighter default bundle is acceptable when no deployment surface exists:

1. editable source code
2. runnable local start command or launcher
3. startup-and-usage guide
4. required input-data, demo-data, or initialization instructions
5. packaged output only when the project actually has a meaningful build or release artifact

## Interpretation Rules

- The package is a deliverable bundle, not just a source-code archive.
- Source code and runnable build output are separate required artifacts for web delivery projects and other build-producing systems.
- Deploy and start are separate responsibilities for deployment-oriented systems and should not be merged into one vague script unless the user explicitly asks for that.
- Manual deployment guidance must still exist when one-click deployment scripts are part of the expected bundle.
- Startup-and-usage guidance must explain accounts, entry URLs, main flows, and demo or trigger paths when those concepts exist for the project.
- Do not force deploy scripts or built web-style output onto lightweight local projects that do not actually have a deployment surface.

## Recommended Extra Item

If the project depends on business data, also include demo-data or initialization-data instructions.
