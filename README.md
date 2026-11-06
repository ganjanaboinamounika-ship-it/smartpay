# SMARTPAY - Smart Payment & Fraud Detection API

A backend payment processing simulation and fraud detection platform built using **Python, FastAPI, PostgreSQL, Redis, RabbitMQ, and Celery**.

SmartPay demonstrates secure authentication, payment verification, fraud risk scoring, asynchronous webhook delivery, retry handling, and automated recovery.

> **Project type:** Educational / Academic Backend Project
> **Version:** 1.0.0

## 1. Project Overview

SmartPay simulates a digital payment processing platform that allows users to create and verify payments while applying fraud detection and risk assessment.

The platform also supports asynchronous webhook notifications, automatic retry handling, and recovery of pending webhook deliveries.

## 2. Key Features

- User registration and login
- JWT-based authentication
- Argon2 password hashing
- Role-based access control (RBAC)
- Payment creation and verification
- Mock payment gateway integration
- Fraud detection and risk scoring
- Idempotency protection
- Redis caching and rate limiting
- RabbitMQ message broker
- Celery background task processing
- Webhook registration and delivery
- Automatic webhook retry and recovery
- Payment and webhook delivery tracking
- PostgreSQL database integration
- Alembic database migrations
- Swagger/OpenAPI documentation
- Automated API testing
- Docker Compose infrastructure

## 3. Technology Stack

| Component | Technology |
|---|---|
| Backend | Python, FastAPI |
| Database | PostgreSQL |
| ORM | SQLAlchemy |
| Migrations | Alembic |
| Authentication | JWT |
| Password Security | Argon2 |
| Cache | Redis |
| Message Broker | RabbitMQ |
| Background Tasks | Celery |
| API Documentation | Swagger / OpenAPI |
| Testing | Pytest, HTTPX |
| Containerization | Docker, Docker Compose |

## 4. System Architecture

```text
                 Client / Swagger UI
                         |
                         v
                  FastAPI Backend
                         |
          +--------------+--------------+
          |              |              |
          v              v              v
      PostgreSQL       Redis        Fraud Engine
          |                             |
          +--------------+--------------+
                         |
                         v
                   RabbitMQ
                         |
                         v
                   Celery Worker
                         |
                         v
                 Webhook Delivery
                         |
                         v
                  External Receiver
```

Celery Beat periodically schedules pending webhook recovery tasks.

## 5. API Endpoints

### Authentication

| Method | Endpoint |
|---|---|
| POST | `/api/v1/auth/register` |
| POST | `/api/v1/auth/login` |
| GET | `/api/v1/auth/me` |

### Role-Based Access Control

| Method | Endpoint |
|---|---|
| GET | `/api/v1/rbac/customer-test` |
| GET | `/api/v1/rbac/admin-test` |
| GET | `/api/v1/rbac/fraud-analyst-test` |

### Payments

| Method | Endpoint |
|---|---|
| POST | `/api/v1/payments/create` |
| POST | `/api/v1/payments/verify` |
| GET | `/api/v1/payments/{payment_id}` |

### Webhooks

| Method | Endpoint |
|---|---|
| GET | `/api/v1/webhooks` |
| POST | `/api/v1/webhooks` |
| POST | `/api/v1/webhooks/{endpoint_id}/deactivate` |
| GET | `/api/v1/webhooks/deliveries` |
| GET | `/api/v1/webhooks/deliveries/{delivery_id}` |
| POST | `/api/v1/webhooks/deliveries/{delivery_id}/retry` |

### Health Checks

| Method | Endpoint |
|---|---|
| GET | `/health` |
| GET | `/health/redis` |

### Development Mock Gateway

| Method | Endpoint |
|---|---|
| POST | `/mock-gateway/payment` |

The mock gateway is available only in development and testing environments.

## 6. Installation and Setup

### Prerequisites

- Python 3.14 or compatible version
- PostgreSQL
- Redis
- RabbitMQ
- Docker Desktop
- Git

### Clone the repository

```powershell
git clone YOUR_GITHUB_REPOSITORY_URL
cd smartpay
```

### Create a virtual environment

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### Install dependencies

```powershell
pip install -r requirements.txt
```

### Configure environment variables

Create a `.env` file using `.env.example` as a reference.

Configure the required database, Redis, RabbitMQ, JWT, and webhook settings.

Never commit `.env` or actual secrets to GitHub.

### Start infrastructure

```powershell
docker compose up -d
```

### Run database migrations

```powershell
alembic upgrade head
```

## 7. Running the Application

Keep each service running in a separate PowerShell terminal.

### Terminal 1 – FastAPI

```powershell
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

### Terminal 2 – Celery Worker

```powershell
celery -A app.workers.celery_app:celery_app worker --loglevel=info --pool=solo
```

### Terminal 3 – Celery Beat

```powershell
celery -A app.workers.celery_app:celery_app beat --loglevel=info
```

### API Documentation

Open:

http://127.0.0.1:8000/docs

## 8. Testing

Run the complete test suite:

```powershell
python -m pytest -q
```

Latest verification:

```text
44 passed, 1 warning
```

Database migration verification:

```powershell
alembic current
alembic heads
```

Both should display the same migration revision.

## 9. Verified Project Results

| Verification | Result |
|---|---|
| Automated tests | 44 passed |
| PostgreSQL | Connected |
| Redis | Connected |
| RabbitMQ | Connected |
| Celery Worker | Started successfully |
| Celery Beat | Scheduled tasks successfully |
| Payment creation | HTTP 201 |
| Payment verification | HTTP 200 |
| Webhook registration | HTTP 201 |
| Webhook delivery | HTTP 200 |
| Webhook recovery task | Successful |

### Successful Payment Example

- Payment ID: 45
- Amount: INR 100.00
- Payment method: UPI
- Status: SUCCESS
- Fraud score: 0
- Risk level: LOW

### Successful Webhook Example

- Event: `payment.success`
- Delivery status: DELIVERED
- HTTP response: 200
- Delivery attempts: 1
- Maximum attempts: 5

## 10. Security Considerations

- JWT-based authentication
- Argon2 password hashing
- Role-based authorization
- Production secret validation
- Environment-based mock gateway restriction
- Idempotency protection
- Webhook delivery tracking
- Retry and recovery mechanisms

**Important:** SmartPay is an educational payment simulation. It is not a real payment processor and is not certified for PCI DSS compliance. Production use would require additional security audits, gateway integration, and operational controls.

## 11. Project Status

**Core backend implementation and initial verification completed.**

- Authentication and authorization – Completed
- Payment processing simulation – Completed
- Fraud detection – Implemented
- Idempotency – Implemented
- Redis and RabbitMQ integration – Verified
- Celery background processing – Verified
- Webhook delivery – Verified
- Automatic recovery scheduling – Verified
- Automated testing – 44 tests passed
- Deployment preparation – Pending

## 12. License

This project is developed for educational and academic purposes.
