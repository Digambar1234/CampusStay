"""part5 production indexes

Revision ID: 202604270004
Revises: 202604270003
Create Date: 2026-04-27 00:04:00.000000
"""
from typing import Sequence, Union

from alembic import op

revision: str = "202604270004"
down_revision: Union[str, None] = "202604270003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    indexes = [
        ("ix_pg_listings_admin_verified", "pg_listings", ["admin_verified"]),
        ("ix_pg_listings_monthly_rent_min", "pg_listings", ["monthly_rent_min"]),
        ("ix_pg_listings_distance_from_lpu_km", "pg_listings", ["distance_from_lpu_km"]),
        ("ix_payments_status", "payments", ["status"]),
        ("ix_reports_status", "reports", ["status"]),
        ("ix_featured_listings_ends_at", "featured_listings", ["ends_at"]),
    ]
    for name, table, columns in indexes:
        op.create_index(name, table, columns, unique=False, if_not_exists=True)


def downgrade() -> None:
    for name, table in [
        ("ix_featured_listings_ends_at", "featured_listings"),
        ("ix_reports_status", "reports"),
        ("ix_payments_status", "payments"),
        ("ix_pg_listings_distance_from_lpu_km", "pg_listings"),
        ("ix_pg_listings_monthly_rent_min", "pg_listings"),
        ("ix_pg_listings_admin_verified", "pg_listings"),
    ]:
        op.drop_index(name, table_name=table, if_exists=True)
