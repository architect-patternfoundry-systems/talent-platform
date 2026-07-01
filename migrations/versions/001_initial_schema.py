"""Initial schema

Revision ID: 001
Revises: 
Create Date: 2026-07-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Create role_definitions table
    op.create_table(
        'role_definitions',
        sa.Column('role_id', sa.String(), nullable=False),
        sa.Column('schema_version', sa.String(), nullable=False, server_default='1.0'),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.String(), nullable=False),
        sa.Column('skills', postgresql.JSON(), nullable=False),
        sa.Column('scope', postgresql.JSON(), nullable=False),
        sa.Column('success_criteria', postgresql.JSON(), nullable=False),
        sa.Column('platform_requirements', postgresql.JSON(), nullable=False),
        sa.Column('human_exception', sa.String(), nullable=False),
        sa.Column('confidence', sa.String(), nullable=False),
        sa.Column('evidence_quality', sa.String(), nullable=False),
        sa.Column('evidence_sources', postgresql.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('role_id')
    )
    
    # Create personal_profiles table
    op.create_table(
        'personal_profiles',
        sa.Column('profile_id', sa.String(), nullable=False),
        sa.Column('schema_version', sa.String(), nullable=False, server_default='1.0'),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('skills', postgresql.JSON(), nullable=False),
        sa.Column('aspirations', postgresql.JSON(), nullable=False),
        sa.Column('experience', postgresql.JSON(), nullable=False),
        sa.Column('availability', postgresql.JSON(), nullable=False),
        sa.Column('platform_preferences', postgresql.JSON(), nullable=False),
        sa.Column('human_exception', sa.String(), nullable=False),
        sa.Column('confidence', sa.String(), nullable=False),
        sa.Column('evidence_quality', sa.String(), nullable=False),
        sa.Column('evidence_sources', postgresql.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('profile_id')
    )
    
    # Create match_results table
    op.create_table(
        'match_results',
        sa.Column('match_id', sa.String(), nullable=False),
        sa.Column('schema_version', sa.String(), nullable=False, server_default='1.0'),
        sa.Column('profile_id', sa.String(), nullable=False),
        sa.Column('role_id', sa.String(), nullable=False),
        sa.Column('skill_overlap', sa.Float(), nullable=False),
        sa.Column('aspiration_alignment', sa.Float(), nullable=False),
        sa.Column('availability_match', sa.Float(), nullable=False),
        sa.Column('platform_match', sa.Float(), nullable=False),
        sa.Column('overall_score', sa.Float(), nullable=False),
        sa.Column('human_exception_alignment', sa.Float(), nullable=False),
        sa.Column('human_exception_rationale', sa.String(), nullable=True),
        sa.Column('confidence', sa.String(), nullable=False),
        sa.Column('evidence_quality', sa.String(), nullable=False),
        sa.Column('override_reason', sa.String(), nullable=True),
        sa.Column('override_author', sa.String(), nullable=True),
        sa.Column('override_timestamp', sa.DateTime(timezone=True), nullable=True),
        sa.Column('original_score', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('match_id')
    )
    
    # Create project_definitions table
    op.create_table(
        'project_definitions',
        sa.Column('project_id', sa.String(), nullable=False),
        sa.Column('schema_version', sa.String(), nullable=False, server_default='1.0'),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.String(), nullable=False),
        sa.Column('phases', postgresql.JSON(), nullable=False),
        sa.Column('roles', postgresql.JSON(), nullable=False),
        sa.Column('agents', postgresql.JSON(), nullable=False),
        sa.Column('platforms', postgresql.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('project_id')
    )
    
    # Create agent_definitions table
    op.create_table(
        'agent_definitions',
        sa.Column('agent_id', sa.String(), nullable=False),
        sa.Column('schema_version', sa.String(), nullable=False, server_default='1.0'),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('agent_type', sa.String(), nullable=False),
        sa.Column('skills', postgresql.JSON(), nullable=False),
        sa.Column('scope', postgresql.JSON(), nullable=False),
        sa.Column('boundaries', postgresql.JSON(), nullable=False),
        sa.Column('platform', sa.String(), nullable=False),
        sa.Column('platform_config', postgresql.JSON(), nullable=False),
        sa.Column('personality', postgresql.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('agent_id')
    )
    
    # Create override_logs table
    op.create_table(
        'override_logs',
        sa.Column('override_id', sa.String(), nullable=False),
        sa.Column('schema_version', sa.String(), nullable=False, server_default='1.0'),
        sa.Column('entity_type', sa.String(), nullable=False),
        sa.Column('entity_id', sa.String(), nullable=False),
        sa.Column('override_reason', sa.String(), nullable=False),
        sa.Column('override_author', sa.String(), nullable=False),
        sa.Column('override_timestamp', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('original_value', postgresql.JSON(), nullable=False),
        sa.Column('override_value', postgresql.JSON(), nullable=False),
        sa.Column('impact', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('override_id')
    )
    
    # Create weight_configurations table
    op.create_table(
        'weight_configurations',
        sa.Column('config_id', sa.String(), nullable=False),
        sa.Column('schema_version', sa.String(), nullable=False, server_default='1.0'),
        sa.Column('scope', sa.String(), nullable=False),
        sa.Column('scope_id', sa.String(), nullable=True),
        sa.Column('skill_overlap_weight', sa.Float(), nullable=False),
        sa.Column('aspiration_alignment_weight', sa.Float(), nullable=False),
        sa.Column('availability_match_weight', sa.Float(), nullable=False),
        sa.Column('platform_match_weight', sa.Float(), nullable=False),
        sa.Column('approved_by', sa.String(), nullable=False),
        sa.Column('approved_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('config_id')
    )


def downgrade():
    op.drop_table('weight_configurations')
    op.drop_table('override_logs')
    op.drop_table('agent_definitions')
    op.drop_table('project_definitions')
    op.drop_table('match_results')
    op.drop_table('personal_profiles')
    op.drop_table('role_definitions')
