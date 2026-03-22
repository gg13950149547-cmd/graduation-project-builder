# Django Music Reference

This note captures the concrete project pattern used as the source standard for this skill.

Source project:

- `D:\项目\基于Django的音乐推荐系统`

## Product shape

- user-facing music recommendation site
- admin surface and management dashboard
- search, rankings, song detail, profile, favorites, playlists
- demo-oriented but structurally complete

## Why this project is a good standard

It contains the full delivery loop, not just source code:

- README describing modules and startup
- package manual describing manual deployment
- deploy script
- start script
- package-release script
- management commands for importing and enriching demo data
- regression tests for key pages and user actions

## Concrete workflow extracted from it

### 1. State the product clearly

The README explains:

- what the system is
- which modules exist
- how to start it
- which URLs matter
- which checks already passed

This is the baseline for automatic requirement summary.

### 2. Make data reproducible

The project does not rely only on empty tables. It includes:

- import command for real music metadata
- backfill command for scene tags
- migration flow

This is the baseline for automatic data initialization.

### 3. Make operations repeatable

The project includes:

- deploy script for environment setup and dependency install
- start script for runtime startup
- package script for zip delivery

This is the baseline for automatic deployment and packaging.

### 4. Make verification explicit

The project documents and includes:

- `manage.py check`
- migrations
- `manage.py test`
- focused tests for homepage, search, rankings, detail page, auth-protected page, favorites, playlists

This is the baseline for automatic testing.

## How to generalize from this example

When working on another stack, preserve the workflow even if the commands change:

- README or brief instead of implicit requirements
- seed or import path instead of empty database
- start and deploy script instead of manual tribal knowledge
- package or bundle output instead of loose files
- focused regression tests instead of "works on my machine"
