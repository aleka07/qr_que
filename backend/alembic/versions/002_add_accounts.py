"""Add accounts (organizations, locations, users)

Revision ID: 002
Revises: 001
Create Date: 2026-01-02

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create user role enum (if not exists)
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE userrole AS ENUM ('admin', 'owner', 'manager', 'staff');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)
    
    # Create organizations table (if not exists)
    op.execute("""
        CREATE TABLE IF NOT EXISTS organizations (
            id UUID NOT NULL PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            slug VARCHAR(50) NOT NULL,
            logo_url VARCHAR(255),
            is_active BOOLEAN NOT NULL DEFAULT true,
            is_demo BOOLEAN NOT NULL DEFAULT false,
            created_at TIMESTAMP NOT NULL,
            updated_at TIMESTAMP NOT NULL
        )
    """)
    op.execute("CREATE UNIQUE INDEX IF NOT EXISTS ix_organizations_slug ON organizations (slug)")
    
    # Create locations table (if not exists)
    op.execute("""
        CREATE TABLE IF NOT EXISTS locations (
            id UUID NOT NULL PRIMARY KEY,
            organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
            name VARCHAR(100) NOT NULL,
            slug VARCHAR(50) NOT NULL,
            mall_name VARCHAR(100),
            city VARCHAR(50),
            address TEXT,
            is_active BOOLEAN NOT NULL DEFAULT true,
            created_at TIMESTAMP NOT NULL,
            updated_at TIMESTAMP NOT NULL
        )
    """)
    op.execute("CREATE INDEX IF NOT EXISTS ix_locations_slug ON locations (slug)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_locations_organization_id ON locations (organization_id)")
    
    # Create users table (if not exists)
    op.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id UUID NOT NULL PRIMARY KEY,
            organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
            location_id UUID REFERENCES locations(id) ON DELETE SET NULL,
            username VARCHAR(50) NOT NULL,
            email VARCHAR(100),
            hashed_password VARCHAR(255) NOT NULL,
            full_name VARCHAR(100),
            role userrole NOT NULL,
            is_active BOOLEAN NOT NULL DEFAULT true,
            created_at TIMESTAMP NOT NULL,
            updated_at TIMESTAMP NOT NULL,
            last_login TIMESTAMP
        )
    """)
    op.execute("CREATE UNIQUE INDEX IF NOT EXISTS ix_users_username ON users (username)")
    op.execute("CREATE UNIQUE INDEX IF NOT EXISTS ix_users_email ON users (email)")
    
    # Add location_id to orders table (if not exists)
    op.execute("""
        DO $$ BEGIN
            ALTER TABLE orders ADD COLUMN location_id UUID REFERENCES locations(id);
        EXCEPTION
            WHEN duplicate_column THEN null;
        END $$;
    """)
    op.execute("CREATE INDEX IF NOT EXISTS ix_orders_location_id ON orders (location_id)")


def downgrade() -> None:
    # Remove location_id from orders
    op.drop_index(op.f('ix_orders_location_id'), table_name='orders')
    op.drop_column('orders', 'location_id')
    
    # Drop users table
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_index(op.f('ix_users_username'), table_name='users')
    op.drop_table('users')
    
    # Drop locations table
    op.drop_index(op.f('ix_locations_organization_id'), table_name='locations')
    op.drop_index(op.f('ix_locations_slug'), table_name='locations')
    op.drop_table('locations')
    
    # Drop organizations table
    op.drop_index(op.f('ix_organizations_slug'), table_name='organizations')
    op.drop_table('organizations')
    
    # Drop enum
    op.execute("DROP TYPE userrole")
