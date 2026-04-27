import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, UUIDPrimaryKeyMixin
from app.models.enums import ImageType


class PGPhoto(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "pg_photos"

    pg_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("pg_listings.id"), index=True)
    image_url: Mapped[str] = mapped_column(String(1000), nullable=False)
    public_id: Mapped[str | None] = mapped_column(String(500), nullable=True)
    image_type: Mapped[ImageType] = mapped_column(
        Enum(ImageType, name="image_type", values_callable=lambda enum: [item.value for item in enum]),
        nullable=False,
    )
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    pg: Mapped["PGListing"] = relationship(back_populates="photos")
