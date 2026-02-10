# 🚀 AI Lead Intelligence Engine

A production-style distributed backend system that
automatically collects, enriches, analyzes, and scores business 
leads using AI.

---

![Python](https://img.shields.io/badge/python-3.10+-blue.svg)
![Django](https://img.shields.io/badge/django-5.2-green.svg)
![Celery](https://img.shields.io/badge/celery-async-red.svg)

## 📋 Overview

The AI Lead Intelligence Engine is a distributed backend platform 
that processes lead information asynchronously, gathers real-time
web intelligence, and delivers detailed professional profiles via 
email. This system functions as an intelligent research assistant that provides actionable insights about prospects.

### 🎯 Key Features

- **REST API Lead Ingestion** - Submit leads via standardized endpoints
- **Asynchronous Processing** - Non-blocking background enrichment using Celery + Redis
- **Multi-Source Intelligence** - Combines LinkedIn, company websites, and recent news
- **AI-Powered Analysis** - Uses Groq LLM for structured profile generation
- **Entity Resolution** - Filters irrelevant results and handles name ambiguity
- **Automated Delivery** - Sends intelligence reports via SMTP email
- **Idempotent Processing** - Prevents duplicate enrichment
- **Status Tracking** - Full lifecycle monitoring (NEW → ENRICHING → ENRICHED → COMPLETED)
## 🏗️ Architecture

```
┌─────────────┐
│   Client    │
│  (Postman)  │
└──────┬──────┘
       │
       ▼
┌─────────────────┐
│  Django REST    │
│      API        │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│     MySQL       │
│ (Lead Storage)  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Redis Queue    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Celery Workers  │
│  (Async Tasks)  │
└────────┬────────┘
         │
    ┌────┴────┐
    ▼         ▼
┌────────┐ ┌────────┐
│ Tavily │ │  Groq  │
│  API   │ │  LLM   │
└────┬───┘ └───┬────┘
     │         │
     └────┬────┘
          ▼
   ┌──────────────┐
   │ Profile      │
   │ Generation   │
   └──────┬───────┘
          │
          ▼
   ┌──────────────┐
   │ Gmail SMTP   │
   │  Delivery    │
   └──────────────┘
```

## 🛠️ Tech Stack

| Component | Technology |
|-----------|-----------|
| **Backend Framework** | Django 5.2 + Django REST Framework |
| **Database** | MySQL 8.0 |
| **Message Broker** | Redis |
| **Task Queue** | Celery |
| **Web Enrichment** | Tavily API |
| **AI/LLM** | Groq (LLaMA 3.1) |
| **Email Delivery** | SMTP (Gmail) |
| **Environment Management** | python-dotenv |

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- MySQL 8.0+
- Redis Server
- Gmail Account with App Password

## 📡 API Usage

### Create Lead

**Endpoint:** `POST /api/leads/`

**Request Body:**
```json
{
  "name": "Satya Nadella",
  "company": "Microsoft",
  "email": "example@email.com",
  "linkedin_url": "https://www.linkedin.com/in/satyanadella"
}
```
**Response:**
```json
{
  "id": 1,
  "name": "Satya Nadella",
  "company": "Microsoft",
  "email": "example@email.com",
  "linkedin_url": "https://www.linkedin.com/in/satyanadella",
  "status": "NEW",
  "created_at": "2026-02-09T10:30:00Z"
}
```

### Status Lifecycle

```
NEW → ENRICHING → ENRICHED → COMPLETED
```

- **NEW**: Lead submitted, queued for processing
- **ENRICHING**: Tavily gathering web intelligence
- **ENRICHED**: Data collected, ready for AI analysis
- **COMPLETED**: Intelligence report generated and emailed

## 🔒 Security Best Practices

✅ **API Keys** - Stored in `.env`, never committed to Git  
✅ **Gmail Security** - Uses App Passwords instead of account credentials  
✅ **Email Uniqueness** - Prevents duplicate lead processing  
✅ **Environment Isolation** - Virtual environment for dependencies  
✅ **Gitignore** - Excludes `.env` and sensitive files  
✅ Idempotent Celery tasks to avoid duplicate enrichment  
✅ Status-based state machine (NEW → ENRICHING → ENRICHED → COMPLETED)  


## 📊 Engineering Scope

- **Lines of Code**: ~500
- **API Endpoints**: 1 (expandable)
- **Background Tasks**: 1 main enrichment pipeline
- **External APIs**: 2 (Tavily, Groq)
- **Database Models**: 1 core Lead model


## 📧 Contact

Karthika U - [LinkedIn](https://www.linkedin.com/in/karthika-u-40464722a/) - [GitHub](https://github.com/karthika-u07)

Project Link: [https://github.com/yourusername/ai-lead-intelligence-engine](https://github.com/yourusername/ai-lead-intelligence-engine)

---

⭐ **If you found this project helpful, please consider giving it a star!**

---

## 🔮 Future Enhancements

- [ ] Admin dashboard for lead management
- [ ] PDF report export
- [ ] Confidence scoring for enrichment quality
- [ ] Webhook notifications
- [ ] Batch CSV upload
- [ ] Docker containerization
- [ ] API authentication and rate limiting
- [ ] GraphQL API layer
- [ ] Integration with CRM systems
- [ ] Advanced analytics dashboard