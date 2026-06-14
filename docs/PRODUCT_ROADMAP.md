# AI Job Hunter Product Roadmap

## Product Goal

Build an AI-assisted job hunting system for embedded, firmware, systems, and hardware-adjacent software roles.
The product should discover jobs, score fit, estimate compensation, select the best resume, prepare applications,
and ask the user to approve or reject each opportunity.

## Core User Experience

The first production-grade workflow is:

1. The system scans configured job sources and company career pages.
2. New jobs are normalized into one internal job schema.
3. The AI match engine scores each job against the candidate profile and resumes.
4. The app shows high-confidence matches in an Android dashboard.
5. The user can approve, reject, blacklist a company, or track interview progress.
6. Approved applications move into an application workflow with audit history.

Example card:

```text
Qualcomm
Embedded Software Engineer

AI Match: 97
Salary: 16-22 LPA
Resume: Embedded_Systems_Primary.pdf

Approve?
```

## Source Coverage

### Search Engine Layer

Initial target sources:

- Naukri
- LinkedIn
- Indeed
- Instahyre
- Cutshort
- Wellfound
- Glassdoor
- ZipRecruiter
- Foundit
- Hirect or successors where available
- Hirist for embedded and systems roles
- Y Combinator Jobs

Implementation rule: prefer official APIs, feeds, partner integrations, user-authorized access, or compliant scraping.
Each source must be isolated behind a connector interface so unreliable or restricted sources can be disabled without
affecting the whole system.

### Company Career Scanner

Initial target companies:

- NVIDIA
- Intel
- Qualcomm
- AMD
- NXP
- Infineon
- TI
- Bosch
- Continental
- ZF
- Valeo
- Aptiv
- Magna
- Harman
- Siemens
- Honeywell
- GE
- Cisco
- Broadcom
- Marvell
- Western Digital
- Micron
- Samsung
- LG
- Sony
- MediaTek
- Renesas
- STMicroelectronics
- Analog Devices
- Microchip
- Schneider Electric
- Eaton
- ABB
- Emerson
- Philips
- Dell
- HP
- Amazon Devices
- Apple
- Google
- Meta
- Tesla
- Lucid
- Rivian

The company list must be configurable through database records or admin-managed config, not hardcoded in scanner code.

## Android Scope

Android has full product support.

Required screens:

- Dashboard
- New jobs
- AI score detail
- Resume used
- Salary estimate
- Approve or reject
- Company blacklist
- Search history
- Interview tracker

The mobile app should be operational first, not marketing-first. The dashboard should open directly into the user's
current job pipeline.

## Backend Domains

### Identity and Profile

- User account
- Candidate profile
- Skills
- Experience
- Preferences
- Location and salary expectations
- Blacklisted companies

### Resume Engine

- Resume upload
- Resume parsing
- Skill extraction
- Primary resume selection
- Resume-to-job selection
- Future: resume tailoring per approved application

### Job Ingestion

- Source connector registry
- Configurable search terms
- Scheduled scans
- Company career scanner
- Duplicate detection
- Normalized job records
- Source audit trail

### AI Match Engine

- Candidate profile embedding
- Resume embedding
- Job embedding
- Match score
- Skill gaps
- Explanation text
- Confidence score

### Salary Estimation

- Salary extraction from posting
- Market fallback range
- Currency and location normalization
- Confidence score

### Application Workflow

- New
- Approved
- Rejected
- Applied
- Interview
- Offer
- Closed

Every state transition should be auditable.

## Delivery Phases

The canonical build sequence is maintained in [PHASE_PLAN.md](PHASE_PLAN.md). The summary below is kept aligned with
that phase plan.

### Phase 1: Backend Foundation

- Fix text encoding corruption across docs and comments.
- Repair CI and local test setup.
- Add proper Alembic migrations.
- Add missing Celery app or remove the worker until implemented.
- Remove unsafe default secrets from production paths.

### Phase 2: Resume Intelligence Pipeline

- Resume upload.
- File storage.
- PDF/text parsing.
- Text normalization.
- Skill extraction.
- Experience extraction.
- AI profile builder.

### Phase 3: Matching and Explainable Ranking

- AI profile matching.
- User skills to job requirements matching.
- Score calculator.
- Explainable AI.
- Ranked jobs.

### Phase 4: Flutter Android Product

- Splash.
- Login.
- Dashboard.
- Recommendations.
- Profile.
- Job details.
- Career roadmap.
- Application queue.

### Phase 5: Career Growth Intelligence

- Missing skills.
- Learning planner.
- Interview engine.
- Company intelligence.
- Career roadmap.

### Phase 6: Productionization and Release

- Flutter app integration.
- REST API hardening.
- Background scheduler.
- PostgreSQL operations.
- Notification engine.
- Monitoring and logs.
- Release APK.

## Immediate Next Slice

Continue Phase 1 to completion:

- Add source, company, job scan, blacklist, and job match models.
- Add CRUD APIs for configured companies and search preferences.
- Add a connector interface with a mock connector for tests.
- Add scheduled ingestion through Celery.

## Engineering Principles

- Build narrow vertical slices that are runnable and tested.
- Keep connectors isolated and disposable.
- Avoid hardcoding company/source lists in business logic.
- Treat job applications as auditable financial-grade workflows.
- Do not auto-submit applications without explicit user approval.
- Prefer boring, observable backend systems over clever hidden automation.

1. Run the Docker stack against PostgreSQL.
2. Apply migrations online.
3. Add CI migration smoke test.
4. Add scan-run ingestion service.
5. Add one compliant real connector after the mock connector.
