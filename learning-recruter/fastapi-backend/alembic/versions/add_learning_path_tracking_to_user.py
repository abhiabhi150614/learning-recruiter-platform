"""Add learning path tracking to user model and create day_progress table

Revision ID: add_learning_path_tracking_to_user
Revises: add_days_generated_tracking
Create Date: 2024-01-15 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_learning_path_tracking_to_user'
down_revision = 'add_days_generated_tracking'
branch_labels = None
depends_on = None


def upgrade():
    # Add new columns to learning_paths table
    op.add_column('learning_paths', sa.Column('current_day', sa.Integer(), nullable=True, server_default='1'))
    op.add_column('learning_paths', sa.Column('days_completed', sa.Integer(), nullable=True, server_default='0'))
    op.add_column('learning_paths', sa.Column('total_days', sa.Integer(), nullable=True, server_default='30'))
    op.add_column('learning_paths', sa.Column('last_activity_at', sa.DateTime(), nullable=True))
    op.add_column('learning_paths', sa.Column('days_data', sa.JSON(), nullable=True))
    op.add_column('learning_paths', sa.Column('updated_at', sa.DateTime(), nullable=True))
    
    # Create day_progress table
    op.create_table('day_progress',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('plan_id', sa.Integer(), nullable=False),
        sa.Column('month_index', sa.Integer(), nullable=False),
        sa.Column('day_number', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(), nullable=False, server_default='locked'),
        sa.Column('started_at', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('quiz_score', sa.Integer(), nullable=True),
        sa.Column('quiz_attempts', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('best_score', sa.Integer(), nullable=True),
        sa.Column('content_viewed', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('time_spent', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('can_proceed', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['plan_id'], ['learning_plans.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for better performance
    op.create_index(op.f('ix_day_progress_user_id'), 'day_progress', ['user_id'], unique=False)
    op.create_index(op.f('ix_day_progress_plan_id'), 'day_progress', ['plan_id'], unique=False)
    op.create_index(op.f('ix_day_progress_month_index'), 'day_progress', ['month_index'], unique=False)
    op.create_index(op.f('ix_day_progress_day_number'), 'day_progress', ['day_number'], unique=False)
    
    # Create unique constraint to prevent duplicate day progress entries
    op.create_unique_constraint('uq_day_progress_user_plan_month_day', 'day_progress', ['user_id', 'plan_id', 'month_index', 'day_number'])


def downgrade():
    # Remove unique constraint
    op.drop_constraint('uq_day_progress_user_plan_month_day', 'day_progress', type_='unique')
    
    # Remove indexes
    op.drop_index(op.f('ix_day_progress_day_number'), table_name='day_progress')
    op.drop_index(op.f('ix_day_progress_month_index'), table_name='day_progress')
    op.drop_index(op.f('ix_day_progress_plan_id'), table_name='day_progress')
    op.drop_index(op.f('ix_day_progress_user_id'), table_name='day_progress')
    
    # Drop day_progress table
    op.drop_table('day_progress')
    
    # Remove columns from learning_paths table
    op.drop_column('learning_paths', 'updated_at')
    op.drop_column('learning_paths', 'days_data')
    op.drop_column('learning_paths', 'last_activity_at')
    op.drop_column('learning_paths', 'total_days')
    op.drop_column('learning_paths', 'days_completed')
    op.drop_column('learning_paths', 'current_day')
