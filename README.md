# 🚀 EMBEDHUNT AI — The Autonomous Career Engine for Embedded Engineers

> *The only platform that doesn't just find you jobs — it applies for them.*

[![Phase A](https://img.shields.io/badge/Phase%20A-Foundation-green?style=for-the-badge)]()
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110-009688?style=for-the-badge&logo=fastapi)]()
[![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python)]()
[![Flutter](https://img.shields.io/badge/Flutter-Android%20%2B%20Desktop-02569B?style=for-the-badge&logo=flutter)]()
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=for-the-badge&logo=docker)]()

---

## What is EMBEDHUNT AI?

EMBEDHUNT AI is an **autonomous, AI-native hiring platform** built exclusively for the embedded software engineering ecosystem.

While other platforms show you jobs, EMBEDHUNT AI:

1. **Monitors** 50+ job portals every 5 minutes
2. **Scores** every job against your profile (0–100 semantic match)
3. **Customizes** your resume per job automatically
4. **Generates** a tailored cover letter
5. **Fills** the application form
6. **Asks YOU** to approve (one tap)
7. **Submits** and logs everything

**You wake up to interviews, not job listings.**

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                        EMBEDHUNT AI                                  │
│                                                                      │
│  Flutter App (Android + Desktop)                                    │
│       │                                                              │
│       ▼                                                              │
│  API Gateway (FastAPI + JWT + Rate Limiting)                        │
│       │                                                              │
│  ┌────┴──────────────────────────────────────────────┐              │
│  │ Auth  │ Resume │ Jobs │ AI Match │ Interview │ Notif│             │
│  └────┬──────────────────────────────────────────────┘              │
│       │                                                              │
│  PostgreSQL │ Redis │ ChromaDB (Vector) │ MinIO (Object Store)      │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Repository Structure

```
embedhunt-ai/
├── backend/               # FastAPI backend (Phase A + B + C)
│   ├── app/
│   │   ├── core/          # Config, security, logging
│   │   ├── db/            # Database sessions, base
│   │   ├── models/        # SQLAlchemy ORM models
│   │   ├── schemas/       # Pydantic request/response schemas
│   │   ├── repositories/  # Data access layer (Repository pattern)
│   │   ├── services/      # Business logic
│   │   └── api/v1/        # FastAPI routers
│   └── tests/
├── flutter_app/           # Flutter cross-platform app (Phase D)
├── ai/                    # AI pipeline (Phase C)
├── database/              # Alembic migrations
├── deployment/            # Docker + Kubernetes
├── .github/workflows/     # CI/CD
└── docs/                  # Architecture, API docs
```

---

## Phase Roadmap

| Phase | Status | Description |
|-------|--------|-------------|
| **A — Foundation** | ✅ **COMPLETE** | Backend scaffold, Auth, DB, Logging, Docker |
| **B — Core Business** | 🔄 Next | Resume Engine, Job Engine, Search |
| **C — AI Pipeline** | ⏳ Planned | Semantic Matching, Gap Analysis, Auto-Apply |
| **D — Frontend** | ⏳ Planned | Flutter Android + Desktop App |
| **E — Production** | ⏳ Planned | CI/CD, K8s, Monitoring, Launch |

---

## Quick Start (Phase A)

### Prerequisites
- Python 3.11+
- Docker & Docker Compose
- PostgreSQL 15+

### 1. Clone & Setup

```bash
git clone https://github.com/ramsec3t10-dev/EMBEDHUNT-AI.git
cd EMBEDHUNT-AI
```

### 2. Environment Setup

```bash
cp backend/.env.example backend/.env
# Edit .env with your values
```

### 3. Run with Docker

```bash
docker-compose up --build
```

### 4. API is live at

- **API**: http://localhost:8000
- **Docs**: http://localhost:8000/docs
- **Health**: http://localhost:8000/health

### 5. Run Tests

```bash
cd backend
pip install -r requirements.txt
pytest tests/ -v
```

---

## Engineering Philosophy

- **Repository-first**: Every sprint produces committed, runnable code
- **Production from day 1**: No placeholder code, no fake progress
- **Security by design**: JWT, RBAC, audit logs baked in from the start
- **Modular**: Every service is independently testable and deployable
- **Observability**: Structured logging, correlation IDs, health endpoints from day 1

---

## Built By

EMBEDHUNT AI Engineering Team  
Version: Phase A — Foundation  
Last Updated: 2025
