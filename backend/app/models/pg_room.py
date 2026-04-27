import uuid

from sqlalchemy import Boolean, Enum, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from app.models.enums import RoomType


class PGRoom(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "pg_rooms"

    pg_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("pg_listings.id"), index=True)
    room_type: Mapped[RoomType] = mapped_column(
        Enum(RoomType, name="room_type", values_callable=lambda enum: [item.value for item in enum]),
        nullable=False,
    )
    price_per_month: Mapped[int] = mapped_column(Integer, nullable=False)
    available_beds: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    ac_available: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    attached_washroom: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    pg: Mapped["PGListing"] = relationship(back_populates="rooms")
