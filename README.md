# 🚀 AI Lead Intelligence Engine

A **production-grade distributed backend system** deployed on AWS EC2 that automatically ingests, enriches, and analyzes business leads using multi-source AI intelligence — with full CI/CD, containerization, JWT auth, and async task processing.

---

![Python](https://img.shields.io/badge/python-3.10+-blue.svg)
![Django](https://img.shields.io/badge/django-5.2-green.svg)
![Celery](https://img.shields.io/badge/celery-async-red.svg)
![Docker](https://img.shields.io/badge/docker-compose-2496ED.svg)
![AWS](https://img.shields.io/badge/AWS-EC2%20%7C%20S3%20configured-FF9900.svg)
![CI/CD](https://img.shields.io/badge/CI%2FCD-GitHub%20Actions-2088FF.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

---

## ❗ Problem Statement

Sales and growth teams often receive raw lead data with minimal context. Manually researching each lead — LinkedIn profile, company background, recent news — takes **15–30 minutes per lead**, making the process inefficient and non-scalable at volume.

This system automates the **entire enrichment pipeline**: it accepts a raw lead, gathers real-time web intelligence from multiple sources, generates a structured AI-powered professional report using an LLM, and delivers it via email — all **without blocking the API response**.

---

## 📋 Overview

The AI Lead Intelligence Engine is a **production-deployed, containerized** backend platform built with a **producer-consumer architecture**. The API returns immediately (HTTP 201) while the full AI pipeline runs asynchronously in the background via Celery workers, making it non-blocking and horizontally scalable.

---
## 🌐 Live Deployment

- API Base URL: http://13.233.174.166
- Health Check: http://13.233.174.166/
### 🎯 Key Features

- **JWT-Protected REST API** — Secure lead ingestion with stateless token-based auth
- **Idempotent Processing** — Header-level idempotency key prevents duplicate enrichment under retries
- **Async AI Pipeline** — Non-blocking enrichment via Celery + Redis message broker
- **Multi-Source Intelligence** — Parallel Tavily searches across LinkedIn, portfolio, and company news
- **LLM Report Generation** — Groq (LLaMA 3.1 8B) generates structured 6-section intelligence reports
- **State Machine Lifecycle** — Full observability: `NEW → ENRICHING → ENRICHED → EMAIL_SENT`
- **Automated Email Delivery** — SMTP-based delivery of AI reports via Gmail
- **Containerized Deployment** — 5-service Docker Compose stack (Django, Nginx, Celery, Redis, MySQL)
- **CI/CD Pipeline** — Auto-deploy to AWS EC2 on every push to `main` via GitHub Actions

---

## 🏗️ System Architecture

### High-Level Design (HLD)

```
Client (Postman / Frontend)
         │
         ▼
  ┌─────────────┐
  │    Nginx    │  ← Reverse Proxy, Static Files (Port 80)
  └──────┬──────┘
         │
         ▼
  ┌──────────────────┐
  │ Gunicorn + Django│  ← REST API, JWT Auth, Serializers
  └───────┬──────────┘
          │
    ┌─────┴──────┐
    ▼            ▼
┌────────┐  ┌─────────┐
│ MySQL  │  │  Redis  │  ← Persistent Store + Message Broker
└────────┘  └────┬────┘
                 │
                 ▼
         ┌──────────────┐
         │ Celery Worker│  ← Async Task Executor
         └──────┬───────┘
                │
        ┌───────┴────────┐
        ▼                ▼
  ┌──────────┐    ┌──────────┐
  │  Tavily  │    │   Groq   │  ← External AI Services
  │   API    │    │   LLM    │
  └──────────┘    └────┬─────┘
                       │
                 ┌─────▼──────┐
                 │ Gmail SMTP │  ← Email Delivery
                 └────────────┘
```

### Low-Level Design (LLD) — Lead State Machine

```
POST /api/leads/
       │
       ▼
[Idempotency Check] ──► Already exists? Return 200
       │
       ▼
[Serializer Validation]
       │
       ▼
[DB Save — status: NEW]  ◄─── @transaction.atomic
       │
       ▼
[enrich_lead_task.delay(lead_id)]  ◄── Fire & Forget
       │
       ▼
  Return HTTP 201 ◄──────────────── API response ends here

────── Background (Celery) ──────────────────────────────

status: ENRICHING
  │
  ├── Tavily Search 1: LinkedIn profile
  ├── Tavily Search 2: GitHub / Portfolio
  └── Tavily Search 3: Company news

status: ENRICHED  → summary stored in DB
  │
  └── Groq LLaMA 3.1 → Generate 6-section report

status: EMAIL_SENT  → report emailed via SMTP
```

### 🔄 Request Flow (Sequence Diagram)

```
Client     Nginx    Django API    MySQL     Redis    Celery Worker  Tavily   Groq   Gmail
  │          │           │          │         │            │           │        │       │
  ├─POST ───►│           │          │         │            │           │        │       │
  │          ├──────────►│          │         │            │           │        │       │
  │          │      Check idempotency          │            │           │        │       │
  │          │           ├─────────►│          │            │           │        │       │
  │          │           │◄─────────│          │            │           │        │       │
  │          │           │  Save lead (atomic) │            │           │        │       │
  │          │           ├─────────►│          │            │           │        │       │
  │          │           │     Queue task      │            │           │        │       │
  │          │           ├──────────────────── ►│           │           │        │       │
  │◄─201─────┤◄──────────│          │          │            │           │        │       │
  │          │           │          │          │  Dequeue   │           │        │       │
  │          │           │          │          ├───────────►│           │        │       │
  │          │           │          │          │            ├──search──►│        │       │
  │          │           │          │          │            │◄─results──┤        │       │
  │          │           │          │          │            ├──generate──────────►       │
  │          │           │          │          │            │◄──report───────────┤       │
  │          │           │          │          │            ├──send email─────────────── ►│
  │          │           │          │◄─────────────────────┤            │        │       │
```

---

## 🛠️ Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| **Backend Framework** | Django 5.2 + DRF | REST API, ORM, admin |
| **Authentication** | JWT (simplejwt) | Stateless token auth |
| **Database** | MySQL 8.0 (containerized) | Persistent lead storage — designed to migrate to RDS |
| **Message Broker** | Redis 7 | Celery task queue |
| **Task Queue** | Celery | Async background processing |
| **Web Enrichment** | Tavily API | Multi-source web search |
| **LLM** | Groq (LLaMA 3.1 8B) | Intelligence report generation |
| **Email** | SMTP / Gmail | Report delivery |
| **Web Server** | Nginx + Gunicorn | Reverse proxy + WSGI |
| **Containerization** | Docker + Docker Compose | 5-service stack |
| **Cloud** | AWS EC2 (ap-south-1) | Production deployment |
| **CI/CD** | GitHub Actions | Auto-deploy on push to main |
| **Env Management** | python-dotenv | Secrets via `.env` |

---

## 📈 Performance & Impact

| Metric | Detail |
|---|---|
| **API Response Time** | Returns in <100ms — 90%+ reduction vs synchronous approach |
| **Non-blocking Throughput** | API accepts new leads while prior enrichments are still running |
| **Parallel Enrichment** | Redis queue enables multiple workers to process leads concurrently |
| **Retry Safety** | Idempotency key + auto-retry (3×) ensures zero duplicate processing under failures |
| **Horizontal Scalability** | Additional Celery workers can be added with zero code changes |

---

## ⚖️ Design Decisions & Trade-offs

| Decision | Chosen | Alternative | Reason |
|---|---|---|---|
| **Task queue** | Celery + Redis | Synchronous processing | Avoids blocking HTTP requests during slow AI calls |
| **Database** | MySQL | NoSQL (MongoDB) | Strong consistency required for idempotency and atomic transactions |
| **Email delivery** | SMTP / Gmail | AWS SES | Simpler MVP setup; SES is a natural upgrade path at scale |
| **Orchestration** | Docker Compose | Kubernetes | Single-node deployment; K8s adds unnecessary complexity at this scale |
| **LLM provider** | Groq (LLaMA 3.1) | OpenAI GPT-4 | Faster inference, lower cost for structured report generation |
| **Auth strategy** | JWT | Session auth | Stateless — scales horizontally without a shared session store |

---

## 🚨 Failure Handling

- **Celery auto-retries** — Tasks automatically retry up to **3× with 5-second backoff** on any exception
- **Idempotency** — Duplicate API calls with the same `Idempotency-Key` return the cached response, preventing re-queuing
- **Atomic transactions** — `@transaction.atomic` ensures lead DB write and task dispatch succeed or fail together; no orphaned tasks
- **Status observability** — `FAILED` status allows identifying leads that exhausted all retries
- **Future**: Dead-letter queue (DLQ) + Sentry alerting for permanently failed jobs

---

## 📊 Scalability

- **Horizontal worker scaling** — Spin up additional Celery workers: `docker-compose up --scale worker=N`
- **Redis as distributed broker** — All workers share the same queue; no code changes needed to scale out
- **Stateless API** — JWT auth means any number of Django/Gunicorn instances can run behind Nginx
- **Nginx load balancing** — Can distribute traffic across multiple `web` containers with one config change
- **Future path**: Redis Cluster for HA, AWS SES for email at volume, Kubernetes for auto-scaling

---

## 🚀 Getting Started

### Prerequisites

- Docker & Docker Compose
- AWS EC2 instance (for deployment)
- Tavily API key
- Groq API key
- Gmail account with App Password

### 1. Clone the Repository

```bash
git clone https://github.com/karthika-u07/ai-lead-intelligence-engine.git
cd ai-lead-intelligence-engine
```

### 2. Configure Environment Variables

```bash
cp .env.example .env
```

Edit `.env`:

```env
MYSQL_DATABASE=ai_leads_db
MYSQL_USER=root
MYSQL_ROOT_PASSWORD=your_password
MYSQL_HOST=db
MYSQL_PORT=3306

GROQ_API_KEY=your_groq_key
TAVILY_API_KEY=your_tavily_key

EMAIL_HOST_USER=your_email@gmail.com
EMAIL_HOST_PASSWORD=your_app_password
```

### 3. Start All Services

```bash
docker-compose up -d --build
```

This spins up: **Django API + Nginx + Celery Worker + Redis + MySQL**

### 4. Run Migrations

```bash
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
```

---

## 📡 API Reference

### Authentication

```http
POST /api/token/
Content-Type: application/json

{
  "username": "admin",
  "password": "your_password"
}
```

Response:
```json
{
  "access": "<access_token>",
  "refresh": "<refresh_token>"
}
```

---

### Create Lead

```http
POST /api/leads/
Authorization: Bearer <access_token>
Idempotency-Key: <unique-uuid>
Content-Type: application/json

{
  "name": "Satya Nadella",
  "company": "Microsoft",
  "email": "example@email.com",
  "linkedin_url": "https://www.linkedin.com/in/satyanadella"
}
```

**Response (201 Created):**
```json
{
  "id": 1,
  "name": "Satya Nadella",
  "company": "Microsoft",
  "email": "example@email.com",
  "status": "NEW",
  "company_summary": null,
  "generated_email": null,
  "created_at": "2026-03-27T10:30:00Z"
}
```

### API Flow Explanation

1. Client sends `POST /api/leads/` with **JWT token** + **Idempotency-Key** header
2. Server checks if this `Idempotency-Key` already exists → returns cached response if so
3. Serializer validates the payload (name, company, email required)
4. Lead saved to MySQL with `status: NEW` inside `@transaction.atomic`
5. `enrich_lead_task.delay(lead_id)` pushes the task to Redis queue
6. **API responds immediately with HTTP 201** — client is never blocked
7. Celery worker picks up the task and runs Tavily + Groq asynchronously
8. Lead `status` updates progressively: `ENRICHING → ENRICHED → EMAIL_SENT`

> The API never waits for AI processing. The full enrichment pipeline runs entirely in the background.

---

### Lead Status Lifecycle

| Status | Meaning |
|---|---|
| `NEW` | Lead submitted, Celery task queued |
| `ENRICHING` | Tavily gathering web intelligence |
| `ENRICHED` | Web data collected, LLM generating report |
| `EMAIL_SENT` | Report generated and delivered |
| `FAILED` | Pipeline error — auto-retried up to 3× |

---

## 🐳 Docker Services

```
web      → Django + Gunicorn     (internal port 8000)
nginx    → Reverse proxy         (public port 80)
worker   → Celery task executor  (no exposed port)
redis    → Message broker        (internal port 6379)
db       → MySQL 8               (internal port 3306, persistent volume)
```

---

## ⚙️ CI/CD Pipeline

Automated deployment via **GitHub Actions** on every push to `main`:

```
Push to main
     │
     ▼
GitHub Actions (ubuntu-latest)
     │
     └── SSH into EC2
           ├── git pull
           ├── docker-compose down
           └── docker-compose up -d --build
```

Secrets managed via **GitHub Secrets**: `EC2_HOST`, `EC2_USER`, `EC2_KEY` — never stored in code.

---

## ☁️ AWS Architecture

The system is deployed on **AWS EC2** using Docker Compose. All services run as containers on a single instance, with Nginx as the only publicly exposed entry point.

### Current Setup

| Component | Detail |
|---|---|
| **EC2 Instance** | Hosts the full Docker Compose stack (Django, Celery, Redis, MySQL, Nginx) |
| **Elastic IP** | Stable public IP for consistent API access |
| **Security Groups** | Port 80 open (HTTP via Nginx), Port 22 restricted (SSH for CI/CD), all internal ports (8000, 6379, 3306) **not publicly exposed** |
| **MySQL** | Runs as a Docker container — designed so migrating to RDS requires only env variable changes |
| **S3** | Configured via `django-storages` + `boto3` but not actively used — ready to store generated reports in future |

### Security Group Rules

```
Port 80  (HTTP)  → Public       ← Nginx entry point
Port 22  (SSH)   → Restricted   ← GitHub Actions CI/CD only
Port 8000        → Internal     ← Django/Gunicorn (not exposed)
Port 6379        → Internal     ← Redis (not exposed)
Port 3306        → Internal     ← MySQL (not exposed)
```

### Deployment Flow

```
Developer pushes to GitHub (main branch)
         │
         ▼
GitHub Actions triggers workflow
         │
         ▼
SSH into EC2 (using stored secrets)
         │
         ├── git pull
         ├── docker-compose down
         └── docker-compose up -d --build
```

### Honest Assessment & Migration Path

> The current setup uses **containerized MySQL** (not RDS) for simplicity and faster iteration. The system is architected so that switching to AWS RDS requires **only environment variable changes** — no code modifications. Similarly, S3 is pre-configured and can start storing reports with zero architectural changes.

### 🔮 Future AWS Architecture (Production Scale)

```
Internet
    │
    ▼
Application Load Balancer (ALB)
    │
    ├──► Django Pods (Auto Scaling Group)
    │
    ├──► Celery Workers (scaled independently)
    │
    ├──► ElastiCache (Managed Redis)
    │
    ├──► RDS MySQL (Multi-AZ, managed backups)
    │
    └──► S3 (report storage + static files)
         + CloudWatch (logging/monitoring)
         + AWS SES (scalable email delivery)
```

| Current | Future (Scalable) |
|---|---|
| MySQL container | AWS RDS (managed, Multi-AZ) |
| Redis container | AWS ElastiCache |
| SMTP / Gmail | AWS SES |
| Docker Compose | Kubernetes (EKS) |
| Single EC2 | Auto Scaling Group + ALB |
| No monitoring | CloudWatch + Sentry |

---

## 🔒 Security

- ✅ JWT authentication on all endpoints (1hr access / 1 day refresh)
- ✅ All secrets in `.env`, never committed to Git
- ✅ Gmail App Passwords — not account credentials
- ✅ Idempotency key prevents duplicate processing on retries
- ✅ `@transaction.atomic` ensures DB write + task dispatch are consistent
- ✅ `DEBUG = False` in production
- ✅ Nginx as the only public-facing layer; Gunicorn is internal only

---

## 📊 Engineering Scope

| Metric | Value |
|---|---|
| Docker Services | 5 |
| API Endpoints | 3 (home, token, leads) |
| Async Pipeline Stages | Search ×3 + LLM + Email |
| External APIs | 2 (Tavily, Groq) |
| Celery Auto-Retries | 3× with 5s backoff |
| Cloud | AWS EC2 (ap-south-1) |
| Lines of Code | ~600 |

---

## 🧠 Key Learnings

- Designing **non-blocking APIs** with async task queues — decoupling request handling from business logic
- Implementing **idempotency in distributed systems** to safely handle retries and duplicate requests
- Building **LLM pipelines** into production backend workflows with structured prompt engineering
- Deploying **multi-container production systems** using Docker Compose + Nginx + Gunicorn
- Automating deployments with **GitHub Actions CI/CD** and SSH-based EC2 delivery
- Applying **state machine patterns** to model complex lifecycle workflows in relational databases

---

## 🎥 Demo

- API tested via **Postman** with JWT auth + Idempotency-Key header
- AI-enriched intelligence reports **delivered via email** with 6-section structured output
- Full system running live on **AWS EC2** (ap-south-1)

*(Screenshots / Postman collection coming soon)*

---

## 🔮 Future Enhancements

### API & Features
- [ ] `GET /api/leads/{id}/` — Poll lead enrichment status in real time
- [ ] Webhook notifications on enrichment completion
- [ ] Batch CSV upload for bulk lead processing
- [ ] PDF report export and download
- [ ] Confidence scoring for enrichment quality
- [ ] Admin dashboard for lead management
- [ ] CRM integration (Salesforce, HubSpot)

### Reliability & Observability
- [ ] Sentry + Dead-letter queue (DLQ) for failed job alerting
- [ ] CloudWatch logging and metrics
- [ ] HTTPS via Certbot / Let's Encrypt on Nginx

### AWS Migration Path
- [ ] MySQL container → **AWS RDS** (managed DB, automated backups, Multi-AZ)
- [ ] Redis container → **AWS ElastiCache** (managed, high availability)
- [ ] SMTP → **AWS SES** (scalable, deliverability at volume)
- [ ] S3 → activate for generated report storage (already configured)

### Scale-Out Architecture
- [ ] **Kubernetes (EKS)** for container orchestration and auto-scaling
- [ ] **Application Load Balancer (ALB)** for traffic distribution
- [ ] **Auto Scaling Groups** for EC2 scaling under load
- [ ] **Kafka** for large-scale event streaming (replace Redis queue)

---

## ☸️ Kubernetes Migration Plan

The current Docker Compose setup maps naturally to Kubernetes — each service becomes a Kubernetes resource:

```
Docker Compose         →    Kubernetes
─────────────────────────────────────────
web (Django)           →    Deployment (N replicas)
worker (Celery)        →    Deployment (scaled by queue depth)
redis                  →    ElastiCache or StatefulSet
db (MySQL)             →    AWS RDS (recommended)
nginx                  →    Ingress Controller
```

**Benefits of migrating to Kubernetes:**
- Horizontal auto-scaling of Django and Celery independently
- Self-healing — crashed pods restart automatically
- Rolling deployments with zero downtime
- Better resource utilization across nodes

> This system is **Kubernetes-ready by design** — stateless API, containerized services, and environment-variable-driven config mean migration requires infrastructure changes, not application code changes.

---

## 📁 Project Structure

```
ai-lead-intelligence-engine/
├── .github/
│   └── workflows/
│       └── deploy.yml          # GitHub Actions CI/CD
├── ai_lead_enrichment/
│   ├── __init__.py             # pymysql compatibility shim
│   ├── celery.py               # Celery app bootstrap
│   ├── settings.py             # Django config (DB, JWT, Celery, Email)
│   ├── urls.py                 # Root URL routing
│   ├── asgi.py
│   └── wsgi.py
├── leads/
│   ├── models.py               # Lead model + status state machine
│   ├── serializers.py          # Input validation + read-only fields
│   ├── views.py                # LeadCreateAPIView + idempotency logic
│   ├── tasks.py                # Celery enrichment pipeline
│   └── urls.py                 # App-level URL routing
├── nginx/
│   └── default.conf            # Reverse proxy + static file config
├── docker-compose.yml          # 5-service container stack
├── Dockerfile                  # Python 3.10-slim image
├── requirements.txt
└── .env                        # Secrets (gitignored)
```

---

## 📧 Contact

**Karthika U**
- LinkedIn: [karthika-u07](https://www.linkedin.com/in/karthika-u07/)
- GitHub: [karthika-u07](https://github.com/karthika-u07)

---

⭐ If you found this project useful, consider giving it a star!
