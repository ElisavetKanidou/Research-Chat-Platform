"""remove old comment columns

Revision ID: remove_old_comment_columns
Revises: add_selected_text_to_comments
Create Date: 2025-12-13 13:15:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'remove_old_comment_columns'
down_revision = 'add_selected_text_to_comments'
branch_labels = None
depends_on = None


def upgrade():
    # Remove old unused columns from the original schema
    op.drop_column('paper_comments', 'comment_type')
    op.drop_column('paper_comments', 'line_number')
    op.drop_column('paper_comments', 'thread_id')


def downgrade():
    # Add them back if needed (for rollback)
    op.add_column('paper_comments', sa.Column('comment_type', sa.String(length=20), nullable=False, server_default='general'))
    op.add_column('paper_comments', sa.Column('line_number', sa.Integer(), nullable=True))
    op.add_column('paper_comments', sa.Column('thread_id', sa.UUID(), nullable=True))
