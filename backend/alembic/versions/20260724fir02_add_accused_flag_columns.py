"""add accused flag columns

Revision ID: 20260724fir02
Revises: 20260707fir01
Create Date: 2026-07-24 00:00:00
"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "20260724fir02"
down_revision: str | None = "20260707fir01"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "Accused",
        sa.Column("Flagged", sa.Boolean(), nullable=True),
    )
    op.add_column(
        "Accused",
        sa.Column("FlagReason", sa.Text(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("Accused", "FlagReason")
    op.drop_column("Accused", "Flagged")
