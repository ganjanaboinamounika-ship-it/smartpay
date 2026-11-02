"""add user role

Revision ID: e6aae94deca3
Revises: f2b5c5a5f471
Create Date: 2026-11-02
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "e6aae94deca3"
down_revision: Union[str, Sequence[str], None] = "f2b5c5a5f471"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    user_role = sa.Enum(
        "CUSTOMER",
        "ADMIN",
        "FRAUD_ANALYST",
        name="user_role",
    )

    user_role.create(op.get_bind(), checkfirst=True)

    op.add_column(
        "users",
        sa.Column(
            "role",
            user_role,
            nullable=False,
            server_default="CUSTOMER",
        ),
    )

    op.alter_column(
        "users",
        "role",
        server_default=None,
    )


def downgrade() -> None:
    op.drop_column("users", "role")

    user_role = sa.Enum(
        "CUSTOMER",
        "ADMIN",
        "FRAUD_ANALYST",
        name="user_role",
    )

    user_role.drop(op.get_bind(), checkfirst=True)