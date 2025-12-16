"""add user last_active field

Revision ID: add_user_last_active
Revises: add_oauth_tokens_deadline
Create Date: 2025-12-15

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_user_last_active'
down_revision = 'add_oauth_tokens_deadline'
branch_labels = None
depends_on = None


def upgrade():
    # Add last_active_at column to users table
    op.add_column('users', sa.Column('last_active_at', sa.DateTime(), nullable=True))


def downgrade():
    # Remove last_active_at column from users table
    op.drop_column('users', 'last_active_at')
