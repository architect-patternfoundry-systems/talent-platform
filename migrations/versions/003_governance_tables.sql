-- Migration 003: Governance Tables
-- This migration adds tables for governance configuration, pilot management,
-- escalation tracking, and audit logging to support self-service governance setup.

-- Governance Configuration Table
CREATE TABLE governance_config (
    config_id VARCHAR(255) PRIMARY KEY,
    tenant_id VARCHAR(255) NOT NULL,
    schema_version VARCHAR(50) NOT NULL DEFAULT '1.0',
    
    -- NVEDO Configuration
    nvedo_user_id VARCHAR(255),
    nvedo_mandate_document_id VARCHAR(255),
    nvedo_mandate_status VARCHAR(50) NOT NULL DEFAULT 'draft', -- draft, active, expired
    nvedo_term_start TIMESTAMP WITH TIME ZONE,
    nvedo_term_end TIMESTAMP WITH TIME ZONE,
    
    -- RACI Board Configuration
    raci_board_version VARCHAR(50) NOT NULL DEFAULT '1.0',
    raci_board_document_id VARCHAR(255),
    raci_board_status VARCHAR(50) NOT NULL DEFAULT 'draft', -- draft, active
    
    -- Pilot Configuration
    pilot_configuration_id VARCHAR(255),
    pilot_status VARCHAR(50) NOT NULL DEFAULT 'not_started', -- not_started, active, paused, completed
    
    -- Feature Flags
    governance_enabled BOOLEAN NOT NULL DEFAULT false,
    pilot_enabled BOOLEAN NOT NULL DEFAULT false,
    escalation_enabled BOOLEAN NOT NULL DEFAULT false,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Pilot Configuration Table
CREATE TABLE pilot_configuration (
    pilot_id VARCHAR(255) PRIMARY KEY,
    tenant_id VARCHAR(255) NOT NULL,
    schema_version VARCHAR(50) NOT NULL DEFAULT '1.0',
    
    -- Pilot Details
    name VARCHAR(255) NOT NULL,
    description TEXT,
    start_date TIMESTAMP WITH TIME ZONE NOT NULL,
    end_date TIMESTAMP WITH TIME ZONE NOT NULL,
    duration_weeks INTEGER NOT NULL,
    
    -- Pilot Scope
    scope JSONB NOT NULL, -- departments, functions, roles
    participants JSONB NOT NULL, -- NVEDO, Data Governance Team, HR Business Partner, Hiring Managers
    
    -- Success Criteria
    success_criteria JSONB NOT NULL,
    
    -- Pilot Status
    current_week INTEGER NOT NULL DEFAULT 0,
    status VARCHAR(50) NOT NULL DEFAULT 'setup', -- setup, active, paused, completed
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Pilot Metrics Table
CREATE TABLE pilot_metrics (
    metrics_id VARCHAR(255) PRIMARY KEY,
    tenant_id VARCHAR(255) NOT NULL,
    pilot_id VARCHAR(255) NOT NULL,
    schema_version VARCHAR(50) NOT NULL DEFAULT '1.0',
    
    -- Week Information
    week INTEGER NOT NULL,
    metrics_date TIMESTAMP WITH TIME ZONE NOT NULL,
    
    -- Quantitative Metrics
    jobs_created INTEGER NOT NULL DEFAULT 0,
    jobs_submitted INTEGER NOT NULL DEFAULT 0,
    jobs_approved INTEGER NOT NULL DEFAULT 0,
    jobs_rejected INTEGER NOT NULL DEFAULT 0,
    jobs_in_revision INTEGER NOT NULL DEFAULT 0,
    
    -- Time Metrics (in hours)
    avg_approval_time_hours FLOAT,
    avg_validation_time_hours FLOAT,
    avg_compensation_review_time_hours FLOAT,
    nvedo_avg_time_per_job_hours FLOAT,
    
    -- Quality Metrics
    human_exception_quality_score FLOAT, -- 0-100
    rejection_rate FLOAT, -- 0-1
    revision_rate FLOAT, -- 0-1
    generic_filler_rate FLOAT, -- 0-1
    
    -- Participant Satisfaction (0-100)
    hiring_manager_satisfaction FLOAT,
    nvedo_satisfaction FLOAT,
    data_governance_satisfaction FLOAT,
    hr_bp_satisfaction FLOAT,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    
    -- Foreign Key
    FOREIGN KEY (pilot_id) REFERENCES pilot_configuration(pilot_id) ON DELETE CASCADE
);

-- Escalation Table
CREATE TABLE escalation (
    escalation_id VARCHAR(255) PRIMARY KEY,
    tenant_id VARCHAR(255) NOT NULL,
    schema_version VARCHAR(50) NOT NULL DEFAULT '1.0',
    
    -- Context
    job_id VARCHAR(255),
    pilot_id VARCHAR(255),
    
    -- Escalation Details
    from_role VARCHAR(50) NOT NULL, -- data_governance_team, hr_business_partner, nvedo
    to_role VARCHAR(50) NOT NULL, -- nvedo, c_suite, steering_committee
    reason VARCHAR(50) NOT NULL, -- policy_conflict, low_quality, human_exception_disagreement, other
    reason_description TEXT,
    
    -- Escalation Status
    status VARCHAR(50) NOT NULL DEFAULT 'pending', -- pending, resolved, escalated_further
    resolution TEXT,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    resolved_at TIMESTAMP WITH TIME ZONE,
    
    -- Foreign Keys
    FOREIGN KEY (pilot_id) REFERENCES pilot_configuration(pilot_id) ON DELETE SET NULL
);

-- Audit Log Table
CREATE TABLE governance_audit_log (
    audit_id VARCHAR(255) PRIMARY KEY,
    tenant_id VARCHAR(255) NOT NULL,
    schema_version VARCHAR(50) NOT NULL DEFAULT '1.0',
    
    -- Action Details
    action_type VARCHAR(100) NOT NULL, -- nvedo_approve, nvedo_reject, raci_board_update, mandate_change, pilot_start, pilot_stop, pilot_extend
    actor_id VARCHAR(255) NOT NULL,
    actor_role VARCHAR(50) NOT NULL,
    
    -- Target Details
    target_type VARCHAR(50) NOT NULL, -- job_description, governance_config, pilot_configuration, escalation
    target_id VARCHAR(255),
    
    -- Action Details
    action_data JSONB,
    reason TEXT,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Job Description Governance Status Table
CREATE TABLE job_description_governance (
    governance_id VARCHAR(255) PRIMARY KEY,
    tenant_id VARCHAR(255) NOT NULL,
    schema_version VARCHAR(50) NOT NULL DEFAULT '1.0',
    
    -- Job Reference
    job_id VARCHAR(255) NOT NULL, -- Reference to role_id in role_definitions table
    
    -- Governance Status
    status VARCHAR(50) NOT NULL DEFAULT 'draft', -- draft, pending_validation, pending_compensation_review, pending_approval, approved, rejected, provisional_approval
    current_stage VARCHAR(50) NOT NULL DEFAULT 'draft',
    
    -- Validation Results
    validation_status VARCHAR(50), -- pending, passed, failed
    validation_feedback TEXT,
    validation_actor_id VARCHAR(255),
    validation_timestamp TIMESTAMP WITH TIME ZONE,
    
    -- Compensation Review Results
    compensation_status VARCHAR(50), -- pending, passed, failed
    compensation_feedback TEXT,
    compensation_actor_id VARCHAR(255),
    compensation_timestamp TIMESTAMP WITH TIME ZONE,
    
    -- NVEDO Approval Results
    nvedo_status VARCHAR(50), -- pending, approved, rejected
    nvedo_feedback TEXT,
    nvedo_actor_id VARCHAR(255),
    nvedo_timestamp TIMESTAMP WITH TIME ZONE,
    
    -- Provisional Approval Details (if status = provisional_approval)
    conditions JSONB,
    conditions_expiry TIMESTAMP WITH TIME ZONE,
    
    -- Rejection Details (if status = rejected)
    rejection_reason TEXT,
    rejection_category VARCHAR(50),
    
    -- Metrics
    total_revision_cycles INTEGER NOT NULL DEFAULT 0,
    total_validation_time_hours FLOAT,
    total_compensation_review_time_hours FLOAT,
    total_nvedo_review_time_hours FLOAT,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    
    -- Foreign Key
    FOREIGN KEY (job_id) REFERENCES role_definitions(role_id) ON DELETE CASCADE
);

-- Create Indexes
CREATE INDEX idx_governance_config_tenant_id ON governance_config(tenant_id);
CREATE INDEX idx_governance_config_nvedo_user_id ON governance_config(nvedo_user_id);
CREATE INDEX idx_pilot_configuration_tenant_id ON pilot_configuration(tenant_id);
CREATE INDEX idx_pilot_configuration_status ON pilot_configuration(status);
CREATE INDEX idx_pilot_metrics_pilot_id ON pilot_metrics(pilot_id);
CREATE INDEX idx_pilot_metrics_week ON pilot_metrics(week);
CREATE INDEX idx_escalation_tenant_id ON escalation(tenant_id);
CREATE INDEX idx_escalation_status ON escalation(status);
CREATE INDEX idx_escalation_pilot_id ON escalation(pilot_id);
CREATE INDEX idx_governance_audit_log_tenant_id ON governance_audit_log(tenant_id);
CREATE INDEX idx_governance_audit_log_action_type ON governance_audit_log(action_type);
CREATE INDEX idx_governance_audit_log_created_at ON governance_audit_log(created_at);
CREATE INDEX idx_job_description_governance_tenant_id ON job_description_governance(tenant_id);
CREATE INDEX idx_job_description_governance_job_id ON job_description_governance(job_id);
CREATE INDEX idx_job_description_governance_status ON job_description_governance(status);

-- Enable RLS on all tables
ALTER TABLE governance_config ENABLE ROW LEVEL SECURITY;
ALTER TABLE pilot_configuration ENABLE ROW LEVEL SECURITY;
ALTER TABLE pilot_metrics ENABLE ROW LEVEL SECURITY;
ALTER TABLE escalation ENABLE ROW LEVEL SECURITY;
ALTER TABLE governance_audit_log ENABLE ROW LEVEL SECURITY;
ALTER TABLE job_description_governance ENABLE ROW LEVEL SECURITY;

-- Create RLS policies
CREATE POLICY governance_config_tenant_isolation ON governance_config
FOR ALL
USING (tenant_id = get_current_tenant_id())
WITH CHECK (tenant_id = get_current_tenant_id());

CREATE POLICY pilot_configuration_tenant_isolation ON pilot_configuration
FOR ALL
USING (tenant_id = get_current_tenant_id())
WITH CHECK (tenant_id = get_current_tenant_id());

CREATE POLICY pilot_metrics_tenant_isolation ON pilot_metrics
FOR ALL
USING (tenant_id = get_current_tenant_id())
WITH CHECK (tenant_id = get_current_tenant_id());

CREATE POLICY escalation_tenant_isolation ON escalation
FOR ALL
USING (tenant_id = get_current_tenant_id())
WITH CHECK (tenant_id = get_current_tenant_id());

CREATE POLICY governance_audit_log_tenant_isolation ON governance_audit_log
FOR ALL
USING (tenant_id = get_current_tenant_id())
WITH CHECK (tenant_id = get_current_tenant_id());

CREATE POLICY job_description_governance_tenant_isolation ON job_description_governance
FOR ALL
USING (tenant_id = get_current_tenant_id())
WITH CHECK (tenant_id = get_current_tenant_id());
