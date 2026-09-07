# JobFlow — Distributed Background Job Processing Platform

> A production-oriented distributed background job processing platform for submitting, executing, tracking, and monitoring asynchronous workloads.

## Current status

JobFlow includes the backend execution pipeline, reliability controls, worker monitoring, authentication, automated quality gates, and a React operational dashboard.

## Architecture

```text
Client / Dashboard
        │
        ▼
     FastAPI ──────────────► PostgreSQL
        │                         ▲
        ▼                         │
      Redis ◄──── Celery Workers ─┘
        │              │
        └──────────────┘

Prometheus-style metrics are exposed through the API layer.
```

## Implemented capabilities

- REST job submission, listing, and detail APIs
- Job lifecycle: `QUEUED`, `RUNNING`, `SUCCESS`, `FAILED`, `RETRYING`, `CANCELLED`
- Persistent execution attempts and retry backoff
- Job priorities, retry limits, timeouts, and idempotency keys
- Standard `Idempotency-Key` request header support with payload conflict detection
- Job cancellation through Celery task revocation
- Worker registration, native heartbeat persistence, and stale-worker detection
- Worker health and Prometheus-style operational metrics
- Authentication with expiring signed bearer tokens and role-based authorization
- Structured JSON request logging with request correlation IDs
- React + TypeScript dashboard with live polling
- Job search and status filtering
- Job detail drawer with results/errors
- Worker status panel
- Production frontend container served by Nginx
- Docker Compose integration for the complete local stack
- Alembic migrations and database hardening constraints/indexes
- Automated Ruff, compilation, migration, and pytest CI checks

## Dashboard

Start the complete stack from `infrastructure/compose`:

```bash
docker compose up --build
```

Then open `http://localhost:3000` for the dashboard and `http://localhost:8000/docs` for the API documentation.

For local frontend development:

```bash
cd frontend
npm install
npm run dev
```

The dashboard expects the API at `http://localhost:8000/api/v1` by default. Set `VITE_API_URL` to override it.

## Authentication

The development stack bootstraps an administrator from `ADMIN_USERNAME` and `ADMIN_PASSWORD`. Change these values before exposing the service outside a local development environment.

Production configuration rejects placeholder security secrets.

## API examples

Authenticate:

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"username":"admin","password":"change-me-now"}'
```

Submit a job with an idempotency key:

```bash
curl -X POST http://localhost:8000/api/v1/jobs \
  -H 'Content-Type: application/json' \
  -H 'Authorization: Bearer <token>' \
  -H 'Idempotency-Key: example-001' \
  -d '{"task_type":"sum","payload":{"numbers":[10,20,30]},"priority":8}'
```

List jobs:

```bash
curl http://localhost:8000/api/v1/jobs \
  -H 'Authorization: Bearer <token>'
```

List workers:

```bash
curl http://localhost:8000/api/v1/workers \
  -H 'Authorization: Bearer <token>'
```

Metrics:

```bash
curl http://localhost:8000/metrics
```

## Database migrations

Apply migrations explicitly with:

```bash
cd backend
alembic upgrade head
```

The Docker Compose stack includes a migration step before the API and worker services.

## Testing

Install development dependencies and run the quality gates locally:

```bash
cd backend
pip install -r requirements/development.txt
ruff check app tests
python -m compileall app tests
alembic upgrade head
pytest -q
```

CI runs the same checks against PostgreSQL and Redis service containers.

## Technology stack

| Layer | Technology |
| --- | --- |
| API | FastAPI |
| Language | Python |
| Queue | Redis |
| Workers | Celery |
| Database | PostgreSQL |
| Dashboard | React + TypeScript + Vite |
| Containers | Docker |
| Web server | Nginx |
| Migrations | Alembic |
| Observability | Prometheus client |
| Quality | Pytest + Ruff + GitHub Actions |

## Engineering roadmap

### Phase 1 — Foundation ✅
Core FastAPI, PostgreSQL, Redis, Celery, configuration, and container scaffolding.

### Phase 2 — Job Processing ✅
Job creation, persistence, asynchronous execution, result handling, and API endpoints.

### Phase 3 — Reliability ✅
Retries, attempts, priorities, backoff, idempotency, cancellation, and migration support.

### Phase 4 — Operations ✅
Worker registry, heartbeats, health tracking, and operational metrics.

### Phase 5 — Dashboard & Integration ✅
React dashboard, live polling, job inspection, worker visibility, search/filtering, cancellation controls, and production frontend containerization.

### Phase 6 — Engineering Hardening ✅
Authentication/RBAC, request correlation, structured logging, explicit lifecycle transitions, idempotency conflict protection, per-job timeout controls, retryable/permanent error classification, database constraints, migration validation, and automated CI quality gates.

### Next — Production validation
End-to-end distributed execution tests, worker failure/recovery tests, load testing, reproducible frontend builds, and deployment-specific hardening.

## Development note

JobFlow is a learning-focused systems project. The repository is designed to demonstrate distributed background processing concepts rather than pretend that local Docker Compose is a complete production deployment.

## Author

**Akhil Raj**
