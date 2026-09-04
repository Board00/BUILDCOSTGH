from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column
from sqlalchemy import String, Boolean
import os
from auth import hash_password

# revision identifiers, used by Alembic.
revision = "99101e248f64"
down_revision = "65bf13f3c6c7"
branch_labels = None
depends_on = None

def upgrade():
    username = os.getenv("INITIAL_ADMIN_USERNAME")
    password = os.getenv("INITIAL_ADMIN_PASSWORD")
    if not username or not password:
        return

    users_table = table(
        "users",
        column("username", String),
        column("hashed_password", String),
        column("is_admin", Boolean),
    )

    op.bulk_insert(
        users_table,
        [
            {
                "username": username,
                "hashed_password": hash_password(password),
                "is_admin": True,
            }
        ],
    )

def downgrade():
    username = os.getenv("INITIAL_ADMIN_USERNAME")
    if username:
        op.execute("DELETE FROM users WHERE username=:username", {"username": username})
