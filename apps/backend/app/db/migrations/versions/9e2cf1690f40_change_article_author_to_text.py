
"""change article author to text

Revision ID: 9e2cf1690f40
Revises: 86a0aa6f4d19
Create Date: 2026-11-09 17:16:55.521711
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "9e2cf1690f40"
down_revision: Union[str, Sequence[str], None] = "86a0aa6f4d19"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        "articles",
        "author",
        existing_type=sa.VARCHAR(length=300),
        type_=sa.Text(),
        existing_nullable=True,
    )


def downgrade() -> None:
    op.alter_column(
        "articles",
        "author",
        existing_type=sa.Text(),
        type_=sa.VARCHAR(length=300),
        existing_nullable=True,
    )
