# CampusStay Architecture

CampusStay is split into a deployable monorepo with a Next.js frontend and a FastAPI backend. The backend owns authentication, roles, credits, unlock history, listing verification state, and all PostgreSQL persistence. The frontend consumes REST APIs and protects dashboards based on the authenticated user's role.

## Frontend

- Next.js App Router with TypeScript.
- Tailwind CSS v4 and local shadcn-style components.
- `lib/api-client.ts` centralizes backend calls and attaches JWT bearer tokens.
- `components/auth/auth-provider.tsx` loads `/api/v1/auth/me`, stores development JWTs in localStorage, and exposes auth state.
- `components/auth/protected-route.tsx` protects student, owner, and admin pages by role.
- Public pages are SEO-friendly server/app-router pages where possible.

Production TODO: move JWT storage from localStorage to httpOnly secure cookies with CSRF-aware session handling.

## Backend

- FastAPI app under `backend/app`.
- SQLAlchemy ORM models under `app/models`.
- Pydantic schemas under `app/schemas`.
- API routers grouped under `/api/v1`.
- Auth logic is separated into `services/auth_service.py`.
- Dependencies handle current-user lookup and role guards.
- Alembic controls schema migrations.

## Database

PostgreSQL is the primary database and should be supplied through `DATABASE_URL`. The schema supports Neon and Supabase PostgreSQL connection strings.

Core relationship shape:

- `users` is the role-bearing identity table.
- `student_profiles` and `pg_owner_profiles` extend users by role.
- `pg_listings` belong to PG owner users.
- `pg_rooms` and `pg_photos` belong to listings.
- `credit_wallets`, `credit_transactions`, `contact_unlocks`, and `payments` support wallet and payment flows.
- `reports` and `admin_action_logs` support trust and moderation.

## Role System

Roles are:

- `student`
- `pg_owner`
- `admin`
- `super_admin`

Public registration accepts only `student` and `pg_owner`. Admin users must be seeded or created manually.

## Credit System

Students receive a `credit_wallet` with 10 credits on signup. A `credit_transaction` records the signup bonus. `contact_unlocks` has a unique constraint on `student_id + pg_id`, which prevents charging a student twice for the same PG contact in the later unlock API.

## Admin Verification

PG listings are not public by default. Owner submissions should move to `pending_review`; admins approve them by setting `status=approved` and `admin_verified=true`. Public browse APIs return only approved and admin-verified listings.

## Owner Listing Workflow

PG owners create listings through protected `/api/v1/owner/listings` APIs. A listing begins as `draft`, then the owner adds rooms and Cloudinary-hosted photos. Submission validates required details, at least one room, and at least one photo before setting `status=pending_review`.

Owners can edit `draft`, `pending_review`, and `rejected` listings. Approved listings are read-only in Part 2; a formal change-request workflow is reserved for later.

## Admin Verification Workflow

Admins and super admins review PGs under `/api/v1/admin/pgs`. They can approve, reject, suspend, or request changes. Each action writes an `admin_action_logs` record with action metadata so moderation is auditable.

## Cloudinary Media Flow

Owner photo uploads are accepted as multipart form data, validated for image type and size, uploaded into `campusstay/pgs/{pg_id}`, and stored in PostgreSQL as Cloudinary `secure_url` plus `public_id`. Raw files are not persisted locally.

## Public Visibility Rules

Public listing APIs return only listings where `status=approved` and `admin_verified=true`. Public responses intentionally exclude `owner_phone` and `whatsapp_number`; contact unlock belongs to Part 3.

## Credit Wallet Flow

Student signup creates a `credit_wallet` with 10 free credits and a `free_signup_bonus` transaction. Students can inspect balance and transaction history through protected `/api/v1/credits` APIs. Credit additions are positive transactions; contact unlock debits are stored as negative transactions.

## Contact Unlock Privacy Model

Public PG APIs never return owner phone or WhatsApp fields. Contact numbers are returned only by student-only credit APIs:

- `POST /api/v1/credits/unlock-contact/{pg_id}`
- `GET /api/v1/credits/unlocked-contacts`

Unlocking is limited to approved and admin-verified PGs. The unique `student_id + pg_id` constraint prevents duplicate unlock records, and the unlock endpoint is transactional so repeat requests do not deduct credits again.

## Razorpay Payment Verification Flow

The frontend asks the backend to create a Razorpay order. Razorpay Checkout returns order/payment/signature values to the browser, but credits are added only after `/api/v1/credits/verify-payment` verifies the signature server-side using `RAZORPAY_KEY_SECRET`. Repeated verification calls for an already paid payment return without adding credits again.

## Review System

Students can review only PGs whose contact they have unlocked. Reviews are unique by `student_id + pg_id`, visible publicly when approved, and default to approved for MVP marketplace liquidity. Admins can approve, hide, or reject reviews with audit logs.

## Report Moderation

Reports can be submitted by logged-in students or public users. Student reports attach `student_id`; public reports require reporter email. Admins can filter, update priority/status, add notes, and resolve reports.

## Featured Listings

Admins can grant featured placement to approved PGs for a selected number of days. Active featured listings are boosted in public PG results and marked on cards/detail responses. Owner paid promotion is reserved for Part 5.

## Analytics Architecture

Analytics are aggregated from operational tables: users, listings, payments, credit transactions, contact unlocks, listing views, reviews, reports, and featured listings. Owners receive aggregate listing metrics only, not student identities.
