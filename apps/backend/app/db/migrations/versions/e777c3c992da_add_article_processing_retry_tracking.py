"""add article processing retry tracking

Revision ID: e777c3c992da
Revises: 91c9a901db46
Create Date: 2026-11-10 18:14:51.378964

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e777c3c992da'
down_revision: Union[str, Sequence[str], None] = '91c9a901db46'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None



def upgrade() -> None:
    """Upgrade schema."""

    # Add processing_attempts as nullable initially.
    op.add_column(
        'articles',
        sa.Column('processing_attempts', sa.Integer(), nullable=True)
    )

    # Initialize existing articles.
    op.execute(
        "UPDATE articles SET processing_attempts = 0 "
        "WHERE processing_attempts IS NULL"
    )

    # Enforce non-null and database-level default.
    op.alter_column(
        'articles',
        'processing_attempts',
        existing_type=sa.Integer(),
        nullable=False,
        server_default='0'
    )

    # Add optional retry information.
    op.add_column(
        'articles',
        sa.Column('last_processing_error', sa.Text(), nullable=True)
    )

    op.add_column(
        'articles',
        sa.Column(
            'next_retry_at',
            sa.DateTime(timezone=True),
            nullable=True
        )
    )

    # Index retry scheduling.
    op.create_index(
        op.f('ix_articles_next_retry_at'),
        'articles',
        ['next_retry_at'],
        unique=False
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_index(
        op.f('ix_articles_next_retry_at'),
        table_name='articles'
    )

    op.drop_column('articles', 'next_retry_at')
    op.drop_column('articles', 'last_processing_error')
    op.drop_column('articles', 'processing_attempts')
