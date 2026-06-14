# EMBEDHUNT AI Phase Plan

This is the execution plan for the complete AI Job Hunter product. Work should move phase by phase, with each phase
ending in runnable, tested, reviewable code.

## Phase 1: Backend Foundation

```text
Client
   |
   v
FastAPI Gateway
   |
   +-------------------+
   |                   |
Authentication     API Router
   |                   |
   +---------+---------+
             |
             v
        Service Layer
             |
             v
      Repository Layer
             |
             v
       PostgreSQL DB
```

### Goal

Build a stable backend foundation that supports authentication, clean API routing, service/repository boundaries,
database migrations, job ingestion, and CI quality gates.

### Scope

- FastAPI app factory and middleware
- JWT authentication
- User model and auth APIs
- API router structure
- Service layer
- Repository layer
- PostgreSQL schema
- Alembic migrations
- Docker services
- CI checks
- Job ingestion foundation
- Company watchlist and blacklist
- Mock job connector for deterministic testing

### Exit Criteria

- Backend starts locally with Docker.
- Migrations create all Phase 1 tables.
- Tests pass in CI.
- Lint and formatting pass.
- Job dashboard can read mock matched jobs.
- Company/source list is configurable through DB records, not hardcoded business logic.

### Current Status

Phase 1 is in progress.

Completed:

- FastAPI foundation
- Authentication foundation
- Service/repository structure
- PostgreSQL models
- Job ingestion models
- Mock embedded job connector
- Deterministic match scorer
- Jobs API surface
- Alembic initial migration
- Initial source/company seed data
- Celery entry point
- Backend tests and lint passing locally

Remaining:

- Run full Docker stack against real PostgreSQL.
- Apply migrations online.
- Add migration command to CI.
- Add scan-run ingestion service.
- Add first real compliant connector after the mock connector.

## Phase 2: Resume Intelligence Pipeline

```text
Resume Upload
      |
      v
File Storage
      |
      v
PDF/Text Parser
      |
      v
Text Normalizer
      |
      v
Skill Extractor
      |
      v
Experience Extractor
      |
      v
AI Profile Builder
```

### Goal

Turn uploaded resumes into structured candidate intelligence that can power job matching and career guidance.

### Scope

- Resume upload API
- File validation
- Object/file storage abstraction
- PDF and text parser
- Text cleanup and normalization
- Skill extraction
- Experience extraction
- Education/certification extraction
- AI profile builder
- Resume version tracking

### Exit Criteria

- User can upload a resume.
- Resume text is extracted and normalized.
- Skills and experience are stored in structured form.
- Candidate AI profile is generated from resume data.
- Parser failures are observable and retryable.

## Phase 3: Matching and Explainable Ranking

```text
AI Profile
    |
    v
User Skills
    |
    v
Job Requirements
    |
    v
Matching Engine
    |
    v
Score Calculator
    |
    v
Explainable AI
    |
    v
Ranked Jobs
```

### Goal

Rank jobs by fit and explain why each job is recommended.

### Scope

- Candidate profile matching
- Resume-to-job matching
- Skill overlap scoring
- Experience-level scoring
- Location and salary preference scoring
- AI embedding score behind feature flag
- Explainable match reasons
- Missing skill detection
- Ranked recommendation API

### Exit Criteria

- Each job has a match score.
- Each score has a human-readable explanation.
- Jobs are ranked consistently.
- Match reasons and missing skills are stored for the dashboard.

## Phase 4: Flutter Android Product

```text
Splash
   |
   v
Login
   |
   v
Dashboard
   |
   +----------------+
   |                |
   v                v
Recommendations  Profile
   |                |
   v                v
Job Details     Career Roadmap
   |
   v
Application Queue
```

### Goal

Ship the first Android app experience around recommendations, profile, job details, and application workflow.

### Scope

- Splash
- Login
- Dashboard
- Recommendations
- Job details
- Profile
- Career roadmap
- Application queue
- Approve/reject actions
- Blacklist company action

### Exit Criteria

- Android app can authenticate with backend.
- User can view ranked recommendations.
- User can view job details.
- User can approve, reject, and blacklist.
- User can see application queue state.

## Phase 5: Career Growth Intelligence

```text
Recommendation
      |
      v
Missing Skills
      |
      v
Learning Planner
      |
      v
Interview Engine
      |
      v
Company Intelligence
      |
      v
Career Roadmap
```

### Goal

Move beyond job search into career acceleration: skill gaps, learning plans, interview prep, and company intelligence.

### Scope

- Missing skill analysis
- Learning planner
- Interview question generator
- Company intelligence summaries
- Role readiness score
- Career roadmap API
- Roadmap UI in Flutter

### Exit Criteria

- User sees missing skills for target roles.
- User receives a learning plan.
- User can generate interview prep for a job.
- Company intelligence is visible in job details.
- Career roadmap is personalized and explainable.

## Phase 6: Productionization and Release

```text
Flutter App
     |
     v
REST APIs
     |
     v
Background Scheduler
     |
     v
PostgreSQL
     |
     v
Notification Engine
     |
     v
Monitoring & Logs
     |
     v
Release APK
```

### Goal

Package the system for real-world usage with background jobs, notifications, monitoring, and Android release output.

### Scope

- Background scheduler
- Notification engine
- Monitoring and logs
- Production Docker setup
- Release configuration
- Android APK build
- Runtime configuration
- Backup and recovery plan

### Exit Criteria

- Scheduled scans run reliably.
- Notifications reach Android app.
- Logs and health checks are usable.
- Release APK is generated.
- Deployment process is documented.

## Working Rules

- Finish one vertical slice at a time.
- Do not add real external job scraping until the connector contract, retry behavior, and source compliance rules are ready.
- Keep AI features behind feature flags until deterministic fallbacks exist.
- Every phase must have tests, migrations when needed, and clear API contracts.
- Innovation should show up as explainability, automation, and user leverage, not hidden fragile behavior.
