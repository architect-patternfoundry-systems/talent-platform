"""RLS policies

Revision ID: 002
Revises: 001
Create Date: 2026-07-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = '001'


def upgrade():
    # Enable RLS on all tables
    op.execute("ALTER TABLE role_definitions ENABLE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE personal_profiles ENABLE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE match_results ENABLE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE project_definitions ENABLE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE agent_definitions ENABLE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE override_logs ENABLE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE weight_configurations ENABLE ROW LEVEL SECURITY")
    
    # Create tenant context function
    op.execute("""
        CREATE OR REPLACE FUNCTION get_current_tenant_id()
        RETURNS TEXT AS $$
        BEGIN
            RETURN current_setting('app.current_tenant_id', true);
        EXCEPTION WHEN OTHERS THEN
            RETURN NULL;
        END;
        $$ LANGUAGE plpgsql SECURITY DEFINER;
    """)
    
    # Create RLS policies for role_definitions
    op.execute("""
        CREATE POLICY role_definitions_tenant_isolation ON role_definitions
        FOR ALL
        USING (tenant_id = get_current_tenant_id())
        WITH CHECK (tenant_id = get_current_tenant_id());
    """)
    
    # Create RLS policies for personal_profiles
    op.execute("""
        CREATE POLICY personal_profiles_tenant_isolation ON personal_profiles
        FOR ALL
        USING (tenant_id = get_current_tenant_id())
        WITH CHECK (tenant_id = get_current_tenant_id());
    """)
    
    # Create RLS policies for match_results
    op.execute("""
        CREATE POLICY match_results_tenant_isolation ON match_results
        FOR ALL
        USING (tenant_id = get_current_tenant_id())
        WITH CHECK (tenant_id = get_current_tenant_id());
    """)
    
    # Create RLS policies for project_definitions
    op.execute("""
        CREATE POLICY project_definitions_tenant_isolation ON project_definitions
        FOR ALL
        USING (tenant_id = get_current_tenant_id())
        WITH CHECK (tenant_id = get_current_tenant_id());
    """)
    
    # Create RLS policies for agent_definitions
    op.execute("""
        CREATE POLICY agent_definitions_tenant_isolation ON agent_definitions
        FOR ALL
        USING (tenant_id = get_current_tenant_id())
        WITH CHECK (tenant_id = get_current_tenant_id());
    """)
    
    # Create RLS policies for override_logs
    op.execute("""
        CREATE POLICY override_logs_tenant_isolation ON override_logs
        FOR ALL
        USING (tenant_id = get_current_tenant_id())
        WITH CHECK (tenant_id = get_current_tenant_id());
    """)
    
    # Create RLS policies for weight_configurations
    op.execute("""
        CREATE POLICY weight_configurations_tenant_isolation ON weight_configurations
        FOR ALL
        USING (tenant_id = get_current_tenant_id())
        WITH CHECK (tenant_id = get_current_tenant_id());
    """)


def downgrade():
    # Drop RLS policies
    op.execute("DROP POLICY IF EXISTS role_definitions_tenant_isolation ON role_definitions")
    op.execute("DROP POLICY IF EXISTS personal_profiles_tenant_isolation ON personal_profiles")
    op.execute("DROP POLICY IF EXISTS match_results_tenant_isolation ON match_results")
    op.execute("DROP POLICY IF EXISTS project_definitions_tenant_isolation ON project_definitions")
    op.execute("DROP POLICY IF EXISTS agent_definitions_tenant_isolation ON agent_definitions")
    op.execute("DROP POLICY IF EXISTS override_logs_tenant_isolation ON override_logs")
    op.execute("DROP POLICY IF EXISTS weight_configurations_tenant_isolation ON weight_configurations")
    
    # Disable RLS on all tables
    op.execute("ALTER TABLE role_definitions DISABLE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE personal_profiles DISABLE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE match_results DISABLE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE project_definitions DISABLE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE agent_definitions DISABLE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE override_logs DISABLE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE weight_configurations DISABLE ROW LEVEL SECURITY")
    
    # Drop tenant context function
    op.execute("DROP FUNCTION IF EXISTS get_current_tenant_id()")
