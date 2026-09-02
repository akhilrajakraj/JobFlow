# JobFlow

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

JobFlow is a learning-focused backend systems project designed around a common production requirement: executing long-running or resource-intensive work outside the request-response lifecycle of an API.

Instead of making an API client wait for a task to finish, JobFlow accepts a job, places it on a queue, processes it asynchronously through workers, persists execution state, and exposes the job lifecycle through an API and dashboard.

The project is intentionally designed to explore reliable background processing, queue-based architectures, failure handling, retries, task prioritization, worker health, and system observability.

## Core Workflow

```text
Client
  │
  ▼
REST API
  │
  ├──────────────► PostgreSQL
  │
  ▼
Redis Queue
  │
  ▼
Celery Workers
  │
  ├── Execute Job
  │
  ├── Retry on Failure
  │
  └── Record Result
  │
  ▼
Job Status / Dashboard
```

## Planned Capabilities

- Asynchronous job submission and execution
- Job lifecycle and status tracking
- Persistent job results and error information
- Execution-attempt history
- Configurable retry handling
- Priority-based job processing
- Worker registration and health monitoring
- Job execution metrics and history
- REST API for application integration
- Web dashboard for operational visibility
- Containerized local development
- Automated testing and CI

> Features are being implemented incrementally. The repository currently represents the foundation of the project rather than a completed production service.

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
├── .github/                 # CI workflows
├── backend/                 # API, domain logic, models, schemas, tests
├── frontend/                # React dashboard
├── infrastructure/          # Docker, Nginx, PostgreSQL and Redis configuration
├── docs/                    # Architecture, API and technical decisions
├── scripts/                 # Development and operational scripts
├── .env.example             # Environment variable template
├── Makefile                 # Development command shortcuts
├── LICENSE
└── README.md
```

## Engineering Goals

JobFlow is being built with emphasis on:

- **Separation of concerns** — API, business logic, persistence, and workers remain independently organized.
- **Reliability** — failed jobs should be observable, retryable, and traceable.
- **Asynchronous execution** — expensive work should not unnecessarily block API requests.
- **Observability** — job and worker state should be visible rather than hidden inside logs.
- **Testability** — core behavior should be covered by automated tests.
- **Containerized development** — supporting services should be reproducible through Docker.
- **Clear architecture** — design decisions and system boundaries should be documented as the project evolves.

## Development Status

🚧 **JobFlow is under active development.**

The project is being developed incrementally, starting with the core job-submission and asynchronous execution pipeline before adding reliability and operational features.

## Roadmap

### Phase 1 — Foundation

- [x] Repository structure
- [ ] FastAPI application setup
- [ ] PostgreSQL integration
- [ ] Redis integration
- [ ] Celery integration
- [ ] Basic Docker environment

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

JobFlow is intended to go beyond a conventional CRUD application. The project focuses on understanding what happens after an API receives work that cannot or should not be completed during the original request.

It provides a practical environment for exploring concepts such as message queues, background workers, retries, task state machines, concurrency, failure handling, service health, and distributed application architecture.

## Learning Outcomes

Through the project, the main areas of focus are:

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

## License

This project is licensed under the MIT License. See [`LICENSE`](LICENSE) for details.

## Author

**Akhil Raj**

GitHub: [@akhilrajakraj](https://github.com/akhilrajakraj)
