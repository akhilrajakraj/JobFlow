# JobFlow — Distributed Background Job Processing Platform

> A production-oriented distributed background job processing platform for submitting, executing, tracking, and monitoring asynchronous workloads.

## Current status

JobFlow now includes the backend execution pipeline, reliability controls, worker monitoring, and a React operational dashboard.

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
- Job cancellation through Celery task revocation
- Worker registration and heartbeat monitoring
- Worker health and operational metrics
- React + TypeScript dashboard with live polling
- Job search and status filtering
- Job detail drawer with results/errors
- Worker status panel
- Production frontend container served by Nginx
- Docker Compose integration for the dashboard
- Alembic migrations for persistent schema changes

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

## API examples

Submit a job:

```bash
curl -X POST http://localhost:8000/api/v1/jobs \
  -H 'Content-Type: application/json' \
  -d '{"task_type":"sum","payload":{"numbers":[10,20,30]},"priority":8}'
```

List jobs:

```bash
curl http://localhost:8000/api/v1/jobs
```

List workers:

```bash
curl http://localhost:8000/api/v1/workers
```

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

### Next — Engineering hardening
Automated integration tests, authentication/authorization, stronger per-job timeout enforcement, retryable-vs-permanent error classification, structured logging, Prometheus/Grafana integration, and production deployment hardening.

## Development note

JobFlow is a learning-focused systems project. The repository is designed to demonstrate distributed background processing concepts rather than pretend that local Docker Compose is a complete production deployment.

## Author

**Akhil Raj**
