# Jewellery ERP SaaS Platform

A production-oriented, multi-tenant Jewellery ERP SaaS platform built with:

- **Frontend:** Next.js 15, Tailwind CSS, Supabase Auth
- **Backend:** FastAPI, SQLAlchemy 2.x, Alembic
- **Database:** Supabase PostgreSQL
- **Deployment:** Railway (backend), Vercel (frontend), Supabase (database)

---

## Project Structure

```
Jewellery/
├── backend/              # FastAPI Python backend
│   ├── app/              # Application code
│   ├── migrations/       # Alembic database migrations
│   ├── tests/            # Pytest tests
│   ├── Dockerfile
│   ├── requirements.txt
│   └── README.md
├── frontend/             # Next.js frontend
│   ├── app/              # Next.js App Router pages
│   ├── components/       # Reusable React components
│   ├── lib/              # API client, auth, utilities
│   ├── hooks/            # Custom React hooks
│   └── README.md
├── docker-compose.yml    # Local development orchestration
└── README.md             # This file
```

---

## Quick Start (Local Development)

### Prerequisites

- Python 3.12+
- Node.js 20+
- A Supabase project

### 1. Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate          # Windows
pip install -r requirements.txt
cp .env.example .env
# Fill in your Supabase credentials in .env
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

### 2. Frontend

```bash
cd frontend
npm install
cp .env.local.example .env.local
# Fill in your Supabase credentials in .env.local
npm run dev
```

Visit:
- Frontend: http://localhost:3000
- Backend API docs: http://localhost:8000/docs
- Health check: http://localhost:8000/health

---

## Development Phases

| Phase | Status | Description |
|---|---|---|
| **Phase 1** | 🟡 In Progress | Foundation, Auth, Organizations |
| **Phase 2** | ⬜ Planned | Users, Roles, Permissions |
| **Phase 3** | ⬜ Planned | Subscription & Feature Access |
| **Phase 4** | ⬜ Planned | Inventory Management |
| **Phase 5** | ⬜ Planned | Gold Pricing & Purchases |
| **Phase 6** | ⬜ Planned | Customers & POS |
| **Phase 7** | ⬜ Planned | Manufacturing & Repairs |
| **Phase 8** | ⬜ Planned | Reports & Deployment Hardening |

---

## Security Notes

- ⚠️ Never commit `.env` or `.env.local` files
- ⚠️ Never expose `SUPABASE_SERVICE_ROLE_KEY` to the frontend
- ⚠️ The `SUPER_ADMIN_EMAIL` is auto-elevated on first login — protect it

---

## Environment Variables Required

See `backend/.env.example` and `frontend/.env.local.example` for all required variables.

---

## License

Proprietary — All rights reserved.
