import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, UUIDPrimaryKeyMixin


class ContactUnlock(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "contact_unlocks"
    __table_args__ = (UniqueConstraint("student_id", "pg_id", name="uq_contact_unlock_student_pg"),)

    student_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), index=True)
    pg_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("pg_listings.id"), index=True)
    credits_used: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    student: Mapped["User"] = relationship(back_populates="contact_unlocks")
    pg: Mapped["PGListing"] = relationship(back_populates="unlocks")
