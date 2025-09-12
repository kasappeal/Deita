"""Add workspace tables and update users to UUID

Revision ID: 002_workspace_tables
Revises: 001_initial
Create Date: 2025-01-27 12:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "002_workspace_tables"
down_revision: Union[str, None] = "001_initial"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade database schema."""
    
    # First, update users table to use UUID primary key
    # Note: In production, this would require careful data migration
    op.execute("CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\"")
    
    # Add new UUID column to users table
    op.add_column('users', sa.Column('uuid_id', postgresql.UUID(as_uuid=True), server_default=sa.text("uuid_generate_v4()"), nullable=False))
    
    # Create unique index on new UUID column
    op.create_index('ix_users_uuid_id', 'users', ['uuid_id'], unique=False)
    
    # Create workspaces table
    op.create_table(
        'workspaces',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text("uuid_generate_v4()"), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('owner_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('is_public', sa.Boolean(), nullable=False, default=True),
        sa.Column('is_orphan', sa.Boolean(), nullable=False, default=False),
        sa.Column('storage_quota_bytes', sa.BigInteger(), nullable=False, default=52428800),
        sa.Column('settings', postgresql.JSON(astext_type=sa.Text()), nullable=False, default={}),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_workspaces'))
    )
    
    # Create indexes for workspaces
    op.create_index(op.f('ix_workspaces_id'), 'workspaces', ['id'], unique=False)
    op.create_index(op.f('ix_workspaces_name'), 'workspaces', ['name'], unique=False)
    op.create_index(op.f('ix_workspaces_owner_id'), 'workspaces', ['owner_id'], unique=False)
    op.create_index(op.f('ix_workspaces_is_orphan'), 'workspaces', ['is_orphan'], unique=False)
    op.create_index(op.f('ix_workspaces_expires_at'), 'workspaces', ['expires_at'], unique=False)
    
    # Create workspace_usage table
    op.create_table(
        'workspace_usage',
        sa.Column('workspace_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('file_count', sa.Integer(), nullable=False, default=0),
        sa.Column('storage_used_bytes', sa.BigInteger(), nullable=False, default=0),
        sa.Column('query_count', sa.Integer(), nullable=False, default=0),
        sa.Column('last_accessed_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['workspace_id'], ['workspaces.id'], name=op.f('fk_workspace_usage_workspace_id_workspaces'), ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('workspace_id', name=op.f('pk_workspace_usage'))
    )
    
    # Create workspace_audit_logs table
    op.create_table(
        'workspace_audit_logs',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text("uuid_generate_v4()"), nullable=False),
        sa.Column('workspace_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('action', sa.String(length=50), nullable=False),
        sa.Column('resource_type', sa.String(length=50), nullable=False),
        sa.Column('resource_id', sa.String(length=255), nullable=True),
        sa.Column('details', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('user_agent', sa.Text(), nullable=True),
        sa.Column('timestamp', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['workspace_id'], ['workspaces.id'], name=op.f('fk_workspace_audit_logs_workspace_id_workspaces'), ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.uuid_id'], name=op.f('fk_workspace_audit_logs_user_id_users')),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_workspace_audit_logs'))
    )
    
    # Create indexes for audit logs
    op.create_index(op.f('ix_workspace_audit_logs_id'), 'workspace_audit_logs', ['id'], unique=False)
    op.create_index(op.f('ix_workspace_audit_logs_workspace_id'), 'workspace_audit_logs', ['workspace_id'], unique=False)
    op.create_index(op.f('ix_workspace_audit_logs_user_id'), 'workspace_audit_logs', ['user_id'], unique=False)
    op.create_index(op.f('ix_workspace_audit_logs_action'), 'workspace_audit_logs', ['action'], unique=False)
    op.create_index(op.f('ix_workspace_audit_logs_timestamp'), 'workspace_audit_logs', ['timestamp'], unique=False)
    
    # Add foreign key constraint from workspaces to users (using new UUID column)
    op.create_foreign_key(op.f('fk_workspaces_owner_id_users'), 'workspaces', 'users', ['owner_id'], ['uuid_id'])
    
    # Create trigger to update updated_at timestamp
    op.execute("""
        CREATE OR REPLACE FUNCTION update_updated_at_column()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = now();
            RETURN NEW;
        END;
        $$ language 'plpgsql';
    """)
    
    op.execute("""
        CREATE TRIGGER update_workspaces_updated_at
        BEFORE UPDATE ON workspaces
        FOR EACH ROW
        EXECUTE FUNCTION update_updated_at_column();
    """)


def downgrade() -> None:
    """Downgrade database schema."""
    
    # Drop triggers and functions
    op.execute("DROP TRIGGER IF EXISTS update_workspaces_updated_at ON workspaces;")
    op.execute("DROP FUNCTION IF EXISTS update_updated_at_column();")
    
    # Drop indexes for audit logs
    op.drop_index(op.f('ix_workspace_audit_logs_timestamp'), table_name='workspace_audit_logs')
    op.drop_index(op.f('ix_workspace_audit_logs_action'), table_name='workspace_audit_logs')
    op.drop_index(op.f('ix_workspace_audit_logs_user_id'), table_name='workspace_audit_logs')
    op.drop_index(op.f('ix_workspace_audit_logs_workspace_id'), table_name='workspace_audit_logs')
    op.drop_index(op.f('ix_workspace_audit_logs_id'), table_name='workspace_audit_logs')
    
    # Drop tables
    op.drop_table('workspace_audit_logs')
    op.drop_table('workspace_usage')
    
    # Drop indexes for workspaces
    op.drop_index(op.f('ix_workspaces_expires_at'), table_name='workspaces')
    op.drop_index(op.f('ix_workspaces_is_orphan'), table_name='workspaces')
    op.drop_index(op.f('ix_workspaces_owner_id'), table_name='workspaces')
    op.drop_index(op.f('ix_workspaces_name'), table_name='workspaces')
    op.drop_index(op.f('ix_workspaces_id'), table_name='workspaces')
    
    op.drop_table('workspaces')
    
    # Remove UUID column from users
    op.drop_index('ix_users_uuid_id', table_name='users')
    op.drop_column('users', 'uuid_id')