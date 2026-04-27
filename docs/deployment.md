# Deployment

## Backend

Deploy the FastAPI backend to Render or Railway.

Build command:

```bash
pip install -r requirements.txt
```

Start command:

```bash
alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

Set all backend environment variables, including production `DATABASE_URL`, `JWT_SECRET_KEY`, `FRONTEND_ORIGINS`, Cloudinary, and Razorpay keys.

## Frontend

Deploy `frontend` to Vercel.

Set:

```env
NEXT_PUBLIC_API_URL=https://your-api-host
NEXT_PUBLIC_RAZORPAY_KEY_ID=rzp_live_or_test_key
NEXT_PUBLIC_SITE_URL=https://campusstay.in
```

## Database

Use Neon or Supabase PostgreSQL. Apply migrations:

```bash
cd backend
alembic upgrade head
```

Seed admin:

```bash
python -m app.seed_admin
```

## Smoke Tests

- `GET /health`
- `GET /ready`
- Register student
- Register owner
- Seed/login admin
- Create and approve PG
- Unlock contact
- Buy credits in Razorpay test mode
- Submit review/report

## Rollback

Keep previous deploy active until migrations and smoke tests pass. Database rollback should be planned per migration; avoid destructive rollbacks on production data.
