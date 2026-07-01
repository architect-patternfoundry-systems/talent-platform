"""Governance API endpoints"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime
import uuid

from src.core.database import get_db
from src.core.middleware import get_current_tenant_id
from src.core.tenant import set_tenant_context
from src.models.governance import (
    GovernanceConfig,
    PilotConfiguration,
    PilotMetrics,
    Escalation,
    GovernanceAuditLog,
    JobDescriptionGovernance
)


router = APIRouter(prefix="/v1/governance", tags=["governance"])


# Pydantic models for request/response

class GovernanceConfigCreate(BaseModel):
    nvedo_user_id: str
    nvedo_mandate_status: str = "draft"
    raci_board_status: str = "draft"
    governance_enabled: bool = False
    pilot_enabled: bool = False
    escalation_enabled: bool = False


class GovernanceConfigResponse(BaseModel):
    config_id: str
    tenant_id: str
    schema_version: str
    nvedo_user_id: Optional[str]
    nvedo_mandate_document_id: Optional[str]
    nvedo_mandate_status: str
    nvedo_term_start: Optional[datetime]
    nvedo_term_end: Optional[datetime]
    raci_board_version: str
    raci_board_document_id: Optional[str]
    raci_board_status: str
    pilot_configuration_id: Optional[str]
    pilot_status: str
    governance_enabled: bool
    pilot_enabled: bool
    escalation_enabled: bool
    created_at: datetime
    updated_at: datetime


class PilotConfigurationCreate(BaseModel):
    name: str
    description: Optional[str] = None
    start_date: datetime
    end_date: datetime
    duration_weeks: int
    scope: dict
    participants: dict
    success_criteria: dict


class PilotConfigurationResponse(BaseModel):
    pilot_id: str
    tenant_id: str
    schema_version: str
    name: str
    description: Optional[str]
    start_date: datetime
    end_date: datetime
    duration_weeks: int
    scope: dict
    participants: dict
    success_criteria: dict
    current_week: int
    status: str
    created_at: datetime
    updated_at: datetime


class PilotMetricsCreate(BaseModel):
    pilot_id: str
    week: int
    metrics_date: datetime
    jobs_created: int = 0
    jobs_submitted: int = 0
    jobs_approved: int = 0
    jobs_rejected: int = 0
    jobs_in_revision: int = 0
    avg_approval_time_hours: Optional[float] = None
    avg_validation_time_hours: Optional[float] = None
    avg_compensation_review_time_hours: Optional[float] = None
    nvedo_avg_time_per_job_hours: Optional[float] = None
    human_exception_quality_score: Optional[float] = None
    rejection_rate: Optional[float] = None
    revision_rate: Optional[float] = None
    generic_filler_rate: Optional[float] = None
    hiring_manager_satisfaction: Optional[float] = None
    nvedo_satisfaction: Optional[float] = None
    data_governance_satisfaction: Optional[float] = None
    hr_bp_satisfaction: Optional[float] = None


class PilotMetricsResponse(BaseModel):
    metrics_id: str
    tenant_id: str
    pilot_id: str
    schema_version: str
    week: int
    metrics_date: datetime
    jobs_created: int
    jobs_submitted: int
    jobs_approved: int
    jobs_rejected: int
    jobs_in_revision: int
    avg_approval_time_hours: Optional[float]
    avg_validation_time_hours: Optional[float]
    avg_compensation_review_time_hours: Optional[float]
    nvedo_avg_time_per_job_hours: Optional[float]
    human_exception_quality_score: Optional[float]
    rejection_rate: Optional[float]
    revision_rate: Optional[float]
    generic_filler_rate: Optional[float]
    hiring_manager_satisfaction: Optional[float]
    nvedo_satisfaction: Optional[float]
    data_governance_satisfaction: Optional[float]
    hr_bp_satisfaction: Optional[float]
    created_at: datetime
    updated_at: datetime


class EscalationCreate(BaseModel):
    job_id: Optional[str] = None
    pilot_id: Optional[str] = None
    from_role: str  # data_governance_team, hr_business_partner, nvedo
    to_role: str  # nvedo, c_suite, steering_committee
    reason: str  # policy_conflict, low_quality, human_exception_disagreement, other
    reason_description: Optional[str] = None


class EscalationResponse(BaseModel):
    escalation_id: str
    tenant_id: str
    schema_version: str
    job_id: Optional[str]
    pilot_id: Optional[str]
    from_role: str
    to_role: str
    reason: str
    reason_description: Optional[str]
    status: str
    resolution: Optional[str]
    created_at: datetime
    resolved_at: Optional[datetime]


class JobDescriptionGovernanceCreate(BaseModel):
    job_id: str
    status: str = "draft"
    current_stage: str = "draft"


class JobDescriptionGovernanceResponse(BaseModel):
    governance_id: str
    tenant_id: str
    schema_version: str
    job_id: str
    status: str
    current_stage: str
    validation_status: Optional[str]
    validation_feedback: Optional[str]
    validation_actor_id: Optional[str]
    validation_timestamp: Optional[datetime]
    compensation_status: Optional[str]
    compensation_feedback: Optional[str]
    compensation_actor_id: Optional[str]
    compensation_timestamp: Optional[datetime]
    nvedo_status: Optional[str]
    nvedo_feedback: Optional[str]
    nvedo_actor_id: Optional[str]
    nvedo_timestamp: Optional[datetime]
    conditions: Optional[dict]
    conditions_expiry: Optional[datetime]
    rejection_reason: Optional[str]
    rejection_category: Optional[str]
    total_revision_cycles: int
    total_validation_time_hours: Optional[float]
    total_compensation_review_time_hours: Optional[float]
    total_nvedo_review_time_hours: Optional[float]
    created_at: datetime
    updated_at: datetime


# Governance Configuration Endpoints

@router.post("/config", response_model=GovernanceConfigResponse, status_code=status.HTTP_201_CREATED)
async def create_governance_config(
    config: GovernanceConfigCreate,
    request,
    db: Session = Depends(get_db)
):
    """Create governance configuration for tenant"""
    try:
        tenant_id = get_current_tenant_id(request)
        set_tenant_context(db, tenant_id)
        
        config_id = f"config_{uuid.uuid4().hex[:8]}"
        
        db_config = GovernanceConfig(
            config_id=config_id,
            tenant_id=tenant_id,
            schema_version="1.0",
            nvedo_user_id=config.nvedo_user_id,
            nvedo_mandate_status=config.nvedo_mandate_status,
            raci_board_status=config.raci_board_status,
            governance_enabled=config.governance_enabled,
            pilot_enabled=config.pilot_enabled,
            escalation_enabled=config.escalation_enabled
        )
        
        db.add(db_config)
        db.commit()
        db.refresh(db_config)
        
        return db_config
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create governance config: {str(e)}"
        )


@router.get("/config", response_model=GovernanceConfigResponse)
async def get_governance_config(
    request,
    db: Session = Depends(get_db)
):
    """Get governance configuration for tenant"""
    try:
        tenant_id = get_current_tenant_id(request)
        set_tenant_context(db, tenant_id)
        
        config = db.query(GovernanceConfig).filter(GovernanceConfig.tenant_id == tenant_id).first()
        
        if config is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Governance config not found"
            )
        
        return config
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get governance config: {str(e)}"
        )


@router.put("/config", response_model=GovernanceConfigResponse)
async def update_governance_config(
    config: GovernanceConfigCreate,
    request,
    db: Session = Depends(get_db)
):
    """Update governance configuration for tenant"""
    try:
        tenant_id = get_current_tenant_id(request)
        set_tenant_context(db, tenant_id)
        
        db_config = db.query(GovernanceConfig).filter(GovernanceConfig.tenant_id == tenant_id).first()
        
        if db_config is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Governance config not found"
            )
        
        db_config.nvedo_user_id = config.nvedo_user_id
        db_config.nvedo_mandate_status = config.nvedo_mandate_status
        db_config.raci_board_status = config.raci_board_status
        db_config.governance_enabled = config.governance_enabled
        db_config.pilot_enabled = config.pilot_enabled
        db_config.escalation_enabled = config.escalation_enabled
        
        db.commit()
        db.refresh(db_config)
        
        return db_config
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update governance config: {str(e)}"
        )


# Pilot Configuration Endpoints

@router.post("/pilot", response_model=PilotConfigurationResponse, status_code=status.HTTP_201_CREATED)
async def create_pilot_configuration(
    pilot: PilotConfigurationCreate,
    request,
    db: Session = Depends(get_db)
):
    """Create pilot configuration"""
    try:
        tenant_id = get_current_tenant_id(request)
        set_tenant_context(db, tenant_id)
        
        pilot_id = f"pilot_{uuid.uuid4().hex[:8]}"
        
        db_pilot = PilotConfiguration(
            pilot_id=pilot_id,
            tenant_id=tenant_id,
            schema_version="1.0",
            name=pilot.name,
            description=pilot.description,
            start_date=pilot.start_date,
            end_date=pilot.end_date,
            duration_weeks=pilot.duration_weeks,
            scope=pilot.scope,
            participants=pilot.participants,
            success_criteria=pilot.success_criteria,
            current_week=0,
            status="setup"
        )
        
        db.add(db_pilot)
        db.commit()
        db.refresh(db_pilot)
        
        return db_pilot
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create pilot configuration: {str(e)}"
        )


@router.get("/pilot/{pilot_id}", response_model=PilotConfigurationResponse)
async def get_pilot_configuration(
    pilot_id: str,
    request,
    db: Session = Depends(get_db)
):
    """Get pilot configuration by ID"""
    try:
        tenant_id = get_current_tenant_id(request)
        set_tenant_context(db, tenant_id)
        
        pilot = db.query(PilotConfiguration).filter(
            PilotConfiguration.pilot_id == pilot_id
        ).first()
        
        if pilot is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Pilot not found: {pilot_id}"
            )
        
        return pilot
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get pilot configuration: {str(e)}"
        )


@router.put("/pilot/{pilot_id}/start", response_model=PilotConfigurationResponse)
async def start_pilot(
    pilot_id: str,
    request,
    db: Session = Depends(get_db)
):
    """Start pilot"""
    try:
        tenant_id = get_current_tenant_id(request)
        set_tenant_context(db, tenant_id)
        
        pilot = db.query(PilotConfiguration).filter(
            PilotConfiguration.pilot_id == pilot_id
        ).first()
        
        if pilot is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Pilot not found: {pilot_id}"
            )
        
        pilot.status = "active"
        pilot.current_week = 1
        
        db.commit()
        db.refresh(pilot)
        
        return pilot
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start pilot: {str(e)}"
        )


@router.put("/pilot/{pilot_id}/stop", response_model=PilotConfigurationResponse)
async def stop_pilot(
    pilot_id: str,
    request,
    db: Session = Depends(get_db)
):
    """Stop pilot"""
    try:
        tenant_id = get_current_tenant_id(request)
        set_tenant_context(db, tenant_id)
        
        pilot = db.query(PilotConfiguration).filter(
            PilotConfiguration.pilot_id == pilot_id
        ).first()
        
        if pilot is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Pilot not found: {pilot_id}"
            )
        
        pilot.status = "completed"
        
        db.commit()
        db.refresh(pilot)
        
        return pilot
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to stop pilot: {str(e)}"
        )


# Pilot Metrics Endpoints

@router.post("/pilot/{pilot_id}/metrics", response_model=PilotMetricsResponse, status_code=status.HTTP_201_CREATED)
async def create_pilot_metrics(
    pilot_id: str,
    metrics: PilotMetricsCreate,
    request,
    db: Session = Depends(get_db)
):
    """Create pilot metrics for a week"""
    try:
        tenant_id = get_current_tenant_id(request)
        set_tenant_context(db, tenant_id)
        
        metrics_id = f"metrics_{uuid.uuid4().hex[:8]}"
        
        db_metrics = PilotMetrics(
            metrics_id=metrics_id,
            tenant_id=tenant_id,
            pilot_id=pilot_id,
            schema_version="1.0",
            week=metrics.week,
            metrics_date=metrics.metrics_date,
            jobs_created=metrics.jobs_created,
            jobs_submitted=metrics.jobs_submitted,
            jobs_approved=metrics.jobs_approved,
            jobs_rejected=metrics.jobs_rejected,
            jobs_in_revision=metrics.jobs_in_revision,
            avg_approval_time_hours=metrics.avg_approval_time_hours,
            avg_validation_time_hours=metrics.avg_validation_time_hours,
            avg_compensation_review_time_hours=metrics.avg_compensation_review_time_hours,
            nvedo_avg_time_per_job_hours=metrics.nvedo_avg_time_per_job_hours,
            human_exception_quality_score=metrics.human_exception_quality_score,
            rejection_rate=metrics.rejection_rate,
            revision_rate=metrics.revision_rate,
            generic_filler_rate=metrics.generic_filler_rate,
            hiring_manager_satisfaction=metrics.hiring_manager_satisfaction,
            nvedo_satisfaction=metrics.nvedo_satisfaction,
            data_governance_satisfaction=metrics.data_governance_satisfaction,
            hr_bp_satisfaction=metrics.hr_bp_satisfaction
        )
        
        db.add(db_metrics)
        db.commit()
        db.refresh(db_metrics)
        
        return db_metrics
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create pilot metrics: {str(e)}"
        )


@router.get("/pilot/{pilot_id}/metrics", response_model=List[PilotMetricsResponse])
async def get_pilot_metrics(
    pilot_id: str,
    request,
    db: Session = Depends(get_db)
):
    """Get all metrics for a pilot"""
    try:
        tenant_id = get_current_tenant_id(request)
        set_tenant_context(db, tenant_id)
        
        metrics = db.query(PilotMetrics).filter(
            PilotMetrics.pilot_id == pilot_id
        ).order_by(PilotMetrics.week).all()
        
        return metrics
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get pilot metrics: {str(e)}"
        )


# Escalation Endpoints

@router.post("/escalation", response_model=EscalationResponse, status_code=status.HTTP_201_CREATED)
async def create_escalation(
    escalation: EscalationCreate,
    request,
    db: Session = Depends(get_db)
):
    """Create escalation"""
    try:
        tenant_id = get_current_tenant_id(request)
        set_tenant_context(db, tenant_id)
        
        escalation_id = f"escalation_{uuid.uuid4().hex[:8]}"
        
        db_escalation = Escalation(
            escalation_id=escalation_id,
            tenant_id=tenant_id,
            schema_version="1.0",
            job_id=escalation.job_id,
            pilot_id=escalation.pilot_id,
            from_role=escalation.from_role,
            to_role=escalation.to_role,
            reason=escalation.reason,
            reason_description=escalation.reason_description,
            status="pending"
        )
        
        db.add(db_escalation)
        db.commit()
        db.refresh(db_escalation)
        
        return db_escalation
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create escalation: {str(e)}"
        )


@router.get("/escalation/{escalation_id}", response_model=EscalationResponse)
async def get_escalation(
    escalation_id: str,
    request,
    db: Session = Depends(get_db)
):
    """Get escalation by ID"""
    try:
        tenant_id = get_current_tenant_id(request)
        set_tenant_context(db, tenant_id)
        
        escalation = db.query(Escalation).filter(
            Escalation.escalation_id == escalation_id
        ).first()
        
        if escalation is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Escalation not found: {escalation_id}"
            )
        
        return escalation
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get escalation: {str(e)}"
        )


@router.put("/escalation/{escalation_id}/resolve", response_model=EscalationResponse)
async def resolve_escalation(
    escalation_id: str,
    resolution: str,
    request,
    db: Session = Depends(get_db)
):
    """Resolve escalation"""
    try:
        tenant_id = get_current_tenant_id(request)
        set_tenant_context(db, tenant_id)
        
        escalation = db.query(Escalation).filter(
            Escalation.escalation_id == escalation_id
        ).first()
        
        if escalation is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Escalation not found: {escalation_id}"
            )
        
        escalation.status = "resolved"
        escalation.resolution = resolution
        escalation.resolved_at = datetime.utcnow()
        
        db.commit()
        db.refresh(escalation)
        
        return escalation
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to resolve escalation: {str(e)}"
        )


# Job Description Governance Endpoints

@router.post("/job-governance", response_model=JobDescriptionGovernanceResponse, status_code=status.HTTP_201_CREATED)
async def create_job_governance(
    governance: JobDescriptionGovernanceCreate,
    request,
    db: Session = Depends(get_db)
):
    """Create job description governance record"""
    try:
        tenant_id = get_current_tenant_id(request)
        set_tenant_context(db, tenant_id)
        
        governance_id = f"governance_{uuid.uuid4().hex[:8]}"
        
        db_governance = JobDescriptionGovernance(
            governance_id=governance_id,
            tenant_id=tenant_id,
            schema_version="1.0",
            job_id=governance.job_id,
            status=governance.status,
            current_stage=governance.current_stage
        )
        
        db.add(db_governance)
        db.commit()
        db.refresh(db_governance)
        
        return db_governance
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create job governance: {str(e)}"
        )


@router.get("/job-governance/{job_id}", response_model=JobDescriptionGovernanceResponse)
async def get_job_governance(
    job_id: str,
    request,
    db: Session = Depends(get_db)
):
    """Get job description governance by job ID"""
    try:
        tenant_id = get_current_tenant_id(request)
        set_tenant_context(db, tenant_id)
        
        governance = db.query(JobDescriptionGovernance).filter(
            JobDescriptionGovernance.job_id == job_id
        ).first()
        
        if governance is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Job governance not found: {job_id}"
            )
        
        return governance
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get job governance: {str(e)}"
        )


@router.put("/job-governance/{governance_id}/validate", response_model=JobDescriptionGovernanceResponse)
async def validate_job_governance(
    governance_id: str,
    validation_status: str,
    validation_feedback: Optional[str] = None,
    request,
    db: Session = Depends(get_db)
):
    """Validate job description (Data Governance Team)"""
    try:
        tenant_id = get_current_tenant_id(request)
        set_tenant_context(db, tenant_id)
        
        governance = db.query(JobDescriptionGovernance).filter(
            JobDescriptionGovernance.governance_id == governance_id
        ).first()
        
        if governance is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Job governance not found: {governance_id}"
            )
        
        governance.validation_status = validation_status
        governance.validation_feedback = validation_feedback
        governance.validation_timestamp = datetime.utcnow()
        
        if validation_status == "passed":
            governance.status = "pending_compensation_review"
            governance.current_stage = "compensation_review"
        
        db.commit()
        db.refresh(governance)
        
        return governance
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to validate job governance: {str(e)}"
        )


@router.put("/job-governance/{governance_id}/approve", response_model=JobDescriptionGovernanceResponse)
async def approve_job_governance(
    governance_id: str,
    nvedo_feedback: Optional[str] = None,
    request,
    db: Session = Depends(get_db)
):
    """Approve job description (NVEDO)"""
    try:
        tenant_id = get_current_tenant_id(request)
        set_tenant_context(db, tenant_id)
        
        governance = db.query(JobDescriptionGovernance).filter(
            JobDescriptionGovernance.governance_id == governance_id
        ).first()
        
        if governance is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Job governance not found: {governance_id}"
            )
        
        governance.nvedo_status = "approved"
        governance.nvedo_feedback = nvedo_feedback
        governance.nvedo_timestamp = datetime.utcnow()
        governance.status = "approved"
        governance.current_stage = "approved"
        
        db.commit()
        db.refresh(governance)
        
        return governance
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to approve job governance: {str(e)}"
        )


@router.put("/job-governance/{governance_id}/reject", response_model=JobDescriptionGovernanceResponse)
async def reject_job_governance(
    governance_id: str,
    rejection_reason: str,
    rejection_category: str,
    request,
    db: Session = Depends(get_db)
):
    """Reject job description (NVEDO)"""
    try:
        tenant_id = get_current_tenant_id(request)
        set_tenant_context(db, tenant_id)
        
        governance = db.query(JobDescriptionGovernance).filter(
            JobDescriptionGovernance.governance_id == governance_id
        ).first()
        
        if governance is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Job governance not found: {governance_id}"
            )
        
        governance.nvedo_status = "rejected"
        governance.nvedo_feedback = rejection_reason
        governance.nvedo_timestamp = datetime.utcnow()
        governance.status = "rejected"
        governance.current_stage = "rejected"
        governance.rejection_reason = rejection_reason
        governance.rejection_category = rejection_category
        governance.total_revision_cycles += 1
        
        db.commit()
        db.refresh(governance)
        
        return governance
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to reject job governance: {str(e)}"
        )
