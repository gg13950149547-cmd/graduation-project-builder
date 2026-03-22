# Stack Adaptation

Use the same delivery workflow across stacks, but adapt the implementation style to the repository.

## Python web stacks

Typical signals:

- `manage.py`
- `requirements.txt`
- `pyproject.toml`
- app folders, templates, migrations

Typical actions:

- identify the framework entrypoint
- run migrations or schema setup
- add management commands or scripts for seed data when needed
- add focused tests for key views, services, and routes
- add start and deploy scripts if missing

### Django

Prioritize:

- settings sanity
- migrations
- management commands for demo data
- `manage.py check`
- view, model, and route tests

### Flask or FastAPI

Prioritize:

- app factory or server entrypoint clarity
- environment config
- schema init or Alembic flow
- pytest-based route and service tests

### Flask plus pipeline or analytics repo

Prioritize:

- pipeline entrypoint clarity
- raw, clean, result, and export directory contract
- optional sync steps for MySQL, MongoDB, or HDFS
- dashboard login and main view flow
- report export path
- startup script with stable port behavior
- lightweight simulation over expensive infrastructure when the full platform is not practical

## Java stacks

Typical signals:

- `pom.xml`
- `build.gradle`
- `src/main/java`
- `src/main/resources`

Typical actions:

- preserve the existing layered structure
- align entity, mapper or repository, service, controller
- confirm datasource config and SQL init
- add narrow controller or service tests
- verify packaging through Maven or Gradle build

## Node.js backend stacks

Typical signals:

- `package.json`
- `src/server.*`
- `app.js`, `server.js`

Typical actions:

- identify start and test scripts
- stabilize env config
- align route handlers, services, and ORM models
- add seed script if the demo data path is weak
- validate with existing test runner or add focused smoke tests

## Frontend-only repositories

Typical signals:

- `package.json`
- `vite.config.*`
- `src/App.*`
- no backend folder

Typical actions:

- infer whether mock data is acceptable
- create consistent data adapters or local mock source
- prioritize route completion, forms, tables, charts, and empty states
- verify build passes
- document how to demo without a backend

## Mixed frontend-backend repositories

Typical actions:

- identify which side defines the contract
- fix backend response shape first if the frontend depends on it
- update frontend requests and state handling next
- add one end-to-end verification path per important module

## Replacement rule

Do not replace the stack unless the current structure is more expensive to rescue than building a minimal conventional version. Graduation projects reward completeness more than architecture purity.

## Data-engineering graduation projects

When the repository mixes scripts, analytics outputs, dashboards, and heavyweight platform names:

- preserve the five-layer story if it already exists
- make the local pipeline reproducible first
- keep optional external integrations behind separate commands
- ensure the dashboard can demonstrate the analysis outputs without requiring the full big-data platform to be live
