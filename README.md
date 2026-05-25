# Marketplace Integration (Django + Celery + Redis)

A backend system designed to simulate real-world asynchronous order processing using Django, Celery, and Redis.
The project focuses on background task execution, reliability, and production-like architecture patterns.

## Key Highlights

- Asynchronous order processing with Celery + Redis
- Reliable task execution using transaction.on_commit
- Retry mechanism for transient API failures (429 / 5xx)
- JWT authentication (SimpleJWT)
- Fully tested API + background tasks (Pytest)
- Fully containerized with Docker & Docker Compose

## System Overview

When an order is created:

1. Order is saved in the database
2. After DB commit, Celery tasks are triggered
3. Each marketplace processes the order independently
4. External marketplace integrations are simulated HTTP services implemented using httpx
5. Order status is updated asynchronously (success / error)

## Tech Stack

- Python / Django / DRF
- Celery
- Redis
- PostgreSQL
- SimpleJWT
- Docker
- Pytest

## Run Locally

```
docker-compose up --build 
```

### Services included:

- Django API
- PostgreSQL
- Redis
- Celery worker

## Run tests

```
docker-compose exec api pytest
```

## Design Decisions

- transaction.on_commit ensures tasks only run after successful DB commits
- Strategy pattern for marketplace payload generation
- Celery backoff retries used for resilience (rate limits & server errors)
- Mocked external integrations for safe testing

## What This Project Demonstrates

- Designing asynchronous backend systems with Celery
- Handling distributed workflows and background processing
- Implementing retry-safe task execution
- Structuring production-like Django architectures
- Writing comprehensive tests for API + async systems