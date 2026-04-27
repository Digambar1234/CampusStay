# Setup Guide

## Backend

From `campusstay/backend`:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

Set `DATABASE_URL` to a PostgreSQL database, such as Neon or Supabase.

Set Cloudinary credentials for PG photo upload:

```env
CLOUDINARY_CLOUD_NAME=your-cloud-name
CLOUDINARY_API_KEY=your-api-key
CLOUDINARY_API_SECRET=your-api-secret
```

Set Razorpay test credentials for credit purchase:

```env
RAZORPAY_KEY_ID=rzp_test_your_key_id
RAZORPAY_KEY_SECRET=your_razorpay_secret
CREDIT_PACK_PRICE_RUPEES=10
CREDIT_PACK_AMOUNT=10
```

Run migrations:

```bash
alembic upgrade head
```

Part 4 adds the `202604270003_part4_trust_analytics` migration for reviews, reports, featured listings, and listing views.

Seed an admin:

```bash
python -m app.seed_admin
```

Run the API:

```bash
uvicorn app.main:app --reload
```

API docs will be available at `http://localhost:8000/docs`.

## Frontend

From `campusstay/frontend`:

```bash
npm install
copy .env.example .env.local
npm run dev
```

Set `NEXT_PUBLIC_API_URL=http://localhost:8000`.

The app runs at `http://localhost:3000`.

## Required Environment Variables

Backend:

- `DATABASE_URL`
- `JWT_SECRET_KEY`
- `JWT_ALGORITHM`
- `ACCESS_TOKEN_EXPIRE_MINUTES`
- `FRONTEND_ORIGIN`
- `ENVIRONMENT`
- `ADMIN_EMAIL`
- `ADMIN_PASSWORD`
- `ADMIN_FULL_NAME`
- `CLOUDINARY_CLOUD_NAME`
- `CLOUDINARY_API_KEY`
- `CLOUDINARY_API_SECRET`
- `RAZORPAY_KEY_ID`
- `RAZORPAY_KEY_SECRET`
- `CREDIT_PACK_PRICE_RUPEES`
- `CREDIT_PACK_AMOUNT`

Frontend:

- `NEXT_PUBLIC_API_URL`
- `NEXT_PUBLIC_RAZORPAY_KEY_ID`

## Razorpay Testing

Use Razorpay test mode keys. The browser opens Razorpay Checkout, but CampusStay adds credits only after the backend verifies `razorpay_signature`. If verification fails, the payment is marked failed and credits are not added.

## Production Setup

- Use Neon or Supabase PostgreSQL.
- Set `FRONTEND_ORIGINS` to exact frontend domains.
- Deploy backend using `render.yaml`, Dockerfile, or Railway equivalent.
- Deploy frontend to Vercel from `frontend`.
- Run `alembic upgrade head` before opening traffic.
- Verify `/ready` returns `ready` or an expected `degraded` state.

## Deployment Notes

- Deploy frontend to Vercel with `NEXT_PUBLIC_API_URL` set to the backend URL.
- Deploy backend to Render or Railway with PostgreSQL credentials configured.
- Run `alembic upgrade head` during backend release or as a release command.
- Use strong generated secrets in production.
