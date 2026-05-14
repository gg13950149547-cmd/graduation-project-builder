# Verification Matrix

Choose the narrowest meaningful verification commands first, then expand only when needed.

## Python and Django

- environment sanity: import framework or run version check
- framework sanity: `manage.py check`
- data sanity: migrations, schema init, seed command
- tests: focused app tests, route tests, service tests
- startup proof: real local run command

## Flask and FastAPI

- import app or run startup check
- database init or migration command
- pytest for routes and services
- startup proof through uvicorn, flask, or equivalent command

## Pipeline and analytics repositories

- run the pipeline entry script
- confirm cleaned data and result artifacts are regenerated
- confirm dashboard entrypoint starts
- confirm export path creates the expected report artifact
- treat HDFS, Spark, MongoDB, or MySQL sync as optional checks unless the repository makes them mandatory for the main demo path

## Java

- dependency and compile check: Maven or Gradle test or package
- datasource or SQL init validation
- controller or service tests
- startup command validation through Spring Boot or equivalent run mode

## Node.js backend

- install and script sanity
- lint only if already part of the repo workflow
- focused test runner path
- startup proof with the actual script in `package.json`

## Frontend

- install and build
- route rendering or component tests if present
- manual smoke path when no test framework exists

## Universal manual checks

When automation is thin, manually verify:

- entry page or login page
- one full create or update flow
- one search or filter flow if applicable
- one admin or management flow if applicable
- one data initialization path

## Reporting rule

Always record which checks passed, which were skipped, and which failed. "Untested" is better than pretending.
