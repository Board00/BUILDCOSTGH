"""initial migration

Revision ID: 8f8cdb60e87a
Revises: 
Create Date: 2026-09-03 18:37:51.852846

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8f8cdb60e87a'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table("materials", sa.Column("id", sa.Integer, primary_key=True), sa.Column("region", sa.String, nullable=False), sa.Column("item", sa.String, nullable=False), sa.Column("unit", sa.String, nullable=False), sa.Column("price", sa.Numeric, nullable=False), sa.Column("source", sa.String, nullable=False), sa.Column("date", sa.Date, server_default=sa.text("CURRENT_DATE")))
    op.create_index("ix_materials_region", "materials", ["region"])
    op.create_table("labor_rates", sa.Column("id", sa.Integer, primary_key=True), sa.Column("region", sa.String, nullable=False), sa.Column("trade", sa.String, nullable=False), sa.Column("rate", sa.Numeric, nullable=False), sa.Column("source", sa.String, nullable=False), sa.Column("date", sa.Date, server_default=sa.text("CURRENT_DATE")))
    op.create_index("ix_labor_rates_region", "labor_rates", ["region"])
    op.create_table("land_prices", sa.Column("id", sa.Integer, primary_key=True), sa.Column("district", sa.String, nullable=False), sa.Column("price", sa.Numeric, nullable=False), sa.Column("source", sa.String, nullable=False), sa.Column("date", sa.Date, server_default=sa.text("CURRENT_DATE")))
    op.create_table("permits", sa.Column("id", sa.Integer, primary_key=True), sa.Column("region", sa.String, nullable=False), sa.Column("fee_type", sa.String, nullable=False), sa.Column("amount", sa.Numeric, nullable=False), sa.Column("source", sa.String, nullable=False), sa.Column("date", sa.Date, server_default=sa.text("CURRENT_DATE")))
    op.create_table("users", sa.Column("id", sa.Integer, primary_key=True), sa.Column("username", sa.String, nullable=False, unique=True), sa.Column("hashed_password", sa.String, nullable=False), sa.Column("created_at", sa.Date, server_default=sa.text("CURRENT_DATE")))
    op.create_table("estimates", sa.Column("id", sa.Integer, primary_key=True), sa.Column("user_input", sa.JSON, nullable=False), sa.Column("itemized", sa.JSON, nullable=False), sa.Column("total", sa.Numeric, nullable=False), sa.Column("confidence", sa.String, nullable=False), sa.Column("created_at", sa.Date, server_default=sa.text("CURRENT_DATE")))
    op.create_table("saved_estimates", sa.Column("id", sa.Integer, primary_key=True), sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id"), nullable=False), sa.Column("estimate", sa.JSON, nullable=False), sa.Column("created_at", sa.Date, server_default=sa.text("CURRENT_DATE")))
    op.create_table("feedback", sa.Column("id", sa.Integer, primary_key=True), sa.Column("estimate_id", sa.Integer, sa.ForeignKey("estimates.id"), nullable=False), sa.Column("actual_cost", sa.Numeric, nullable=False), sa.Column("notes", sa.String), sa.Column("submitted_at", sa.Date, server_default=sa.text("CURRENT_DATE")))


def downgrade() -> None:
    """Downgrade schema."""
    for table_name in ("feedback", "saved_estimates", "estimates", "users", "permits", "land_prices", "labor_rates", "materials"):
        op.drop_table(table_name)
