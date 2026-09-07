# JobFlow — Distributed Background Job Processing Platform

> A learning-focused distributed job processing platform built to explore asynchronous execution, reliability, observability, authentication, and production engineering.

## Status

**Engineering hardening complete.** JobFlow currently provides a FastAPI API, PostgreSQL persistence, Redis/Celery workers, a React operational dashboard, authentication/RBAC, retry and timeout controls, worker health tracking, Prometheus-style metrics, migrations, Docker Compose orchestration, and automated CI checks.

This repository demonstrates production-oriented engineering practices, but it is intentionally not presented as a fully managed production service.

## Architecture

```text
                         ┌──────────────────────┐
                         │ React + TypeScript UI │
                         └──────────┬───────────┘
                                    │ HTTP / JSON
                                    ▼
                         ┌──────────────────────┐
                         │      FastAPI API     │
                         │ Auth • RBAC • Jobs   │
                         └──────┬─────────┬─────┘
                                │         │
                         state/data       │ enqueue
                                ▼         ▼
                       ┌────────────┐  ┌────────────┐
                       │ PostgreSQL │  │   Redis    │
                       └────────────┘  └─────┬──────┘
                                             │
                                      ┌──────▼──────┐
                                      │    Celery   │
                                      │   Workers   │
                                      └──────┬──────┘
                                             │
                                             └──────► PostgreSQL

                    /metrics ─────► Prometheus-compatible metrics
```

## Key engineering capabilities

### Job execution
- REST job submission, listing, detail, and cancellation
- Explicit lifecycle state machine
- Priority-aware Celery dispatch
- Per-job soft and hard execution limits
- Persistent execution attempts

### Reliability
- Configurable retry limits
- Exponential retry backoff
- Explicit retryable vs permanent error classification
- Idempotency keys with request fingerprints
- Database uniqueness constraints for execution attempts
- Cancellation race protection
- Worker-lost detection through Celery acknowledgements and persisted heartbeats
- Stale worker detection based on heartbeat age

### Security
- Persistent users and role-based authorization
- Signed, expiring bearer tokens
- Salted PBKDF2 password hashing
- Production configuration validation for secrets and debug mode
- Restricted CORS configuration

### Operations and observability
- Worker registration and lifecycle status
- Native Celery heartbeat persistence
- Request IDs for API tracing
- Structured JSON logging
- Prometheus-compatible counters, gauges, and histograms
- Health endpoint covering PostgreSQL and Redis

### Delivery and quality
- Alembic database migrations
- Docker Compose stack with a dedicated migration service
- CI with PostgreSQL and Redis service containers
- Dependency installation for development/testing
- Ruff linting, Python compilation checks, migration execution, and pytest
- API, authentication, security, state-machine, retry, and idempotency tests

## Run locally

Create a `.env` from `.env.example`, then start the stack:

```bash
docker compose -f infrastructure/compose/docker-compose.yml up --build
```

Open:

- Dashboard: `http://localhost:3000`
- API docs: `http://localhost:8000/docs`
- Health: `http://localhost:8000/health`
- Metrics: `http://localhost:8000/metrics`

The default development administrator is configured through `ADMIN_USERNAME` and `ADMIN_PASSWORD`. Change these values before exposing the service outside a local development environment.

## Test and lint

```bash
cd backend
pip install -r requirements/development.txt
ruff check app tests
alembic upgrade head
pytest -q
```

CI performs the same checks against real PostgreSQL and Redis service containers.

## Example API flow

Authenticate:

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"username":"admin","password":"change-me-now"}'
```

Submit a job using the returned bearer token:

```bash
curl -X POST http://localhost:8000/api/v1/jobs \
  -H 'Authorization: Bearer <TOKEN>' \
  -H 'Content-Type: application/json' \
  -H 'Idempotency-Key: demo-sum-001' \
  -d '{"task_type":"sum","payload":{"numbers":[10,20,30]},"priority":8}'
```

## Technology stack

| Layer | Technology |
| --- | --- |
| API | FastAPI |
| Language | Python 3.12 |
| Queue | Redis |
| Workers | Celery |
| Database | PostgreSQL |
| Dashboard | React + TypeScript + Vite |
| Containers | Docker + Docker Compose |
| Web server | Nginx |
| Migrations | Alembic |
| Observability | Prometheus client |
| CI | GitHub Actions |
| Testing | Pytest |

## Engineering roadmap

### Phase 1 — Foundation ✅
FastAPI, PostgreSQL, Redis, Celery, configuration, and container scaffolding.

### Phase 2 — Job Processing ✅
Persistence, asynchronous execution, result handling, and APIs.

### Phase 3 — Reliability ✅
Retries, attempts, priorities, backoff, idempotency, cancellation, and migrations.

### Phase 4 — Operations ✅
Worker registry, heartbeats, health tracking, and metrics.

### Phase 5 — Dashboard & Integration ✅
React dashboard, polling, job inspection, worker visibility, search/filtering, cancellation, and Nginx containerization.

### Phase 6 — Engineering Hardening ✅
Authentication/RBAC, explicit state transitions, timeout enforcement, retry classification, structured logging, request tracing, production configuration validation, database constraints, integration-oriented CI, and stronger automated tests.

## Engineering note

JobFlow is intentionally built as a systems-learning project. The goal is to demonstrate how a distributed background-job platform can be designed and hardened, while being explicit about the difference between production-oriented code and a production-operated service.

## Author

**Akhil Raj**
