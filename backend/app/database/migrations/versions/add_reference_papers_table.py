"""Add reference_papers table for AI personalization

Revision ID: add_reference_papers
Revises: add_user_last_active
Create Date: 2025-12-16

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_reference_papers'
down_revision = 'add_user_last_active'
branch_labels = None
depends_on = None


def upgrade():
    """Create reference_papers table"""
    # Create enum type for paper_type
    paper_type_enum = postgresql.ENUM('lab', 'personal', 'literature', name='papertype')
    paper_type_enum.create(op.get_bind(), checkfirst=True)

    op.create_table(
        'reference_papers',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),

        # Foreign keys
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),

        # Paper information
        sa.Column('title', sa.String(length=500), nullable=False),
        sa.Column('authors', sa.String(length=500), nullable=True),
        sa.Column('year', sa.Integer(), nullable=True),
        sa.Column('journal', sa.String(length=300), nullable=True),
        sa.Column('doi', sa.String(length=200), nullable=True),

        # Paper type and categorization
        sa.Column('paper_type', paper_type_enum, nullable=False),
        sa.Column('research_area', sa.String(length=200), nullable=True),
        sa.Column('keywords', postgresql.JSON(astext_type=sa.Text()), nullable=True),

        # File storage
        sa.Column('file_url', sa.String(length=500), nullable=False),
        sa.Column('file_size', sa.Integer(), nullable=True),
        sa.Column('original_filename', sa.String(length=300), nullable=False),

        # Extracted content
        sa.Column('content_text', sa.Text(), nullable=True),
        sa.Column('abstract', sa.Text(), nullable=True),

        # Analysis status
        sa.Column('is_analyzed', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('analysis_date', sa.String(length=50), nullable=True),

        # Writing style analysis
        sa.Column('writing_style_features', postgresql.JSON(astext_type=sa.Text()), nullable=True),

        # Metadata
        sa.Column('metadata', postgresql.JSON(astext_type=sa.Text()), nullable=True),

        # Usage tracking
        sa.Column('times_used', sa.Integer(), nullable=False, server_default='0'),

        # Constraints
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(
            ['user_id'],
            ['users.id'],
            name='fk_reference_papers_user_id',
            ondelete='CASCADE'
        )
    )

    # Create indexes
    op.create_index(
        'ix_reference_papers_user_id',
        'reference_papers',
        ['user_id']
    )
    op.create_index(
        'ix_reference_papers_paper_type',
        'reference_papers',
        ['paper_type']
    )
    op.create_index(
        'ix_reference_papers_is_analyzed',
        'reference_papers',
        ['is_analyzed']
    )


def downgrade():
    """Drop reference_papers table"""
    op.drop_index('ix_reference_papers_is_analyzed', table_name='reference_papers')
    op.drop_index('ix_reference_papers_paper_type', table_name='reference_papers')
    op.drop_index('ix_reference_papers_user_id', table_name='reference_papers')
    op.drop_table('reference_papers')

    # Drop enum type
    paper_type_enum = postgresql.ENUM('lab', 'personal', 'literature', name='papertype')
    paper_type_enum.drop(op.get_bind(), checkfirst=True)
