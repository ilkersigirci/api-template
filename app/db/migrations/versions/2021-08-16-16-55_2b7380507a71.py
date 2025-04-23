"""Created Initial Tables.

Revision ID: 2b7380507a71
Revises: 819cbf6e030b
Create Date: 2021-08-16 16:55:25.157309

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "2b7380507a71"
down_revision = "819cbf6e030b"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Run the upgrade migrations."""
    op.create_table(
        "user",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=200), nullable=True),
        sa.Column("email", sa.String(length=200), nullable=True),
        sa.Column("hashed_password", sa.String(length=200), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "item",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=200), nullable=True),
        sa.Column("description", sa.String(length=200), nullable=True),
        sa.Column("price", sa.Float(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    """Run the downgrade migrations."""
    op.drop_table("user")
    op.drop_table("item")
    # ### end Alembic commands ###
