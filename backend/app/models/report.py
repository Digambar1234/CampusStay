import uuid

from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from app.models.enums import ReportPriority, ReportStatus, ReportType


class Report(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "reports"

    student_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    pg_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("pg_listings.id"), index=True)
    reporter_email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    reporter_phone: Mapped[str | None] = mapped_column(String(30), nullable=True)
    report_type: Mapped[ReportType] = mapped_column(
        Enum(ReportType, name="report_type", values_callable=lambda enum: [item.value for item in enum]),
        default=ReportType.OTHER,
        nullable=False,
    )
    priority: Mapped[ReportPriority] = mapped_column(
        Enum(ReportPriority, name="report_priority", values_callable=lambda enum: [item.value for item in enum]),
        default=ReportPriority.MEDIUM,
        nullable=False,
    )
    reason: Mapped[str] = mapped_column(String(180), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    admin_note: Mapped[str | None] = mapped_column(Text, nullable=True)
    resolved_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[ReportStatus] = mapped_column(
        Enum(ReportStatus, name="report_status", values_callable=lambda enum: [item.value for item in enum]),
        default=ReportStatus.OPEN,
        nullable=False,
    )

    student: Mapped["User | None"] = relationship(back_populates="reports", foreign_keys=[student_id])
    pg: Mapped["PGListing"] = relationship(back_populates="reports")
    resolver: Mapped["User | None"] = relationship(foreign_keys=[resolved_by])
