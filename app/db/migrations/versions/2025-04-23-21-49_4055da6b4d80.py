"""add_admin_user.

Revision ID: 4055da6b4d80
Revises: 2b7380507a71
Create Date: 2025-04-23 21:49:35.409310

"""

from alembic import op
from sqlalchemy.sql import column, table
from sqlalchemy.sql.sqltypes import Integer, String

from app.api.auth.utils import get_password_hash

# revision identifiers, used by Alembic.
revision = "4055da6b4d80"
down_revision = "2b7380507a71"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Run the migration to add admin user."""
    # Create a table representation for inserting data
    user_table = table(
        "user",
        column("id", Integer),
        column("name", String),
        column("email", String),
        column("hashed_password", String),
    )

    # Generate hashed password for admin user
    hashed_password = get_password_hash("admin")

    # Insert admin user
    op.bulk_insert(
        user_table,
        [
            {
                "name": "admin",
                "email": "admin@mail.com",
                "hashed_password": hashed_password,
            }
        ],
    )


def downgrade() -> None:
    """Undo the migration by removing the admin user."""
    op.execute("DELETE FROM user WHERE email = 'admin@mail.com'")
