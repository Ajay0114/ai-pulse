"""add article relevance classification fields

Revision ID: 91c9a901db46
Revises: 9e2cf1690f40
Create Date: 2026-11-10 17:52:45.193648

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '91c9a901db46'
down_revision: Union[str, Sequence[str], None] = '9e2cf1690f40'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None



def upgrade() -> None:
    """Upgrade schema."""

    # Add new fields as nullable first to support existing articles.
    op.add_column(
        'articles',
        sa.Column('relevance_status', sa.String(length=30), nullable=True)
    )
    op.add_column(
        'articles',
        sa.Column('relevance_score', sa.Float(), nullable=True)
    )
    op.add_column(
        'articles',
        sa.Column('importance_reason', sa.Text(), nullable=True)
    )
    op.add_column(
        'articles',
        sa.Column('feed_type', sa.String(length=30), nullable=True)
    )

    # Assign initial values to existing articles.
    op.execute(
        "UPDATE articles SET relevance_status = 'pending' "
        "WHERE relevance_status IS NULL"
    )
    op.execute(
        "UPDATE articles SET feed_type = 'pending' "
        "WHERE feed_type IS NULL"
    )

    # Enforce non-null constraints and database-level defaults.
    op.alter_column(
        'articles',
        'relevance_status',
        existing_type=sa.String(length=30),
        nullable=False,
        server_default='pending'
    )
    op.alter_column(
        'articles',
        'feed_type',
        existing_type=sa.String(length=30),
        nullable=False,
        server_default='pending'
    )

    # Add indexes.
    op.create_index(
        op.f('ix_articles_feed_type'),
        'articles',
        ['feed_type'],
        unique=False
    )
    op.create_index(
        op.f('ix_articles_relevance_status'),
        'articles',
        ['relevance_status'],
        unique=False
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_index(
        op.f('ix_articles_relevance_status'),
        table_name='articles'
    )
    op.drop_index(
        op.f('ix_articles_feed_type'),
        table_name='articles'
    )

    op.drop_column('articles', 'feed_type')
    op.drop_column('articles', 'importance_reason')
    op.drop_column('articles', 'relevance_score')
    op.drop_column('articles', 'relevance_status')

