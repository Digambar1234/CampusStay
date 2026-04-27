# Database Schema

## users

Stores account identity, auth hash, role, and account status. Related one-to-one with student or PG owner profiles.

## student_profiles

Role extension for student users. Defaults university to Lovely Professional University.

## pg_owner_profiles

Role extension for PG owner users. Tracks business details and owner verification status.

## pg_listings

Core PG inventory table. Belongs to a PG owner user. Stores address, location, facilities, rent range, owner contact, and verification workflow status.

Public visibility rule: `status = approved` and `admin_verified = true`.

## pg_rooms

Room-level price and availability rows for a PG listing.

## pg_photos

Image metadata for listing photos. Stores Cloudinary `image_url`, nullable `public_id`, image type, and primary-photo flag.

## credit_wallets

One wallet per student user. Starts with 10 credits after student signup.

Part 3 uses this table as the source of truth for contact unlock eligibility and purchased credit balance.

## credit_transactions

Append-only credit ledger for signup bonuses, purchases, unlocks, refunds, and admin adjustments.

Positive amounts add credits. Contact unlocks use `amount = -1` so wallet usage is auditable.

## contact_unlocks

Tracks each student-to-PG contact unlock. Unique constraint on `student_id + pg_id` prevents duplicate charging for the same PG contact.

Only rows in this table allow a student to see previously unlocked owner phone and WhatsApp values again.

## payments

Prepared for Razorpay credit purchase flow. Stores provider order/payment IDs, rupee amount, credit quantity, and payment status.

Part 3 verifies Razorpay signatures before setting `status=paid` and adding purchased credits to the student's wallet.

## reports

Student or public reports against PG listings. Supports moderation states.

## admin_action_logs

Audit log for admin actions against users, listings, payments, or other targets.

In Part 2, PG approve/reject/suspend/request-changes actions write records with `target_type=pg_listing` and action metadata.

## reviews

Stores student reviews for PGs. A unique constraint on `student_id + pg_id` prevents duplicate reviews. Ratings are 1 to 5. Reviews default to `approved`, and admins can hide or reject inappropriate reviews.

## featured_listings

Stores admin-granted or future paid promotion windows for PGs. Active featured rows boost PG visibility in public browse results.

## listing_views

Stores listing detail views for analytics. Viewer user ID is nullable, and IP/user-agent are stored only as hashes when available.

## updated reports

Reports now include reporter email/phone, report type, priority, admin note, resolver, and resolved timestamp for moderation workflows.
