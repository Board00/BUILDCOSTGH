from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column
from sqlalchemy import String, Boolean
from auth import hash_password   # ✅ reuse your password hashing

# revision identifiers, used by Alembic.
revision = "99101e248f64"
down_revision = "65bf13f3c6c7"
branch_labels = None
depends_on = None

def upgrade():
    # ✅ Only seed first admin user
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
                "username": "Konrad",
                "hashed_password": hash_password("love"),  # ⚠️ replace with strong password
                "is_admin": True,
            }
        ],
    )

def downgrade():
    # Optional: remove seeded admin
    op.execute("DELETE FROM users WHERE username='Konrad'")
