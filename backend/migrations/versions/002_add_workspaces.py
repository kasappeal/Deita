"""Create workspaces table

Revision ID: 002_add_workspaces
Revises: 001_initial
Create Date: 2025-01-01 12:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "002_add_workspaces"
down_revision: Union[str, None] = "001_initial"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade database schema."""
    # Create workspaces table
    op.create_table(
        "workspaces",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("owner_id", sa.Integer(), nullable=True),
        sa.Column("visibility", sa.String(), nullable=False, default="public"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.Column(
            "last_accessed_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_workspaces")),
        sa.ForeignKeyConstraint(
            ["owner_id"], 
            ["users.id"], 
            name=op.f("fk_workspaces_owner_id_users"),
            ondelete="SET NULL"
        ),
    )

    # Create indexes
    op.create_index(op.f("ix_workspaces_id"), "workspaces", ["id"], unique=False)
    op.create_index(op.f("ix_workspaces_owner_id"), "workspaces", ["owner_id"], unique=False)


def downgrade() -> None:
    """Downgrade database schema."""
    # Drop indexes
    op.drop_index(op.f("ix_workspaces_owner_id"), table_name="workspaces")
    op.drop_index(op.f("ix_workspaces_id"), table_name="workspaces")

    # Drop table
    op.drop_table("workspaces")