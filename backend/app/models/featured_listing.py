import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from app.models.enums import FeaturedListingSource, FeaturedListingStatus


class FeaturedListing(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "featured_listings"

    pg_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("pg_listings.id"), index=True)
    owner_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), index=True)
    status: Mapped[FeaturedListingStatus] = mapped_column(
        Enum(FeaturedListingStatus, name="featured_listing_status", values_callable=lambda enum: [item.value for item in enum]),
        default=FeaturedListingStatus.ACTIVE,
        index=True,
        nullable=False,
    )
    starts_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    ends_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    amount_rupees: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    source: Mapped[FeaturedListingSource] = mapped_column(
        Enum(FeaturedListingSource, name="featured_listing_source", values_callable=lambda enum: [item.value for item in enum]),
        default=FeaturedListingSource.ADMIN_GRANT,
        nullable=False,
    )

    pg: Mapped["PGListing"] = relationship(back_populates="featured_listings")
    owner: Mapped["User"] = relationship()
