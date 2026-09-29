# Jewellery ERP — FastAPI Backend

## Overview

This is the FastAPI backend for the multi-tenant Jewellery ERP SaaS platform.

- **Framework:** FastAPI 0.115
- **Database ORM:** SQLAlchemy 2.x
- **Migrations:** Alembic
- **Database:** Supabase PostgreSQL
- **Auth:** Supabase JWT verification

---

## Local Development Setup

### Prerequisites

- Python 3.12+
- pip

### 1. Create a virtual environment

```bash
cd backend
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (macOS/Linux)
source venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment

```bash
cp .env.example .env
```

Edit `.env` with your actual values:

| Variable | Where to find it | Required |
|---|---|---|
| `DATABASE_URL` | Supabase → Project Settings → Database → Connection String (Transaction) | ✅ |
| `SUPABASE_URL` | Supabase → Project Settings → API → Project URL | ✅ |
| `SUPABASE_JWT_SECRET` | Supabase → Project Settings → API → JWT Secret | ✅ |
| `SUPABASE_SERVICE_ROLE_KEY` | Supabase → Project Settings → API → service_role key | ✅ |
| `SUPER_ADMIN_EMAIL` | Your email address | ✅ |
| `SECRET_KEY` | Generate with: `python -c "import secrets; print(secrets.token_hex(32))"` | ✅ |

> ⚠️ **NEVER commit `.env` to version control.** The `.gitignore` excludes it.

### 4. Run database migrations

```bash
alembic upgrade head
```

This will:
- Create all tables in your Supabase database
- Set up constraints, indexes, and triggers
- Seed system roles and permissions

### 5. Start the development server

```bash
uvicorn app.main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`

- **API docs:** http://localhost:8000/docs
- **Health check:** http://localhost:8000/health

---

## Architecture

```
app/
├── main.py              # App factory, middleware, exception handlers
├── core/
│   ├── config.py        # Settings (from env vars)
│   ├── security.py      # JWT verification
│   ├── exceptions.py    # Custom exception classes
│   └── logging.py       # Structured logging
├── db/
│   ├── base.py          # SQLAlchemy base + TimestampMixin
│   └── session.py       # Engine + get_db dependency
├── dependencies/
│   ├── auth.py          # get_current_user
│   ├── organization.py  # get_organization_membership
│   └── permissions.py   # has_feature_access, require_feature
├── modules/
│   ├── auth/            # /auth/me endpoint
│   └── organizations/   # Full CRUD for organizations + branches
└── shared/
    ├── models.py        # All SQLAlchemy models
    ├── schemas.py       # Shared Pydantic schemas
    └── utils.py         # Utility functions
```

## Authentication Flow

1. User logs in via **Supabase Auth** (email/password)
2. Supabase returns a **JWT access token**
3. Frontend sends `Authorization: Bearer <token>` with every API request
4. FastAPI verifies the token using `SUPABASE_JWT_SECRET`
5. FastAPI looks up or creates the user in our `users` table
6. If the email matches `SUPER_ADMIN_EMAIL`, the user gets `is_super_admin = true`

## Database Connection

FastAPI connects directly to Supabase PostgreSQL via the `DATABASE_URL` (connection string).
We do NOT use the Supabase REST API for data — we use SQLAlchemy with raw PostgreSQL.

This means:
- ✅ Full SQL control
- ✅ Proper transactions
- ✅ Alembic migrations
- ⚠️ RLS is not automatically applied — we enforce tenant isolation in WHERE clauses

---

## Running Tests

```bash
pytest tests/ -v
```

---

## Deployment (Railway)

1. Push to GitHub
2. Create a new Railway project, connect GitHub repo
3. Set all environment variables from `.env.example`
4. Railway will detect the `Dockerfile` and build automatically
5. Set the start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
6. Add a health check path: `/health`

---

## Migration Commands

```bash
# Create a new migration (auto-detect changes)
alembic revision --autogenerate -m "describe your change"

# Apply all pending migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# View migration history
alembic history
```
