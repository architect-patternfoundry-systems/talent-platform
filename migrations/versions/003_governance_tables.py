"""Governance tables

Revision ID: 003
Revises: 002
Create Date: 2026-07-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '003'
down_revision = '002'
branch_labels = None
depends_on = '002'


def upgrade():
    # Create governance_config table
    op.create_table(
        'governance_config',
        sa.Column('config_id', sa.String(), nullable=False),
        sa.Column('tenant_id', sa.String(), nullable=False),
        sa.Column('schema_version', sa.String(), nullable=False, server_default='1.0'),
        sa.Column('nvedo_user_id', sa.String(), nullable=True),
        sa.Column('nvedo_mandate_document_id', sa.String(), nullable=True),
        sa.Column('nvedo_mandate_status', sa.String(), nullable=False, server_default='draft'),
        sa.Column('nvedo_term_start', sa.DateTime(timezone=True), nullable=True),
        sa.Column('nvedo_term_end', sa.DateTime(timezone=True), nullable=True),
        sa.Column('raci_board_version', sa.String(), nullable=False, server_default='1.0'),
        sa.Column('raci_board_document_id', sa.String(), nullable=True),
        sa.Column('raci_board_status', sa.String(), nullable=False, server_default='draft'),
        sa.Column('pilot_configuration_id', sa.String(), nullable=True),
        sa.Column('pilot_status', sa.String(), nullable=False, server_default='not_started'),
        sa.Column('governance_enabled', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('pilot_enabled', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('escalation_enabled', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('config_id')
    )
    
    # Create pilot_configuration table
    op.create_table(
        'pilot_configuration',
        sa.Column('pilot_id', sa.String(), nullable=False),
        sa.Column('tenant_id', sa.String(), nullable=False),
        sa.Column('schema_version', sa.String(), nullable=False, server_default='1.0'),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('start_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('end_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('duration_weeks', sa.Integer(), nullable=False),
        sa.Column('scope', postgresql.JSON(), nullable=False),
        sa.Column('participants', postgresql.JSON(), nullable=False),
        sa.Column('success_criteria', postgresql.JSON(), nullable=False),
        sa.Column('current_week', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('status', sa.String(), nullable=False, server_default='setup'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('pilot_id')
    )
    
    # Create pilot_metrics table
    op.create_table(
        'pilot_metrics',
        sa.Column('metrics_id', sa.String(), nullable=False),
        sa.Column('tenant_id', sa.String(), nullable=False),
        sa.Column('pilot_id', sa.String(), nullable=False),
        sa.Column('schema_version', sa.String(), nullable=False, server_default='1.0'),
        sa.Column('week', sa.Integer(), nullable=False),
        sa.Column('metrics_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('jobs_created', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('jobs_submitted', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('jobs_approved', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('jobs_rejected', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('jobs_in_revision', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('avg_approval_time_hours', sa.Float(), nullable=True),
        sa.Column('avg_validation_time_hours', sa.Float(), nullable=True),
        sa.Column('avg_compensation_review_time_hours', sa.Float(), nullable=True),
        sa.Column('nvedo_avg_time_per_job_hours', sa.Float(), nullable=True),
        sa.Column('human_exception_quality_score', sa.Float(), nullable=True),
        sa.Column('rejection_rate', sa.Float(), nullable=True),
        sa.Column('revision_rate', sa.Float(), nullable=True),
        sa.Column('generic_filler_rate', sa.Float(), nullable=True),
        sa.Column('hiring_manager_satisfaction', sa.Float(), nullable=True),
        sa.Column('nvedo_satisfaction', sa.Float(), nullable=True),
        sa.Column('data_governance_satisfaction', sa.Float(), nullable=True),
        sa.Column('hr_bp_satisfaction', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['pilot_id'], ['pilot_configuration'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('metrics_id')
    )
    
    # Create escalation table
    op.create_table(
        'escalation',
        sa.Column('escalation_id', sa.String(), nullable=False),
        sa.Column('tenant_id', sa.String(), nullable=False),
        sa.Column('schema_version', sa.String(), nullable=False, server_default='1.0'),
        sa.Column('job_id', sa.String(), nullable=True),
        sa.Column('pilot_id', sa.String(), nullable=True),
        sa.Column('from_role', sa.String(), nullable=False),
        sa.Column('to_role', sa.String(), nullable=False),
        sa.Column('reason', sa.String(), nullable=False),
        sa.Column('reason_description', sa.Text(), nullable=True),
        sa.Column('status', sa.String(), nullable=False, server_default='pending'),
        sa.Column('resolution', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('resolved_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['pilot_id'], ['pilot_configuration'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('escalation_id')
    )
    
    # Create governance_audit_log table
    op.create_table(
        'governance_audit_log',
        sa.Column('audit_id', sa.String(), nullable=False),
        sa.Column('tenant_id', sa.String(), nullable=False),
        sa.Column('schema_version', sa.String(), nullable=False, server_default='1.0'),
        sa.Column('action_type', sa.String(), nullable=False),
        sa.Column('actor_id', sa.String(), nullable=False),
        sa.Column('actor_role', sa.String(), nullable=False),
        sa.Column('target_type', sa.String(), nullable=False),
        sa.Column('target_id', sa.String(), nullable=True),
        sa.Column('action_data', postgresql.JSON(), nullable=True),
        sa.Column('reason', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('audit_id')
    )
    
    # Create job_description_governance table
    op.create_table(
        'job_description_governance',
        sa.Column('governance_id', sa.String(), nullable=False),
        sa.Column('tenant_id', sa.String(), nullable=False),
        sa.Column('schema_version', sa.String(), nullable=False, server_default='1.0'),
        sa.Column('job_id', sa.String(), nullable=False),
        sa.Column('status', sa.String(), nullable=False, server_default='draft'),
        sa.Column('current_stage', sa.String(), nullable=False, server_default='draft'),
        sa.Column('validation_status', sa.String(), nullable=True),
        sa.Column('validation_feedback', sa.Text(), nullable=True),
        sa.Column('validation_actor_id', sa.String(), nullable=True),
        sa.Column('validation_timestamp', sa.DateTime(timezone=True), nullable=True),
        sa.Column('compensation_status', sa.String(), nullable=True),
        sa.Column('compensation_feedback', sa.Text(), nullable=True),
        sa.Column('compensation_actor_id', sa.String(), nullable=True),
        sa.Column('compensation_timestamp', sa.DateTime(timezone=True), nullable=True),
        sa.Column('nvedo_status', sa.String(), nullable=True),
        sa.Column('nvedo_feedback', sa.Text(), nullable=True),
        sa.Column('nvedo_actor_id', sa.String(), nullable=True),
        sa.Column('nvedo_timestamp', sa.DateTime(timezone=True), nullable=True),
        sa.Column('conditions', postgresql.JSON(), nullable=True),
        sa.Column('conditions_expiry', sa.DateTime(timezone=True), nullable=True),
        sa.Column('rejection_reason', sa.Text(), nullable=True),
        sa.Column('rejection_category', sa.String(), nullable=True),
        sa.Column('total_revision_cycles', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('total_validation_time_hours', sa.Float(), nullable=True),
        sa.Column('total_compensation_review_time_hours', sa.Float(), nullable=True),
        sa.Column('total_nvedo_review_time_hours', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['job_id'], ['role_definitions'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('governance_id')
    )
    
    # Create indexes
    op.create_index('governance_config', ['tenant_id'], name='idx_governance_config_tenant_id')
    op.create_index('governance_config', ['nvedo_user_id'], name='idx_governance_config_nvedo_user_id')
    op.create_index('pilot_configuration', ['tenant_id'], name='idx_pilot_configuration_tenant_id')
    op.create_index('pilot_configuration', ['status'], name='idx_pilot_configuration_status')
    op.create_index('pilot_metrics', ['pilot_id'], name='idx_pilot_metrics_pilot_id')
    op.create_index('pilot_metrics', ['week'], name='idx_pilot_metrics_week')
    op.create_index('escalation', ['tenant_id'], name='idx_escalation_tenant_id')
    op.create_index('escalation', ['status'], name='idx_escalation_status')
    op.create_index('escalation', ['pilot_id'], name='idx_escalation_pilot_id')
    op.create_index('governance_audit_log', ['tenant_id'], name='idx_governance_audit_log_tenant_id')
    op.create_index('governance_audit_log', ['action_type'], name='idx_governance_audit_log_action_type')
    op.create_index('governance_audit_log', ['created_at'], name='idx_governance_audit_log_created_at')
    op.create_index('job_description_governance', ['tenant_id'], name='idx_job_description_governance_tenant_id')
    op.create_index('job_description_governance', ['job_id'], name='idx_job_description_governance_job_id')
    op.create_index('job_description_governance', ['status'], name='idx_job_description_governance_status')
    
    # Enable RLS on all tables
    op.execute("ALTER TABLE governance_config ENABLE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE pilot_configuration ENABLE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE pilot_metrics ENABLE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE escalation ENABLE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE governance_audit_log ENABLE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE job_description_governance ENABLE ROW LEVEL SECURITY")
    
    # Create RLS policies
    op.execute("""
        CREATE POLICY governance_config_tenant_isolation ON governance_config
        FOR ALL
        USING (tenant_id = get_current_tenant_id())
        WITH CHECK (tenant_id = get_current_tenant_id())
    """)
    
    op.execute("""
        CREATE POLICY pilot_configuration_tenant_isolation ON pilot_configuration
        FOR ALL
        USING (tenant_id = get_current_tenant_id())
        WITH CHECK (tenant_id = get_current_tenant_id())
    """)
    
    op.execute("""
        CREATE POLICY pilot_metrics_tenant_isolation ON pilot_metrics
        FOR ALL
        USING (tenant_id = get_current_tenant_id())
        WITH CHECK (tenant_id = get_current_tenant_id())
    """)
    
    op.execute("""
        CREATE POLICY escalation_tenant_isolation ON escalation
        FOR ALL
        USING (tenant_id = get_current_tenant_id())
        WITH CHECK (tenant_id = get_current_tenant_id())
    """)
    
    op.execute("""
        CREATE POLICY governance_audit_log_tenant_isolation ON governance_audit_log
        FOR ALL
        USING (tenant_id = get_current_tenant_id())
        WITH CHECK (tenant_id = get_current_tenant_id())
    """)
    
    op.execute("""
        CREATE POLICY job_description_governance_tenant_isolation ON job_description_governance
        FOR ALL
        USING (tenant_id = get_current_tenant_id())
        WITH CHECK (tenant_id = get_current_tenant_id())
    """)


def downgrade():
    # Drop RLS policies
    op.execute("DROP POLICY IF EXISTS job_description_governance_tenant_isolation ON job_description_governance")
    op.execute("DROP POLICY IF EXISTS governance_audit_log_tenant_isolation ON governance_audit_log")
    op.execute("DROP POLICY IF EXISTS escalation_tenant_isolation ON escalation")
    op.execute("DROP POLICY IF EXISTS pilot_metrics_tenant_isolation ON pilot_metrics")
    op.execute("DROP POLICY IF EXISTS pilot_configuration_tenant_isolation ON pilot_configuration")
    op.execute("DROP POLICY IF EXISTS governance_config_tenant_isolation ON governance_config")
    
    # Disable RLS on all tables
    op.execute("ALTER TABLE job_description_governance DISABLE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE governance_audit_log DISABLE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE escalation DISABLE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE pilot_metrics DISABLE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE pilot_configuration DISABLE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE governance_config DISABLE ROW LEVEL SECURITY")
    
    # Drop indexes
    op.drop_index('idx_job_description_governance_status', table_name='job_description_governance')
    op.drop_index('idx_job_description_governance_job_id', table_name='job_description_governance')
    op.drop_index('idx_job_description_governance_tenant_id', table_name='job_description_governance')
    op.drop_index('idx_governance_audit_log_created_at', table_name='governance_audit_log')
    op.drop_index('idx_governance_audit_log_action_type', table_name='governance_audit_log')
    op.drop_index('idx_governance_audit_log_tenant_id', table_name='governance_audit_log')
    op.drop_index('idx_escalation_pilot_id', table_name='escalation')
    op.drop_index('idx_escalation_status', table_name='escalation')
    op.drop_index('idx_escalation_tenant_id', table_name='escalation')
    op.drop_index('idx_pilot_metrics_week', table_name='pilot_metrics')
    op.drop_index('idx_pilot_metrics_pilot_id', table_name='pilot_metrics')
    op.drop_index('idx_pilot_configuration_status', table_name='pilot_configuration')
    op.drop_index('idx_pilot_configuration_tenant_id', table_name='pilot_configuration')
    op.drop_index('idx_governance_config_nvedo_user_id', table_name='governance_config')
    op.drop_index('idx_governance_config_tenant_id', table_name='governance_config')
    
    # Drop tables
    op.drop_table('job_description_governance')
    op.drop_table('governance_audit_log')
    op.drop_table('escalation')
    op.drop_table('pilot_metrics')
    op.drop_table('pilot_configuration')
    op.drop_table('governance_config')
