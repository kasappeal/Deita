"""merge queries and row_count migrations

Revision ID: 8d748dd07d74
Revises: 004_add_queries, ffa3cc0330b3
Create Date: 2025-10-03 10:14:21.762467+00:00

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "8d748dd07d74"
down_revision: Union[str, None] = ("004_add_queries", "ffa3cc0330b3")
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade database schema."""
    pass


def downgrade() -> None:
    """Downgrade database schema."""
    pass
