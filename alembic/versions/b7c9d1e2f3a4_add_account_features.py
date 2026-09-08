"""add account profile, reset, and referral fields

Revision ID: b7c9d1e2f3a4
Revises: a1b2c3d4e5f6
"""
from alembic import op
import sqlalchemy as sa

revision = "b7c9d1e2f3a4"
down_revision = "a1b2c3d4e5f6"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("users", sa.Column("email", sa.String(), nullable=True))
    op.add_column("users", sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()))
    op.add_column("users", sa.Column("referral_code", sa.String(), nullable=True))
    op.add_column("users", sa.Column("referred_by_id", sa.Integer(), nullable=True))
    op.execute("UPDATE users SET referral_code = 'REF' || id WHERE referral_code IS NULL")
    op.create_index("ix_users_email", "users", ["email"], unique=True)
    op.create_index("ix_users_referral_code", "users", ["referral_code"], unique=True)
    op.create_foreign_key("fk_users_referred_by_id", "users", "users", ["referred_by_id"], ["id"])
    op.create_table(
        "password_reset_tokens",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("token_hash", sa.String(), nullable=False),
        sa.Column("expires_at", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column("used_at", sa.TIMESTAMP(timezone=True), nullable=True),
    )
    op.create_index("ix_password_reset_tokens_token_hash", "password_reset_tokens", ["token_hash"], unique=True)


def downgrade() -> None:
    op.drop_index("ix_password_reset_tokens_token_hash", table_name="password_reset_tokens")
    op.drop_table("password_reset_tokens")
    op.drop_constraint("fk_users_referred_by_id", "users", type_="foreignkey")
    op.drop_index("ix_users_referral_code", table_name="users")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_column("users", "referred_by_id")
    op.drop_column("users", "referral_code")
    op.drop_column("users", "is_active")
    op.drop_column("users", "email")