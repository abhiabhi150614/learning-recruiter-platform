"""Add days_generated tracking to learning plans

Revision ID: add_days_generated_tracking
Revises: 34f350f87d1d
Create Date: 2024-01-15 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_days_generated_tracking'
down_revision = '34f350f87d1d'
branch_labels = None
depends_on = None


def upgrade():
    # Update existing learning plans to add days_generated tracking
    connection = op.get_bind()
    
    # Get all learning plans
    result = connection.execute("SELECT id, plan FROM learning_plans")
    
    for row in result:
        plan_id = row[0]
        plan_data = row[1]
        
        if plan_data and isinstance(plan_data, dict) and 'months' in plan_data:
            months = plan_data['months']
            updated = False
            
            for month in months:
                if isinstance(month, dict):
                    # Check if days exist and mark as generated
                    if 'days' in month and month['days'] and len(month['days']) > 0:
                        month['days_generated'] = True
                        updated = True
                    elif 'days' not in month or not month['days']:
                        month['days_generated'] = False
                        updated = True
            
            if updated:
                # Update the plan in database
                connection.execute(
                    "UPDATE learning_plans SET plan = %s WHERE id = %s",
                    (plan_data, plan_id)
                )


def downgrade():
    # Remove days_generated tracking
    connection = op.get_bind()
    
    # Get all learning plans
    result = connection.execute("SELECT id, plan FROM learning_plans")
    
    for row in result:
        plan_id = row[0]
        plan_data = row[1]
        
        if plan_data and isinstance(plan_data, dict) and 'months' in plan_data:
            months = plan_data['months']
            updated = False
            
            for month in months:
                if isinstance(month, dict) and 'days_generated' in month:
                    del month['days_generated']
                    updated = True
            
            if updated:
                # Update the plan in database
                connection.execute(
                    "UPDATE learning_plans SET plan = %s WHERE id = %s",
                    (plan_data, plan_id)
                )
