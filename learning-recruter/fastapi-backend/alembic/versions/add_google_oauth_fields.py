"""Add Google OAuth fields to User model

Revision ID: add_google_oauth_fields
Revises: 
Create Date: 2024-01-01 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_google_oauth_fields'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Add Google OAuth fields to users table
    op.add_column('users', sa.Column('google_id', sa.String(), nullable=True))
    op.add_column('users', sa.Column('google_email', sa.String(), nullable=True))
    op.add_column('users', sa.Column('google_name', sa.String(), nullable=True))
    op.add_column('users', sa.Column('google_picture', sa.String(), nullable=True))
    op.add_column('users', sa.Column('is_google_authenticated', sa.Boolean(), nullable=False, server_default='false'))
    
    # Make hashed_password nullable for Google users
    op.alter_column('users', 'hashed_password', nullable=True)
    
    # Create indexes for Google fields
    op.create_index(op.f('ix_users_google_id'), 'users', ['google_id'], unique=True)

def downgrade():
    # Remove indexes
    op.drop_index(op.f('ix_users_google_id'), table_name='users')
    
    # Remove Google OAuth fields
    op.drop_column('users', 'is_google_authenticated')
    op.drop_column('users', 'google_picture')
    op.drop_column('users', 'google_name')
    op.drop_column('users', 'google_email')
    op.drop_column('users', 'google_id')
    
    # Make hashed_password non-nullable again
    op.alter_column('users', 'hashed_password', nullable=False) 