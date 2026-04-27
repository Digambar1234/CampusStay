"""add pg photo public id

Revision ID: 202604270002
Revises: 202604270001
Create Date: 2026-04-27 00:02:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "202604270002"
down_revision: Union[str, None] = "202604270001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("pg_photos", sa.Column("public_id", sa.String(length=500), nullable=True))


def downgrade() -> None:
    op.drop_column("pg_photos", "public_id")
