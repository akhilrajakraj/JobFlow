# JobFlow — Distributed Background Job Processing Platform

> A production-oriented distributed background job processing platform for submitting, executing, tracking, and monitoring asynchronous workloads.

[![Status](https://img.shields.io/badge/status-in%20development-yellow)](https://github.com/akhilrajakraj/JobFlow)
[![Python](https://img.shields.io/badge/Python-3.x-blue)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/API-FastAPI-009688)](https://fastapi.tiangolo.com/)
[![Redis](https://img.shields.io/badge/Queue-Redis-DC382D)](https://redis.io/)
[![Celery](https://img.shields.io/badge/Workers-Celery-37814A)](https://docs.celeryq.dev/)
[![PostgreSQL](https://img.shields.io/badge/Database-PostgreSQL-4169E1)](https://www.postgresql.org/)
[![React](https://img.shields.io/badge/Frontend-React-61DAFB)](https://react.dev/)
[![Docker](https://img.shields.io/badge/Infrastructure-Docker-2496ED)](https://www.docker.com/)

## Overview

JobFlow is a learning-focused backend systems project built around a common production problem: executing long-running or resource-intensive work outside the API request-response lifecycle.

A client submits a job through the API. JobFlow records the job, places work onto a queue, processes it through background workers, persists execution state and results, and exposes the lifecycle through an API and web dashboard.

The project is intentionally focused on reliable asynchronous processing, queue-based architecture, retries, task prioritization, worker health, failure handling, and operational visibility.

## Architecture

```text
                         ┌─────────────────┐
                         │     Client      │
                         └────────┬────────┘
                                  │
                                  ▼
                         ┌─────────────────┐
                         │   FastAPI API   │
                         └──────┬─────┬────┘
                                │     │
                    persist     │     │ enqueue
                                ▼     ▼
                       ┌──────────┐  ┌──────────┐
                       │PostgreSQL│  │  Redis   │
                       └──────────┘  └────┬─────┘
                                          │
                                          ▼
                                  ┌──────────────┐
                                  │Celery Workers│
                                  └──────┬───────┘
                                         │
                                         ▼
                                  Execute / Retry
                                         │
                                         ▼
                                  Persist Results
                                         │
                                         ▼
                                  Dashboard / API
```

## Core Workflow

1. A client submits a job through the REST API.
2. The API creates a persistent job record.
3. The job is placed on the Redis-backed queue.
4. A Celery worker picks up the job asynchronously.
5. Execution state and attempts are tracked.
6. Successful results or failure information are persisted.
7. Retry policies can requeue failed work.
8. Clients can inspect job status and execution history through the API and dashboard.

## Planned Capabilities

- Asynchronous job submission and execution
- Job lifecycle tracking: `QUEUED`, `RUNNING`, `SUCCESS`, `FAILED`, `RETRYING`, `CANCELLED`
- Persistent results and error information
- Execution-attempt history
- Configurable retry handling with backoff
- Priority-based job processing
- Worker registration and health monitoring
- Worker heartbeat tracking
- Job execution metrics and timing information
- REST API for application integration
- React + TypeScript operational dashboard
- Containerized local development
- Automated testing and CI

> Features are being implemented incrementally. The repository currently contains the architectural foundation and scaffolding; it is not yet a completed production service.

## Technology Stack

| Layer | Technology |
| --- | --- |
| API | FastAPI |
| Language | Python |
| Task Queue | Redis |
| Background Processing | Celery |
| Database | PostgreSQL |
| Frontend | React + TypeScript |
| Containers | Docker |
| Reverse Proxy | Nginx |
| Testing | Pytest |
| CI | GitHub Actions |

## Repository Structure

```text
JobFlow/
├── .github/
│   └── workflows/                 # CI workflows (planned/added as CI evolves)
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── routes/
│   │   │   │   ├── auth.py
│   │   │   │   ├── jobs.py
│   │   │   │   └── workers.py
│   │   │   └── dependencies.py
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   ├── database.py
│   │   │   └── security.py
│   │   ├── models/
│   │   │   ├── job.py
│   │   │   ├── job_attempt.py
│   │   │   └── worker.py
│   │   ├── schemas/
│   │   │   ├── auth.py
│   │   │   └── job.py
│   │   ├── services/
│   │   │   ├── job_service.py
│   │   │   └── worker_service.py
│   │   └── main.py
│   ├── requirements/
│   │   ├── base.txt
│   │   ├── development.txt
│   │   └── production.txt
│   ├── tests/
│   │   ├── api/
│   │   ├── services/
│   │   └── worker/
│   └── Dockerfile
│
├── frontend/
│   └── src/
│       ├── components/
│       ├── hooks/
│       ├── pages/
│       ├── services/
│       ├── types/
│       ├── utils/
│       ├── App.tsx
│       └── main.tsx
│
├── infrastructure/
│   ├── compose/
│   │   ├── docker-compose.yml
│   │   └── docker-compose.dev.yml
│   ├── docker/
│   │   ├── nginx/
│   │   │   └── nginx.conf
│   │   └── postgres/
│   │       └── init/
│   └── redis/
│
├── docs/
│   ├── architecture/
│   │   └── system-overview.md
│   └── api/
│
├── scripts/
│   ├── setup.sh
│   └── health_check.sh
│
├── .env.example
├── .gitignore
├── LICENSE
├── Makefile
└── README.md
```

## Engineering Goals

JobFlow is being built with emphasis on:

- **Separation of concerns** — API, business logic, persistence, and workers are organized independently.
- **Reliability** — failed work should be observable, retryable, and traceable.
- **Asynchronous execution** — expensive work should not unnecessarily block API requests.
- **Observability** — job and worker state should be visible rather than hidden inside logs.
- **Testability** — core behavior should be covered by automated tests as implementation progresses.
- **Containerized development** — supporting services should be reproducible through Docker.
- **Clear architecture** — system boundaries and technical decisions should be documented as the project evolves.

## Roadmap

### Phase 1 — Foundation

- [x] Repository structure
- [x] Core application scaffolding
- [x] Backend package organization
- [x] Frontend scaffolding
- [x] Infrastructure configuration layout
- [ ] FastAPI application implementation
- [ ] PostgreSQL integration
- [ ] Redis integration
- [ ] Celery integration

### Phase 2 — Job Processing

- [ ] Job creation API
- [ ] Job status lifecycle
- [ ] Background task execution
- [ ] Result persistence
- [ ] Error handling

### Phase 3 — Reliability

- [ ] Retry handling
- [ ] Execution attempts
- [ ] Job priorities
- [ ] Exponential backoff
- [ ] Failure recovery

### Phase 4 — Operations

- [ ] Worker registration
- [ ] Worker heartbeats
- [ ] Worker health status
- [ ] Execution metrics
- [ ] Operational dashboard

### Phase 5 — Engineering Quality

- [ ] Automated test suite
- [ ] API documentation
- [ ] CI checks
- [ ] Production deployment documentation

## Why JobFlow?

JobFlow is designed to go beyond a conventional CRUD application. It provides a practical environment for understanding what happens after an API receives work that cannot or should not be completed during the original request.

The project provides hands-on experience with message queues, background workers, task state machines, concurrency, retries, failure handling, service health, persistence, and distributed application architecture.

## Learning Outcomes

Through JobFlow, the main areas of focus are:

- Backend API design
- Distributed task processing
- Message queues
- Worker architecture
- Database-backed state management
- Retry and failure strategies
- Service orchestration with Docker
- System observability
- Automated testing
- Production-oriented backend architecture

## Development Status

🚧 **JobFlow is under active development.**

The current repository establishes the project architecture and development foundation. Implementation will proceed incrementally, starting with the core job-submission and asynchronous execution pipeline before adding reliability and operational features.

## License

This project is licensed under the MIT License. See [`LICENSE`](LICENSE) for details.

## Author

**Akhil Raj**

GitHub: [@akhilrajakraj](https://github.com/akhilrajakraj)
