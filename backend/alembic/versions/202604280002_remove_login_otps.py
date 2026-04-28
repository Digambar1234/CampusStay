"""remove login otps

Revision ID: 202604280002
Revises: 202604280001
Create Date: 2026-04-28 00:02:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "202604280002"
down_revision: Union[str, None] = "202604280001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_index("ix_login_otps_phone", table_name="login_otps", if_exists=True)
    op.drop_index("ix_login_otps_user_id", table_name="login_otps", if_exists=True)
    op.drop_table("login_otps", if_exists=True)


def downgrade() -> None:
    op.create_table(
        "login_otps",
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("phone", sa.String(length=30), nullable=False),
        sa.Column("code_hash", sa.String(length=128), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("attempts", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("consumed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_login_otps_phone", "login_otps", ["phone"])
    op.create_index("ix_login_otps_user_id", "login_otps", ["user_id"])
