import uuid

from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class StudentProfile(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "student_profiles"

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), unique=True)
    university_name: Mapped[str] = mapped_column(String(160), default="Lovely Professional University")
    course: Mapped[str | None] = mapped_column(String(120), nullable=True)
    year: Mapped[str | None] = mapped_column(String(30), nullable=True)

    user: Mapped["User"] = relationship(back_populates="student_profile")


class PGOwnerProfile(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "pg_owner_profiles"

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), unique=True)
    business_name: Mapped[str | None] = mapped_column(String(160), nullable=True)
    alternate_phone: Mapped[str | None] = mapped_column(String(30), nullable=True)
    is_owner_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    user: Mapped["User"] = relationship(back_populates="owner_profile")
