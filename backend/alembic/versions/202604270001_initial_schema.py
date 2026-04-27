"""initial schema

Revision ID: 202604270001
Revises:
Create Date: 2026-04-27 00:01:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "202604270001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    user_role = postgresql.ENUM("student", "pg_owner", "admin", "super_admin", name="user_role", create_type=False)
    gender_allowed = postgresql.ENUM("boys", "girls", "co_living", name="gender_allowed", create_type=False)
    listing_status = postgresql.ENUM("draft", "pending_review", "approved", "rejected", "suspended", name="listing_status", create_type=False)
    room_type = postgresql.ENUM("single", "double_sharing", "triple_sharing", "four_sharing", "dormitory", name="room_type", create_type=False)
    image_type = postgresql.ENUM("room", "washroom", "building", "mess", "common_area", "other", name="image_type", create_type=False)
    credit_transaction_type = postgresql.ENUM(
        "free_signup_bonus", "purchase", "contact_unlock", "refund", "admin_adjustment",
        name="credit_transaction_type", create_type=False,
    )
    payment_provider = postgresql.ENUM("razorpay", name="payment_provider", create_type=False)
    payment_status = postgresql.ENUM("created", "paid", "failed", "refunded", name="payment_status", create_type=False)
    report_status = postgresql.ENUM("open", "reviewed", "resolved", "rejected", name="report_status", create_type=False)

    bind = op.get_bind()
    for enum in [
        user_role, gender_allowed, listing_status, room_type, image_type,
        credit_transaction_type, payment_provider, payment_status, report_status,
    ]:
        enum.create(bind, checkfirst=True)

    op.create_table(
        "users",
        sa.Column("full_name", sa.String(length=120), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("phone", sa.String(length=30), nullable=True),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("role", user_role, nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("is_verified", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)
    op.create_index("ix_users_phone", "users", ["phone"], unique=True)

    op.create_table(
        "student_profiles",
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("university_name", sa.String(length=160), nullable=False),
        sa.Column("course", sa.String(length=120), nullable=True),
        sa.Column("year", sa.String(length=30), nullable=True),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id"),
    )
    op.create_table(
        "pg_owner_profiles",
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("business_name", sa.String(length=160), nullable=True),
        sa.Column("alternate_phone", sa.String(length=30), nullable=True),
        sa.Column("is_owner_verified", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id"),
    )
    op.create_table(
        "pg_listings",
        sa.Column("owner_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("pg_name", sa.String(length=180), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("address", sa.String(length=500), nullable=False),
        sa.Column("landmark", sa.String(length=180), nullable=True),
        sa.Column("distance_from_lpu_km", sa.Numeric(5, 2), nullable=True),
        sa.Column("latitude", sa.Numeric(10, 7), nullable=True),
        sa.Column("longitude", sa.Numeric(10, 7), nullable=True),
        sa.Column("gender_allowed", gender_allowed, nullable=False),
        sa.Column("food_available", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("wifi_available", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("ac_available", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("laundry_available", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("parking_available", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("security_available", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("monthly_rent_min", sa.Integer(), nullable=True),
        sa.Column("monthly_rent_max", sa.Integer(), nullable=True),
        sa.Column("deposit_amount", sa.Integer(), nullable=True),
        sa.Column("owner_phone", sa.String(length=30), nullable=False),
        sa.Column("whatsapp_number", sa.String(length=30), nullable=True),
        sa.Column("status", listing_status, nullable=False),
        sa.Column("admin_verified", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["owner_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_pg_listings_owner_id", "pg_listings", ["owner_id"])
    op.create_index("ix_pg_listings_status", "pg_listings", ["status"])

    op.create_table(
        "credit_wallets",
        sa.Column("student_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("balance", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["student_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("student_id"),
    )
    op.create_table(
        "credit_transactions",
        sa.Column("student_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("type", credit_transaction_type, nullable=False),
        sa.Column("amount", sa.Integer(), nullable=False),
        sa.Column("reason", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.ForeignKeyConstraint(["student_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_credit_transactions_student_id", "credit_transactions", ["student_id"])

    op.create_table(
        "payments",
        sa.Column("student_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("provider", payment_provider, nullable=False),
        sa.Column("provider_order_id", sa.String(length=255), nullable=True),
        sa.Column("provider_payment_id", sa.String(length=255), nullable=True),
        sa.Column("amount_rupees", sa.Integer(), nullable=False),
        sa.Column("credits_purchased", sa.Integer(), nullable=False),
        sa.Column("status", payment_status, nullable=False),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["student_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_payments_student_id", "payments", ["student_id"])

    op.create_table(
        "pg_rooms",
        sa.Column("pg_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("room_type", room_type, nullable=False),
        sa.Column("price_per_month", sa.Integer(), nullable=False),
        sa.Column("available_beds", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("ac_available", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("attached_washroom", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["pg_id"], ["pg_listings.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_pg_rooms_pg_id", "pg_rooms", ["pg_id"])
    op.create_table(
        "pg_photos",
        sa.Column("pg_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("image_url", sa.String(length=1000), nullable=False),
        sa.Column("image_type", image_type, nullable=False),
        sa.Column("is_primary", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.ForeignKeyConstraint(["pg_id"], ["pg_listings.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_pg_photos_pg_id", "pg_photos", ["pg_id"])
    op.create_table(
        "contact_unlocks",
        sa.Column("student_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("pg_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("credits_used", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.ForeignKeyConstraint(["pg_id"], ["pg_listings.id"]),
        sa.ForeignKeyConstraint(["student_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("student_id", "pg_id", name="uq_contact_unlock_student_pg"),
    )
    op.create_index("ix_contact_unlocks_pg_id", "contact_unlocks", ["pg_id"])
    op.create_index("ix_contact_unlocks_student_id", "contact_unlocks", ["student_id"])
    op.create_table(
        "reports",
        sa.Column("student_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("pg_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("reason", sa.String(length=180), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("status", report_status, nullable=False),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["pg_id"], ["pg_listings.id"]),
        sa.ForeignKeyConstraint(["student_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_reports_pg_id", "reports", ["pg_id"])
    op.create_table(
        "admin_action_logs",
        sa.Column("admin_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("action", sa.String(length=120), nullable=False),
        sa.Column("target_type", sa.String(length=120), nullable=False),
        sa.Column("target_id", sa.String(length=120), nullable=True),
        sa.Column("metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.ForeignKeyConstraint(["admin_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_admin_action_logs_admin_id", "admin_action_logs", ["admin_id"])


def downgrade() -> None:
    for table in [
        "admin_action_logs", "reports", "contact_unlocks", "pg_photos", "pg_rooms",
        "payments", "credit_transactions", "credit_wallets", "pg_listings",
        "pg_owner_profiles", "student_profiles", "users",
    ]:
        op.drop_table(table)

    bind = op.get_bind()
    for enum_name in [
        "report_status", "payment_status", "payment_provider", "credit_transaction_type",
        "image_type", "room_type", "listing_status", "gender_allowed", "user_role",
    ]:
        sa.Enum(name=enum_name).drop(bind, checkfirst=True)
