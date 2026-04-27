# Security

## Authentication

CampusStay uses JWT access tokens with `sub`, `role`, and `exp` claims. Public registration is restricted to `student` and `pg_owner`; admin accounts are seeded or created manually.

Current frontend storage uses localStorage for development continuity. Recommended production improvement: migrate to httpOnly secure cookie auth with CSRF protection.

## Role-Based Access

Backend dependencies enforce role access for student, PG owner, admin, and super admin routes. PG owners can access only their own listings. Student-only unlock APIs cannot be used by owners or admins.

## Contact Privacy

Public PG APIs do not return owner phone or WhatsApp. Contact details are returned only by protected student credit unlock APIs after the student unlocks an approved PG.

## Rate Limiting

Sensitive endpoints are rate limited with SlowAPI:

- Login: 5/minute
- Register: 3/minute
- Contact unlock: 10/minute
- Payment order: 5/minute
- Payment verify: 10/minute
- Reviews/reports: 5/minute
- Photo upload: 10/minute

Current limiter is process-local. For multi-instance production, use Redis-backed shared rate limiting.

## Payment Verification

Razorpay payment success is never trusted from the frontend alone. Backend verifies `razorpay_signature` with `RAZORPAY_KEY_SECRET` before adding credits.

## Upload Restrictions

PG photo uploads allow only jpg, jpeg, png, and webp, reject SVG, and enforce a 5MB limit before uploading to Cloudinary.

## Security Headers

The API sets content type, frame, referrer, permissions, and conservative CSP headers. HSTS is enabled only in production.

## Audit Logs

Admin listing moderation, review moderation, report resolution, and featured listing actions write `AdminActionLog` records.

## Future Improvements

- httpOnly cookie auth
- Email OTP verification
- Password reset flow
- Redis rate limit storage
- Sentry or OpenTelemetry monitoring
- Automated database backups
- WAF/CDN protection
