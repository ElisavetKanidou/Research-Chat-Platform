"""Add OAuth tokens table and deadline to papers

Revision ID: add_oauth_tokens_deadline
Revises: cf9312be3c74
Create Date: 2025-12-14

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_oauth_tokens_deadline'
down_revision = 'add_comment_updated_type'
branch_labels = None
depends_on = None


def upgrade():
    # Create oauth_tokens table
    op.create_table('oauth_tokens',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('service', sa.String(length=50), nullable=False),
        sa.Column('access_token', sa.Text(), nullable=False),
        sa.Column('refresh_token', sa.Text(), nullable=True),
        sa.Column('token_type', sa.String(length=50), nullable=True),
        sa.Column('expires_at', sa.DateTime(), nullable=True),
        sa.Column('token_metadata', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_oauth_tokens_user_id'), 'oauth_tokens', ['user_id'], unique=False)
    op.create_index(op.f('ix_oauth_tokens_service'), 'oauth_tokens', ['service'], unique=False)

    # Add deadline column to papers table
    op.add_column('papers', sa.Column('deadline', sa.DateTime(), nullable=True))


def downgrade():
    # Remove deadline column from papers
    op.drop_column('papers', 'deadline')

    # Drop oauth_tokens table
    op.drop_index(op.f('ix_oauth_tokens_service'), table_name='oauth_tokens')
    op.drop_index(op.f('ix_oauth_tokens_user_id'), table_name='oauth_tokens')
    op.drop_table('oauth_tokens')
