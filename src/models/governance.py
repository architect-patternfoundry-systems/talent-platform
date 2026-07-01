"""Governance models"""
from sqlalchemy import Column, String, DateTime, Boolean, Integer, Float, JSON, Text, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from src.core.database import Base


class GovernanceConfig(Base):
    """Governance Configuration model"""
    
    __tablename__ = "governance_config"
    
    # Primary key
    config_id = Column(String, primary_key=True)
    
    # Tenant context
    tenant_id = Column(String, nullable=False)
    
    # Schema version
    schema_version = Column(String, nullable=False, default="1.0")
    
    # NVEDO Configuration
    nvedo_user_id = Column(String, nullable=True)
    nvedo_mandate_document_id = Column(String, nullable=True)
    nvedo_mandate_status = Column(String, nullable=False, default="draft")  # draft, active, expired
    nvedo_term_start = Column(DateTime(timezone=True), nullable=True)
    nvedo_term_end = Column(DateTime(timezone=True), nullable=True)
    
    # RACI Board Configuration
    raci_board_version = Column(String, nullable=False, default="1.0")
    raci_board_document_id = Column(String, nullable=True)
    raci_board_status = Column(String, nullable=False, default="draft")  # draft, active
    
    # Pilot Configuration
    pilot_configuration_id = Column(String, nullable=True)
    pilot_status = Column(String, nullable=False, default="not_started")  # not_started, active, paused, completed
    
    # Feature Flags
    governance_enabled = Column(Boolean, nullable=False, default=False)
    pilot_enabled = Column(Boolean, nullable=False, default=False)
    escalation_enabled = Column(Boolean, nullable=False, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)


class PilotConfiguration(Base):
    """Pilot Configuration model"""
    
    __tablename__ = "pilot_configuration"
    
    # Primary key
    pilot_id = Column(String, primary_key=True)
    
    # Tenant context
    tenant_id = Column(String, nullable=False)
    
    # Schema version
    schema_version = Column(String, nullable=False, default="1.0")
    
    # Pilot Details
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    start_date = Column(DateTime(timezone=True), nullable=False)
    end_date = Column(DateTime(timezone=True), nullable=False)
    duration_weeks = Column(Integer, nullable=False)
    
    # Pilot Scope
    scope = Column(JSON, nullable=False)  # departments, functions, roles
    participants = Column(JSON, nullable=False)  # NVEDO, Data Governance Team, HR Business Partner, Hiring Managers
    
    # Success Criteria
    success_criteria = Column(JSON, nullable=False)
    
    # Pilot Status
    current_week = Column(Integer, nullable=False, default=0)
    status = Column(String, nullable=False, default="setup")  # setup, active, paused, completed
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    metrics = relationship("PilotMetrics", back_populates="pilot", cascade="all, delete-orphan")
    escalations = relationship("Escalation", back_populates="pilot", cascade="all, delete-orphan")


