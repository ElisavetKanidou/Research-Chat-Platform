"""add comment_updated notification type

Revision ID: add_comment_updated_type
Revises: remove_old_comment_columns
Create Date: 2025-12-13 19:58:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_comment_updated_type'
down_revision = 'remove_old_comment_columns'
branch_labels = None
depends_on = None


def upgrade():
    # Add new enum value to notificationtype
    # Note: This must be done outside transaction in PostgreSQL < 12
    # For PostgreSQL >= 12, this works fine in transaction
    op.execute("ALTER TYPE notificationtype ADD VALUE IF NOT EXISTS 'comment_updated'")


def downgrade():
    # Downgrading enum values is complex and usually not recommended
    # Would require recreating the enum and updating all references
    pass
