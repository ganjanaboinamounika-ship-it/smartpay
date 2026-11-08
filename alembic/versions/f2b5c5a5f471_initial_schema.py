"""initial schema

Revision ID: f2b5c5a5f471
Revises:
Create Date: 2026-11-02 16:09:04.366738
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "f2b5c5a5f471"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create the initial users table."""

    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        "ix_users_email",
        "users",
        ["email"],
        unique=True,
    )


def downgrade() -> None:
    """Remove the initial users table."""

    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")
