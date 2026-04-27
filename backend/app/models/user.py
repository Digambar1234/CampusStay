import uuid

from sqlalchemy import Boolean, Enum, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from app.models.enums import Role


class User(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "users"

    full_name: Mapped[str] = mapped_column(String(120), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    phone: Mapped[str | None] = mapped_column(String(30), unique=True, index=True, nullable=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[Role] = mapped_column(
        Enum(Role, name="user_role", values_callable=lambda enum: [item.value for item in enum]),
        nullable=False,
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    student_profile: Mapped["StudentProfile | None"] = relationship(back_populates="user", uselist=False)
    owner_profile: Mapped["PGOwnerProfile | None"] = relationship(back_populates="user", uselist=False)
    owned_listings: Mapped[list["PGListing"]] = relationship(back_populates="owner")
    credit_wallet: Mapped["CreditWallet | None"] = relationship(back_populates="student", uselist=False)
    credit_transactions: Mapped[list["CreditTransaction"]] = relationship(back_populates="student")
    contact_unlocks: Mapped[list["ContactUnlock"]] = relationship(back_populates="student")
    payments: Mapped[list["Payment"]] = relationship(back_populates="student")
    reports: Mapped[list["Report"]] = relationship(back_populates="student", foreign_keys="Report.student_id")
    reviews: Mapped[list["Review"]] = relationship(back_populates="student")
    admin_actions: Mapped[list["AdminActionLog"]] = relationship(back_populates="admin")
