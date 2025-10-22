"""Add recruiter tracking to users

Revision ID: add_recruiter_tracking
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_recruiter_tracking'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Add created_by_recruiter_id column to users table
    op.add_column('users', sa.Column('created_by_recruiter_id', sa.Integer(), nullable=True))
    op.create_foreign_key('fk_users_created_by_recruiter', 'users', 'users', ['created_by_recruiter_id'], ['id'])

def downgrade():
    # Remove the column and foreign key
    op.drop_constraint('fk_users_created_by_recruiter', 'users', type_='foreignkey')
    op.drop_column('users', 'created_by_recruiter_id')