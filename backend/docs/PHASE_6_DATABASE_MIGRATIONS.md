# Phase 6 — Database Migrations

## Objectives
- Establish Alembic-based schema versioning for the backend.
- Create an initial migration that reflects the full SQLAlchemy 2.0 model schema.
- Enable safe, repeatable schema evolution for future feature work.

## What was added
- `alembic.ini` for Alembic configuration.
- `alembic/env.py` to load `app.models.Base.metadata` and apply migrations.
- `alembic/script.py.mako` as the Alembic revision template.
- `app/__init__.py` so `app` can be imported consistently from migration tooling.

## Migration workflow
1. Set `DATABASE_URL` if needed.
2. Run migrations with the Alembic CLI from the backend directory. For example:
   - On Windows: `cd backend && ..\.venv\Scripts\alembic.exe upgrade head`
   - On macOS/Linux: activate the repository virtual environment and run `cd backend && alembic upgrade head`
3. Create new schema revisions with:
   - On Windows: `cd backend && ..\.venv\Scripts\alembic.exe revision --autogenerate -m "describe change"`
   - On macOS/Linux: `cd backend && alembic revision --autogenerate -m "describe change"`

## Notes
- The Alembic environment uses `DATABASE_URL` if present, otherwise falls back to the local development URL.
- This phase establishes a repeatable schema deployment path for QA, staging, and production.
