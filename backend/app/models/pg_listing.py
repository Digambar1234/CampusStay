import uuid
from decimal import Decimal

from sqlalchemy import Boolean, Enum, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from app.models.enums import GenderAllowed, ListingStatus


class PGListing(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "pg_listings"

    owner_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), index=True)
    pg_name: Mapped[str] = mapped_column(String(180), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    address: Mapped[str] = mapped_column(String(500), nullable=False)
    landmark: Mapped[str | None] = mapped_column(String(180), nullable=True)
    distance_from_lpu_km: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), nullable=True)
    latitude: Mapped[Decimal | None] = mapped_column(Numeric(10, 7), nullable=True)
    longitude: Mapped[Decimal | None] = mapped_column(Numeric(10, 7), nullable=True)
    gender_allowed: Mapped[GenderAllowed] = mapped_column(
        Enum(GenderAllowed, name="gender_allowed", values_callable=lambda enum: [item.value for item in enum]),
        nullable=False,
    )
    food_available: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    wifi_available: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    ac_available: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    laundry_available: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    parking_available: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    security_available: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    monthly_rent_min: Mapped[int | None] = mapped_column(Integer, nullable=True)
    monthly_rent_max: Mapped[int | None] = mapped_column(Integer, nullable=True)
    deposit_amount: Mapped[int | None] = mapped_column(Integer, nullable=True)
    owner_phone: Mapped[str] = mapped_column(String(30), nullable=False)
    whatsapp_number: Mapped[str | None] = mapped_column(String(30), nullable=True)
    status: Mapped[ListingStatus] = mapped_column(
        Enum(ListingStatus, name="listing_status", values_callable=lambda enum: [item.value for item in enum]),
        default=ListingStatus.DRAFT,
        index=True,
    )
    admin_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    owner: Mapped["User"] = relationship(back_populates="owned_listings")
    rooms: Mapped[list["PGRoom"]] = relationship(back_populates="pg", cascade="all, delete-orphan")
    photos: Mapped[list["PGPhoto"]] = relationship(back_populates="pg", cascade="all, delete-orphan")
    unlocks: Mapped[list["ContactUnlock"]] = relationship(back_populates="pg")
    reports: Mapped[list["Report"]] = relationship(back_populates="pg")
    reviews: Mapped[list["Review"]] = relationship(back_populates="pg")
    featured_listings: Mapped[list["FeaturedListing"]] = relationship(back_populates="pg")
    views: Mapped[list["ListingView"]] = relationship(back_populates="pg")
