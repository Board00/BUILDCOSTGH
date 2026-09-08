"""remove email and password reset features

Revision ID: d9e1f3a4b5c6
Revises: c8d0e2f3a4b5
"""
from alembic import op

revision = "d9e1f3a4b5c6"
down_revision = "c8d0e2f3a4b5"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_index("ix_password_reset_tokens_token_hash", table_name="password_reset_tokens")
    op.drop_table("password_reset_tokens")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_column("users", "email")


def downgrade() -> None:
    import sqlalchemy as sa

    op.add_column("users", sa.Column("email", sa.String(), nullable=True))
    op.create_index("ix_users_email", "users", ["email"], unique=True)
    op.create_table(
        "password_reset_tokens",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("token_hash", sa.String(), nullable=False),
        sa.Column("expires_at", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column("used_at", sa.TIMESTAMP(timezone=True), nullable=True),
    )
    op.create_index("ix_password_reset_tokens_token_hash", "password_reset_tokens", ["token_hash"], unique=True)