# CampusStay

CampusStay is a production-oriented verified PG discovery platform for students near LPU. Students browse verified PGs, compare prices/facilities/reviews, unlock owner contacts with credits, and report bad listings. PG owners submit listings for admin verification. Admins moderate listings, reviews, reports, featured placements, revenue, and analytics.

## Current Status

- Part 1: auth, roles, PostgreSQL schema, wallets, dashboards.
- Part 2: owner listing CRUD, rooms, Cloudinary photos, admin verification, public PG pages.
- Part 3: credit wallet, contact unlock, Razorpay order and signature verification.
- Part 4: reviews, reports, featured listings, listing views, owner/admin analytics.
- Part 5: rate limiting, security headers, request logging, readiness checks, audit logs, SEO/legal pages, deployment docs.

## Tech Stack

- Frontend: Next.js 16, TypeScript, Tailwind CSS, shadcn-style components.
- Backend: FastAPI, SQLAlchemy, Alembic, Pydantic, JWT, bcrypt.
- Database: PostgreSQL via Neon, Supabase, or local Postgres.
- Storage: Cloudinary.
- Payments: Razorpay.
- Deployment: Vercel frontend, Render/Railway backend.

## Local Setup

Backend:

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
alembic upgrade head
python -m app.seed_admin
uvicorn app.main:app --reload
```

Frontend:

```bash
cd frontend
npm install
copy .env.example .env.local
npm run dev
```

## Production Setup

- Deploy backend with `render.yaml` or `backend/Dockerfile`.
- Backend start command: `alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Deploy frontend to Vercel from `frontend`.
- Set exact `FRONTEND_ORIGINS`; do not use wildcards in production.
- Run `/ready` after deployment.

## Test Flows

- Student signup receives 10 credits.
- Owner creates PG, adds rooms/photos, submits for review.
- Admin approves listing.
- Student unlocks owner contact.
- Student buys credits through Razorpay test checkout.
- Student reviews unlocked PG.
- Public/student reports listing.
- Admin moderates reviews/reports and grants featured placement.

## Known Limitations

- Frontend JWT storage is localStorage; production should migrate to httpOnly cookies.
- Rate limiting is process-local; multi-instance production should use Redis-backed limits.
- Notifications, password reset, and email verification are reserved for Part 6.
