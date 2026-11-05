\# SMARTPAY - Smart Payment \& Fraud Detection API



A production-style educational payment processing and fraud detection backend built using Python and FastAPI.



\## Project Objective



SMARTPAY simulates a digital payment platform with:



\- User authentication

\- JWT authentication

\- Role-based access control

\- Payment processing simulation

\- Fraud detection and risk scoring

\- Idempotency protection

\- Redis caching and rate limiting

\- RabbitMQ messaging

\- Celery background processing

\- Webhooks

\- Refunds

\- Audit logging

\- Admin analytics

\- Swagger/OpenAPI documentation

\- Automated testing

\- Docker deployment



\## Technology Stack



| Component | Technology |

|---|---|

| Backend | Python, FastAPI, Pydantic |

| Database | PostgreSQL, SQLAlchemy |

| Migrations | Alembic |

| Cache | Redis |

| Message Queue | RabbitMQ |

| Background Tasks | Celery |

| Authentication | JWT, Argon2 |

| Testing | Pytest, HTTPX |

| Containerization | Docker, Docker Compose |



\## Project Status



\- Phases 1-10: Completed

\- Phase 11: RabbitMQ and Celery integration - Completed

\- Phase 12: Webhooks - Upcoming



\### Phase 11 Verification



Successfully tested asynchronous task processing:



1\. Celery worker connected to RabbitMQ.

2\. A test task was submitted.

3\. The worker processed the task.

4\. The result was retrieved from Redis.



\## Running the Infrastructure



Start PostgreSQL, Redis, and RabbitMQ:



```powershell

docker compose up -d

