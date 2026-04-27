"""part4 trust analytics

Revision ID: 202604270003
Revises: 202604270002
Create Date: 2026-04-27 00:03:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "202604270003"
down_revision: Union[str, None] = "202604270002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    review_status = postgresql.ENUM("pending", "approved", "hidden", "rejected", name="review_status", create_type=False)
    report_type = postgresql.ENUM("fake_listing", "wrong_price", "wrong_phone", "room_not_available", "misleading_photos", "abusive_owner", "other", name="report_type", create_type=False)
    report_priority = postgresql.ENUM("low", "medium", "high", name="report_priority", create_type=False)
    featured_status = postgresql.ENUM("active", "expired", "cancelled", "pending", name="featured_listing_status", create_type=False)
    featured_source = postgresql.ENUM("admin_grant", "paid", name="featured_listing_source", create_type=False)
    for enum in [review_status, report_type, report_priority, featured_status, featured_source]:
        enum.create(bind, checkfirst=True)

    op.create_table(
        "reviews",
        sa.Column("student_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("pg_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("rating", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=180), nullable=True),
        sa.Column("comment", sa.Text(), nullable=False),
        sa.Column("status", review_status, nullable=False),
        sa.Column("is_edited", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["pg_id"], ["pg_listings.id"]),
        sa.ForeignKeyConstraint(["student_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("student_id", "pg_id", name="uq_review_student_pg"),
    )
    op.create_index("ix_reviews_pg_id", "reviews", ["pg_id"])
    op.create_index("ix_reviews_status", "reviews", ["status"])
    op.create_index("ix_reviews_student_id", "reviews", ["student_id"])

    op.add_column("reports", sa.Column("reporter_email", sa.String(length=255), nullable=True))
    op.add_column("reports", sa.Column("reporter_phone", sa.String(length=30), nullable=True))
    op.add_column("reports", sa.Column("report_type", report_type, nullable=False, server_default="other"))
    op.add_column("reports", sa.Column("priority", report_priority, nullable=False, server_default="medium"))
    op.add_column("reports", sa.Column("admin_note", sa.Text(), nullable=True))
    op.add_column("reports", sa.Column("resolved_by", postgresql.UUID(as_uuid=True), nullable=True))
    op.add_column("reports", sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True))
    op.create_foreign_key("fk_reports_resolved_by_users", "reports", "users", ["resolved_by"], ["id"])

    op.create_table(
        "featured_listings",
        sa.Column("pg_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("owner_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("status", featured_status, nullable=False),
        sa.Column("starts_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("ends_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("amount_rupees", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("source", featured_source, nullable=False),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["owner_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["pg_id"], ["pg_listings.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_featured_listings_owner_id", "featured_listings", ["owner_id"])
    op.create_index("ix_featured_listings_pg_id", "featured_listings", ["pg_id"])
    op.create_index("ix_featured_listings_status", "featured_listings", ["status"])

    op.create_table(
        "listing_views",
        sa.Column("pg_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("viewer_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("ip_hash", sa.String(length=128), nullable=True),
        sa.Column("user_agent_hash", sa.String(length=128), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.ForeignKeyConstraint(["pg_id"], ["pg_listings.id"]),
        sa.ForeignKeyConstraint(["viewer_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_listing_views_pg_id", "listing_views", ["pg_id"])
    op.create_index("ix_listing_views_viewer_id", "listing_views", ["viewer_id"])


def downgrade() -> None:
    op.drop_table("listing_views")
    op.drop_table("featured_listings")
    op.drop_constraint("fk_reports_resolved_by_users", "reports", type_="foreignkey")
    for col in ["resolved_at", "resolved_by", "admin_note", "priority", "report_type", "reporter_phone", "reporter_email"]:
        op.drop_column("reports", col)
    op.drop_table("reviews")
    bind = op.get_bind()
    for enum_name in ["featured_listing_source", "featured_listing_status", "report_priority", "report_type", "review_status"]:
        sa.Enum(name=enum_name).drop(bind, checkfirst=True)
