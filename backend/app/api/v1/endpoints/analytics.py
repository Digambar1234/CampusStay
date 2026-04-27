from sqlalchemy import func, select
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends

from app.db.session import get_db
from app.dependencies.auth import require_roles
from app.models import ContactUnlock, FeaturedListing, ListingView, Payment, PGListing, Review, User
from app.models.enums import ListingStatus, PaymentStatus, ReviewStatus, Role
from app.schemas.trust import AdminAnalyticsSummary, AdminRevenueResponse, OwnerAnalyticsSummary, OwnerListingAnalytics, TopPGResponse
from app.services.analytics_service import active_featured_condition, admin_summary, owner_listing_metrics

owner_router = APIRouter(prefix="/owner/analytics", tags=["owner-analytics"])
admin_router = APIRouter(prefix="/admin/analytics", tags=["admin-analytics"])


@owner_router.get("/summary", response_model=OwnerAnalyticsSummary)
def owner_summary(user: User = Depends(require_roles(Role.PG_OWNER)), db: Session = Depends(get_db)) -> OwnerAnalyticsSummary:
    rows = owner_listing_metrics(db, user.id)
    statuses = [row["status"] for row in rows]
    ratings = [row["average_rating"] for row in rows if row["average_rating"] is not None]
    return OwnerAnalyticsSummary(
        total_listings=len(rows),
        approved_listings=statuses.count(ListingStatus.APPROVED),
        pending_listings=statuses.count(ListingStatus.PENDING_REVIEW),
        rejected_listings=statuses.count(ListingStatus.REJECTED),
        total_views=sum(row["views_count"] for row in rows),
        total_contact_unlocks=sum(row["contact_unlock_count"] for row in rows),
        total_reviews=sum(row["review_count"] for row in rows),
        average_rating_across_listings=round(sum(ratings) / len(ratings), 2) if ratings else None,
        active_featured_listings=sum(1 for row in rows if row["is_featured"]),
    )


@owner_router.get("/listings", response_model=list[OwnerListingAnalytics])
def owner_listing_analytics(user: User = Depends(require_roles(Role.PG_OWNER)), db: Session = Depends(get_db)) -> list[OwnerListingAnalytics]:
    return [OwnerListingAnalytics(**row) for row in owner_listing_metrics(db, user.id)]


@admin_router.get("/summary", response_model=AdminAnalyticsSummary)
def get_admin_summary(_: User = Depends(require_roles(Role.ADMIN, Role.SUPER_ADMIN)), db: Session = Depends(get_db)) -> AdminAnalyticsSummary:
    return AdminAnalyticsSummary(**admin_summary(db))


@admin_router.get("/revenue", response_model=AdminRevenueResponse)
def revenue(_: User = Depends(require_roles(Role.ADMIN, Role.SUPER_ADMIN)), db: Session = Depends(get_db)) -> AdminRevenueResponse:
    payments = db.scalars(select(Payment).where(Payment.status == PaymentStatus.PAID).order_by(Payment.created_at.desc()).limit(50)).all()
    return AdminRevenueResponse(
        total_revenue_rupees=sum(p.amount_rupees for p in payments),
        credits_sold=sum(p.credits_purchased for p in payments),
        payments=[{"id": str(p.id), "student_id": str(p.student_id), "amount_rupees": p.amount_rupees, "credits_purchased": p.credits_purchased, "created_at": p.created_at.isoformat()} for p in payments],
    )


@admin_router.get("/top-pgs", response_model=list[TopPGResponse])
def top_pgs(_: User = Depends(require_roles(Role.ADMIN, Role.SUPER_ADMIN)), db: Session = Depends(get_db)) -> list[TopPGResponse]:
    listings = db.scalars(select(PGListing).limit(100)).all()
    rows = []
    for listing in listings:
        views = db.scalar(select(func.count(ListingView.id)).where(ListingView.pg_id == listing.id)) or 0
        unlocks = db.scalar(select(func.count(ContactUnlock.id)).where(ContactUnlock.pg_id == listing.id)) or 0
        avg = db.scalar(select(func.avg(Review.rating)).where(Review.pg_id == listing.id, Review.status == ReviewStatus.APPROVED))
        count = db.scalar(select(func.count(Review.id)).where(Review.pg_id == listing.id, Review.status == ReviewStatus.APPROVED)) or 0
        rows.append(TopPGResponse(pg_id=listing.id, pg_name=listing.pg_name, views=views, unlocks=unlocks, average_rating=round(float(avg), 2) if avg else None, review_count=count))
    return sorted(rows, key=lambda row: (row.views, row.unlocks, row.average_rating or 0), reverse=True)[:20]
