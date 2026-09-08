"""remove referral features from users

Revision ID: c8d0e2f3a4b5
Revises: b7c9d1e2f3a4
"""
from alembic import op

revision = "c8d0e2f3a4b5"
down_revision = "b7c9d1e2f3a4"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_constraint("fk_users_referred_by_id", "users", type_="foreignkey")
    op.drop_index("ix_users_referral_code", table_name="users")
    op.drop_column("users", "referred_by_id")
    op.drop_column("users", "referral_code")


def downgrade() -> None:
    import sqlalchemy as sa

    op.add_column("users", sa.Column("referral_code", sa.String(), nullable=True))
    op.add_column("users", sa.Column("referred_by_id", sa.Integer(), nullable=True))
    op.create_index("ix_users_referral_code", "users", ["referral_code"], unique=True)
    op.create_foreign_key("fk_users_referred_by_id", "users", "users", ["referred_by_id"], ["id"])