"""associate estimates with their owner

Revision ID: a1b2c3d4e5f6
Revises: 903d9859fbe7
"""
from alembic import op
import sqlalchemy as sa

revision = "a1b2c3d4e5f6"
down_revision = "903d9859fbe7"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "estimates",
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
    )
    op.create_index("ix_estimates_user_id", "estimates", ["user_id"])


def downgrade() -> None:
    op.drop_index("ix_estimates_user_id", table_name="estimates")
    op.drop_column("estimates", "user_id")
