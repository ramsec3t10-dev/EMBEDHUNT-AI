# Database Migrations

Alembic migration versions live in `database/migrations/versions`.

Run from the repository root:

```bash
alembic upgrade head
```

The Alembic environment reads `DATABASE_URL` from the backend settings and converts the asyncpg URL to a synchronous
PostgreSQL URL for migrations.
