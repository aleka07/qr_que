"""Initial migration

Revision ID: 001
Revises: 
Create Date: 2026-01-02

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create order status enum
    op.execute("CREATE TYPE orderstatus AS ENUM ('pending', 'scanned', 'preparing', 'ready', 'completed', 'cancelled')")
    
    # Create orders table
    op.create_table('orders',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('human_id', sa.String(length=50), nullable=False),
        sa.Column('status', postgresql.ENUM('pending', 'scanned', 'preparing', 'ready', 'completed', 'cancelled', name='orderstatus'), nullable=False),
        sa.Column('token', sa.String(length=50), nullable=False),
        sa.Column('device_id', sa.String(length=100), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_orders_human_id'), 'orders', ['human_id'], unique=False)
    op.create_index(op.f('ix_orders_token'), 'orders', ['token'], unique=True)
    op.create_index(op.f('ix_orders_device_id'), 'orders', ['device_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_orders_device_id'), table_name='orders')
    op.drop_index(op.f('ix_orders_token'), table_name='orders')
    op.drop_index(op.f('ix_orders_human_id'), table_name='orders')
    op.drop_table('orders')
    op.execute("DROP TYPE orderstatus")
