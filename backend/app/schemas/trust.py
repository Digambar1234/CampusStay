from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field

from app.models.enums import FeaturedListingSource, FeaturedListingStatus, ListingStatus, ReportPriority, ReportStatus, ReportType, ReviewStatus


class ReviewCreate(BaseModel):
    rating: int = Field(ge=1, le=5)
    title: str | None = Field(default=None, max_length=180)
    comment: str = Field(min_length=5)


class ReviewUpdate(BaseModel):
    rating: int | None = Field(default=None, ge=1, le=5)
    title: str | None = Field(default=None, max_length=180)
    comment: str | None = Field(default=None, min_length=5)


class PublicReviewResponse(BaseModel):
    id: UUID
    pg_id: UUID
    rating: int
    title: str | None
    comment: str
    status: ReviewStatus
    is_edited: bool
    reviewer_name: str
    created_at: datetime
    updated_at: datetime


class StudentReviewResponse(PublicReviewResponse):
    pg_name: str


class AdminReviewResponse(StudentReviewResponse):
    student_name: str
    student_email: str


class ReviewListResponse(BaseModel):
    items: list[PublicReviewResponse]
    total: int
    average_rating: float | None


class ReportCreate(BaseModel):
    report_type: ReportType
    reason: str = Field(min_length=3, max_length=180)
    description: str | None = None
    reporter_email: EmailStr | None = None
    reporter_phone: str | None = Field(default=None, max_length=30)


class ReportUpdate(BaseModel):
    status: ReportStatus | None = None
    priority: ReportPriority | None = None
    admin_note: str | None = None


class ReportResponse(BaseModel):
    id: UUID
    pg_id: UUID
    pg_name: str
    student_id: UUID | None
    reporter_email: str | None
    reporter_phone: str | None
    report_type: ReportType
    priority: ReportPriority
    reason: str
    description: str | None
    status: ReportStatus
    admin_note: str | None
    resolved_by: UUID | None
    resolved_at: datetime | None
    created_at: datetime
    updated_at: datetime


class FeaturedListingCreate(BaseModel):
    pg_id: UUID
    days: int = Field(ge=1, le=365)
    amount_rupees: int = Field(default=0, ge=0)
    source: FeaturedListingSource = FeaturedListingSource.ADMIN_GRANT


class FeaturedListingResponse(BaseModel):
    id: UUID
    pg_id: UUID
    pg_name: str
    owner_id: UUID
    status: FeaturedListingStatus
    starts_at: datetime
    ends_at: datetime
    amount_rupees: int
    source: FeaturedListingSource
    created_at: datetime
    updated_at: datetime


class OwnerAnalyticsSummary(BaseModel):
    total_listings: int
    approved_listings: int
    pending_listings: int
    rejected_listings: int
    total_views: int
    total_contact_unlocks: int
    total_reviews: int
    average_rating_across_listings: float | None
    active_featured_listings: int


class OwnerListingAnalytics(BaseModel):
    pg_id: UUID
    pg_name: str
    status: ListingStatus
    views_count: int
    contact_unlock_count: int
    review_count: int
    average_rating: float | None
    is_featured: bool
    created_at: datetime


class AdminAnalyticsSummary(BaseModel):
    total_users: int
    total_students: int
    total_pg_owners: int
    total_pg_listings: int
    approved_pg_listings: int
    pending_pg_listings: int
    rejected_pg_listings: int
    suspended_pg_listings: int
    total_contact_unlocks: int
    total_credit_revenue_rupees: int
    total_credits_purchased: int
    total_reviews: int
    total_reports: int
    open_reports: int
    active_featured_listings: int


class AdminRevenueResponse(BaseModel):
    total_revenue_rupees: int
    credits_sold: int
    payments: list[dict]


class TopPGResponse(BaseModel):
    pg_id: UUID
    pg_name: str
    views: int
    unlocks: int
    average_rating: float | None
    review_count: int
