"""district

Revision ID: 1e79e93de742
Revises: 94df3ca35b5f
Create Date: 2026-09-04 11:21:22.268623
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '1e79e93de742'
down_revision: Union[str, Sequence[str], None] = '94df3ca35b5f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # Step 1: Fill NULL values with a placeholder
    op.execute("UPDATE materials SET district = 'Unknown' WHERE district IS NULL")

    # Step 2: Set default value (optional safeguard)
    op.alter_column(
        'materials',
        'district',
        existing_type=sa.VARCHAR(),
        server_default="Unknown"
    )

    # Step 3: Enforce NOT NULL
    op.alter_column(
        'materials',
        'district',
        existing_type=sa.VARCHAR(),
        nullable=False
    )

def downgrade() -> None:
    # Rollback: allow NULL again and remove default
    op.alter_column(
        'materials',
        'district',
        existing_type=sa.VARCHAR(),
        nullable=True,
        server_default=None
    )
