"""add selected_text to comments and rename parent_id

Revision ID: add_selected_text_to_comments
Revises: a2215a7ed26f
Create Date: 2025-12-13 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_selected_text_to_comments'
down_revision = 'a2215a7ed26f'
branch_labels = None
depends_on = None


def upgrade():
    # Add selected_text column
    op.add_column('paper_comments', sa.Column('selected_text', sa.Text(), nullable=True))

    # Rename parent_id to parent_comment_id
    op.alter_column('paper_comments', 'parent_id', new_column_name='parent_comment_id')


def downgrade():
    # Rename back
    op.alter_column('paper_comments', 'parent_comment_id', new_column_name='parent_id')

    # Remove selected_text column
    op.drop_column('paper_comments', 'selected_text')
