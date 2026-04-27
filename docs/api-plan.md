# API Plan

## Implemented in Part 1

- `GET /health`
- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`
- `GET /api/v1/auth/me`
- `GET /api/v1/student/dashboard`
- `GET /api/v1/owner/dashboard`
- `GET /api/v1/admin/dashboard`
- `GET /api/v1/pgs`

## Implemented in Part 2

Owner listing APIs:

- `POST /api/v1/owner/listings`
- `GET /api/v1/owner/listings`
- `GET /api/v1/owner/listings/{pg_id}`
- `PATCH /api/v1/owner/listings/{pg_id}`
- `POST /api/v1/owner/listings/{pg_id}/submit`
- `DELETE /api/v1/owner/listings/{pg_id}`
- `POST /api/v1/owner/listings/{pg_id}/rooms`
- `PATCH /api/v1/owner/listings/{pg_id}/rooms/{room_id}`
- `DELETE /api/v1/owner/listings/{pg_id}/rooms/{room_id}`
- `POST /api/v1/owner/listings/{pg_id}/photos`
- `DELETE /api/v1/owner/listings/{pg_id}/photos/{photo_id}`
- `PATCH /api/v1/owner/listings/{pg_id}/photos/{photo_id}/primary`

Admin PG verification APIs:

- `GET /api/v1/admin/pgs/pending`
- `GET /api/v1/admin/pgs/approved`
- `GET /api/v1/admin/pgs/rejected`
- `GET /api/v1/admin/pgs/{pg_id}`
- `POST /api/v1/admin/pgs/{pg_id}/approve`
- `POST /api/v1/admin/pgs/{pg_id}/reject`
- `POST /api/v1/admin/pgs/{pg_id}/suspend`
- `POST /api/v1/admin/pgs/{pg_id}/request-changes`

Public PG APIs:

- `GET /api/v1/pgs` with filters and sorting
- `GET /api/v1/pgs/{pg_id}`

## Reserved Namespaces

- `/api/v1/users`
- `/api/v1/student`
- `/api/v1/owner`
- `/api/v1/admin`
- `/api/v1/pgs`
- `/api/v1/credits`

## Implemented in Part 3

- `GET /api/v1/credits/wallet`
- `GET /api/v1/credits/transactions`
- `GET /api/v1/credits/unlock-status/{pg_id}`
- `POST /api/v1/credits/unlock-contact/{pg_id}`
- `GET /api/v1/credits/unlocked-contacts`
- `POST /api/v1/credits/create-order`
- `POST /api/v1/credits/verify-payment`

## Implemented in Part 4

- `GET /api/v1/reviews/pg/{pg_id}`
- `POST /api/v1/reviews/pg/{pg_id}`
- `PATCH /api/v1/reviews/{review_id}`
- `DELETE /api/v1/reviews/{review_id}`
- `GET /api/v1/student/reviews`
- `GET /api/v1/admin/reviews`
- `POST /api/v1/admin/reviews/{review_id}/approve`
- `POST /api/v1/admin/reviews/{review_id}/hide`
- `POST /api/v1/admin/reviews/{review_id}/reject`
- `POST /api/v1/reports/pg/{pg_id}`
- `GET /api/v1/student/reports`
- `GET /api/v1/admin/reports`
- `GET /api/v1/admin/reports/{report_id}`
- `PATCH /api/v1/admin/reports/{report_id}`
- `POST /api/v1/admin/reports/{report_id}/resolve`
- `POST /api/v1/admin/featured-listings`
- `GET /api/v1/admin/featured-listings`
- `POST /api/v1/admin/featured-listings/{id}/cancel`
- `GET /api/v1/owner/analytics/summary`
- `GET /api/v1/owner/analytics/listings`
- `GET /api/v1/admin/analytics/summary`
- `GET /api/v1/admin/analytics/revenue`
- `GET /api/v1/admin/analytics/top-pgs`

## Implemented in Part 5

- `GET /ready`
- `GET /api/v1/admin/audit-logs`
- Rate-limited sensitive POST endpoints
- Standardized error response envelope
- Security headers and request ID middleware

## Future APIs for Part 6

- Notification system.
- Owner paid promotions with Razorpay.
- Email verification and OTP login.
- Password reset.
- AI PG recommendation.
- AI chatbot.
- Mobile app.
- Tiffin, laundry, and other student marketplace extensions.
