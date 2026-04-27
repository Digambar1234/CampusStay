from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import and_, func, select
from sqlalchemy.orm import Session

from app.models import ContactUnlock, FeaturedListing, ListingView, Payment, PGListing, Report, Review, User
from app.models.enums import FeaturedListingStatus, ListingStatus, PaymentStatus, ReportStatus, ReviewStatus, Role


def active_featured_condition():
    now = datetime.now(UTC)
    return and_(FeaturedListing.status == FeaturedListingStatus.ACTIVE, FeaturedListing.starts_at <= now, FeaturedListing.ends_at >= now)


def is_pg_featured(db: Session, pg_id: UUID) -> bool:
    return db.scalar(select(func.count(FeaturedListing.id)).where(FeaturedListing.pg_id == pg_id, active_featured_condition())) > 0


def review_stats(db: Session, pg_id: UUID) -> tuple[float | None, int]:
    avg_rating, count = db.execute(
        select(func.avg(Review.rating), func.count(Review.id)).where(Review.pg_id == pg_id, Review.status == ReviewStatus.APPROVED)
    ).one()
    return (round(float(avg_rating), 2) if avg_rating is not None else None, count)


def owner_listing_metrics(db: Session, owner_id: UUID) -> list[dict]:
    listings = db.scalars(select(PGListing).where(PGListing.owner_id == owner_id).order_by(PGListing.created_at.desc())).all()
    rows: list[dict] = []
    for listing in listings:
        avg_rating, review_count = review_stats(db, listing.id)
        rows.append(
            {
                "pg_id": listing.id,
                "pg_name": listing.pg_name,
                "status": listing.status,
                "views_count": db.scalar(select(func.count(ListingView.id)).where(ListingView.pg_id == listing.id)) or 0,
                "contact_unlock_count": db.scalar(select(func.count(ContactUnlock.id)).where(ContactUnlock.pg_id == listing.id)) or 0,
                "review_count": review_count,
                "average_rating": avg_rating,
                "is_featured": is_pg_featured(db, listing.id),
                "created_at": listing.created_at,
            }
        )
    return rows


def admin_summary(db: Session) -> dict:
    return {
        "total_users": db.scalar(select(func.count(User.id))) or 0,
        "total_students": db.scalar(select(func.count(User.id)).where(User.role == Role.STUDENT)) or 0,
        "total_pg_owners": db.scalar(select(func.count(User.id)).where(User.role == Role.PG_OWNER)) or 0,
        "total_pg_listings": db.scalar(select(func.count(PGListing.id))) or 0,
        "approved_pg_listings": db.scalar(select(func.count(PGListing.id)).where(PGListing.status == ListingStatus.APPROVED)) or 0,
        "pending_pg_listings": db.scalar(select(func.count(PGListing.id)).where(PGListing.status == ListingStatus.PENDING_REVIEW)) or 0,
        "rejected_pg_listings": db.scalar(select(func.count(PGListing.id)).where(PGListing.status == ListingStatus.REJECTED)) or 0,
        "suspended_pg_listings": db.scalar(select(func.count(PGListing.id)).where(PGListing.status == ListingStatus.SUSPENDED)) or 0,
        "total_contact_unlocks": db.scalar(select(func.count(ContactUnlock.id))) or 0,
        "total_credit_revenue_rupees": db.scalar(select(func.coalesce(func.sum(Payment.amount_rupees), 0)).where(Payment.status == PaymentStatus.PAID)) or 0,
        "total_credits_purchased": db.scalar(select(func.coalesce(func.sum(Payment.credits_purchased), 0)).where(Payment.status == PaymentStatus.PAID)) or 0,
        "total_reviews": db.scalar(select(func.count(Review.id))) or 0,
        "total_reports": db.scalar(select(func.count(Report.id))) or 0,
        "open_reports": db.scalar(select(func.count(Report.id)).where(Report.status == ReportStatus.OPEN)) or 0,
        "active_featured_listings": db.scalar(select(func.count(FeaturedListing.id)).where(active_featured_condition())) or 0,
    }
