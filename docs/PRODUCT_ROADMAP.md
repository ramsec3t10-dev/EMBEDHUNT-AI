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

### Phase 0: Stabilize Foundation

- Fix text encoding corruption across docs and comments.
- Repair CI and local test setup.
- Add proper Alembic migrations.
- Add missing Celery app or remove the worker until implemented.
- Remove unsafe default secrets from production paths.

### Phase 1: Job Data Backbone

- Add source, company, job scan, blacklist, and job match models.
- Add CRUD APIs for configured companies and search preferences.
- Add a connector interface with a mock connector for tests.
- Add scheduled ingestion through Celery.

### Phase 2: Matching MVP

- Add candidate profile and resume selection APIs.
- Implement deterministic scoring first.
- Add AI embedding scoring behind a feature flag.
- Store match explanations and score components.

### Phase 3: Android MVP

- Build dashboard, new jobs, approval actions, blacklist, and history.
- Use backend APIs only; avoid business logic duplication in the app.
- Add push notification hooks after the workflow is stable.

### Phase 4: Source Expansion

- Add high-value connectors one by one.
- Track source reliability, latency, duplicates, and failure rates.
- Add admin controls to disable noisy sources.

### Phase 5: Application Assistant

- Generate cover letters.
- Prepare application packets.
- Add manual approval gate.
- Add browser automation only where compliant and user-authorized.

## Engineering Principles

- Build narrow vertical slices that are runnable and tested.
- Keep connectors isolated and disposable.
- Avoid hardcoding company/source lists in business logic.
- Treat job applications as auditable financial-grade workflows.
- Do not auto-submit applications without explicit user approval.
- Prefer boring, observable backend systems over clever hidden automation.

## Immediate Next Slice

The next useful implementation slice is the job ingestion foundation:

1. Create models for `JobSource`, `CompanyWatchlist`, `JobScanRun`, `JobListing`, `JobMatch`, and `CompanyBlacklist`.
2. Add Alembic migration support.
3. Add a connector interface plus one mock connector.
4. Add an API endpoint to list new matched jobs for the dashboard.
5. Add tests that run in CI without hitting external job sites.
