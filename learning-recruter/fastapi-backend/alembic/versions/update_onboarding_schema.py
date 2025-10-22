"""update onboarding schema for personalized learning

Revision ID: update_onboarding_schema
Revises: 34f350f87d1d
Create Date: 2024-01-01 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'update_onboarding_schema'
down_revision = '34f350f87d1d'
branch_labels = None
depends_on = None


def upgrade():
    # Drop old columns
    op.drop_column('onboarding', 'goals')
    op.drop_column('onboarding', 'custom_goal')
    op.drop_column('onboarding', 'skills')
    op.drop_column('onboarding', 'custom_skill')
    op.drop_column('onboarding', 'learning_style')
    op.drop_column('onboarding', 'time_availability')
    op.drop_column('onboarding', 'subjects')
    
    # Add new columns
    op.add_column('onboarding', sa.Column('career_goals', postgresql.JSONB(astext_type=sa.Text()), nullable=True))
    op.add_column('onboarding', sa.Column('current_skills', postgresql.JSONB(astext_type=sa.Text()), nullable=True))
    op.add_column('onboarding', sa.Column('time_commitment', sa.String(), nullable=True))


def downgrade():
    # Drop new columns
    op.drop_column('onboarding', 'career_goals')
    op.drop_column('onboarding', 'current_skills')
    op.drop_column('onboarding', 'time_commitment')
    
    # Add back old columns
    op.add_column('onboarding', sa.Column('goals', postgresql.JSONB(astext_type=sa.Text()), nullable=True))
    op.add_column('onboarding', sa.Column('custom_goal', sa.String(), nullable=True))
    op.add_column('onboarding', sa.Column('skills', postgresql.JSONB(astext_type=sa.Text()), nullable=True))
    op.add_column('onboarding', sa.Column('custom_skill', sa.String(), nullable=True))
    op.add_column('onboarding', sa.Column('learning_style', sa.String(), nullable=True))
    op.add_column('onboarding', sa.Column('time_availability', sa.String(), nullable=True))
    op.add_column('onboarding', sa.Column('subjects', postgresql.JSONB(astext_type=sa.Text()), nullable=True))