class PilotMetrics(Base):
    """Pilot Metrics model"""
    
    __tablename__ = "pilot_metrics"
    
    # Primary key
    metrics_id = Column(String, primary_key=True)
    
    # Tenant context
    tenant_id = Column(String, nullable=False)
    
    # Pilot reference
    pilot_id = Column(String, ForeignKey("pilot_configuration.pilot_id", ondelete="CASCADE"), nullable=False)
    
    # Schema version
    schema_version = Column(String, nullable=False, default="1.0")
    
    # Week Information
    week = Column(Integer, nullable=False)
    metrics_date = Column(DateTime(timezone=True), nullable=False)
    
    # Quantitative Metrics
    jobs_created = Column(Integer, nullable=False, default=0)
    jobs_submitted = Column(Integer, nullable=False, default=0)
    jobs_approved = Column(Integer, nullable=False, default=0)
    jobs_rejected = Column(Integer, nullable=False, default=0)
    jobs_in_revision = Column(Integer, nullable=False, default=0)
    
    # Time Metrics (in hours)
    avg_approval_time_hours = Column(Float, nullable=True)
    avg_validation_time_hours = Column(Float, nullable=True)
    avg_compensation_review_time_hours = Column(Float, nullable=True)
    nvedo_avg_time_per_job_hours = Column(Float, nullable=True)
    
    # Quality Metrics
    human_exception_quality_score = Column(Float, nullable=True)  # 0-100
    rejection_rate = Column(Float, nullable=True)  # 0-1
    revision_rate = Column(Float, nullable=True)  # 0-1
    generic_filler_rate = Column(Float, nullable=True)  # 0-1
    
    # Participant Satisfaction (0-100)
    hiring_manager_satisfaction = Column(Float, nullable=True)
    nvedo_satisfaction = Column(Float, nullable=True)
    data_governance_satisfaction = Column(Float, nullable=True)
    hr_bp_satisfaction = Column(Float, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    pilot = relationship("PilotConfiguration", back_populates="metrics")


class Escalation(Base):
    """Escalation model"""
    
    __tablename__ = "escalation"
    
    # Primary key
    escalation_id = Column(String, primary_key=True)
    
    # Tenant context
    tenant_id = Column(String, nullable=False)
    
    # Schema version
    schema_version = Column(String, nullable=False, default="1.0")
    
    # Context
    job_id = Column(String, nullable=True)
    pilot_id = Column(String, ForeignKey("pilot_configuration.pilot_id", ondelete="SET NULL"), nullable=True)
    
    # Escalation Details
    from_role = Column(String, nullable=False)  # data_governance_team, hr_business_partner, nvedo
    to_role = Column(String, nullable=False)  # nvedo, c_suite, steering_committee
    reason = Column(String, nullable=False)  # policy_conflict, low_quality, human_exception_disagreement, other
    reason_description = Column(Text, nullable=True)
    
    # Escalation Status
    status = Column(String, nullable=False, default="pending")  # pending, resolved, escalated_further
    resolution = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    pilot = relationship("PilotConfiguration", back_populates="escalations")


class GovernanceAuditLog(Base):
    """Governance Audit Log model"""
    
    __tablename__ = "governance_audit_log"
    
    # Primary key
    audit_id = Column(String, primary_key=True)
    
    # Tenant context
    tenant_id = Column(String, nullable=False)
    
    # Schema version
    schema_version = Column(String, nullable=False, default="1.0")
    
    # Action Details
    action_type = Column(String, nullable=False)  # nvedo_approve, nvedo_reject, raci_board_update, mandate_change, pilot_start, pilot_stop, pilot_extend
    actor_id = Column(String, nullable=False)
    actor_role = Column(String, nullable=False)
    
    # Target Details
    target_type = Column(String, nullable=False)  # job_description, governance_config, pilot_configuration, escalation
    target_id = Column(String, nullable=True)
    
    # Action Details
    action_data = Column(JSON, nullable=True)
    reason = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class JobDescriptionGovernance(Base):
    """Job Description Governance Status model"""
    
    __tablename__ = "job_description_governance"
    
    # Primary key
    governance_id = Column(String, primary_key=True)
    
    # Tenant context
    tenant_id = Column(String, nullable=False)
    
    # Schema version
    schema_version = Column(String, nullable=False, default="1.0")
    
    # Job Reference
    job_id = Column(String, ForeignKey("role_definitions.role_id", ondelete="CASCADE"), nullable=False)
    
    # Governance Status
    status = Column(String, nullable=False, default="draft")  # draft, pending_validation, pending_compensation_review, pending_approval, approved, rejected, provisional_approval
    current_stage = Column(String, nullable=False, default="draft")
    
    # Validation Results
    validation_status = Column(String, nullable=True)  # pending, passed, failed
    validation_feedback = Column(Text, nullable=True)
    validation_actor_id = Column(String, nullable=True)
    validation_timestamp = Column(DateTime(timezone=True), nullable=True)
    
    # Compensation Review Results
    compensation_status = Column(String, nullable=True)  # pending, passed, failed
    compensation_feedback = Column(Text, nullable=True)
    compensation_actor_id = Column(String, nullable=True)
    compensation_timestamp = Column(DateTime(timezone=True), nullable=True)
    
    # NVEDO Approval Results
    nvedo_status = Column(String, nullable=True)  # pending, approved, rejected
    nvedo_feedback = Column(Text, nullable=True)
    nvedo_actor_id = Column(String, nullable=True)
    nvedo_timestamp = Column(DateTime(timezone=True), nullable=True)
    
    # Provisional Approval Details (if status = provisional_approval)
    conditions = Column(JSON, nullable=True)
    conditions_expiry = Column(DateTime(timezone=True), nullable=True)
    
    # Rejection Details (if status = rejected)
    rejection_reason = Column(Text, nullable=True)
    rejection_category = Column(String, nullable=True)
    
    # Metrics
    total_revision_cycles = Column(Integer, nullable=False, default=0)
    total_validation_time_hours = Column(Float, nullable=True)
    total_compensation_review_time_hours = Column(Float, nullable=True)
    total_nvedo_review_time_hours = Column(Float, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
