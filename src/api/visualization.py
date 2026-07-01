"""Visualization API endpoints"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel

from src.core.database import get_db
from src.core.middleware import get_current_tenant_id
from src.core.tenant import set_tenant_context
from src.services.visualization import VisualizationService


router = APIRouter(prefix="/v1/visualization", tags=["visualization"])


# Pydantic models for request/response
class VennDiagramRequest(BaseModel):
    profile_id: str
    role_id: str


class MatchScoreBreakdownRequest(BaseModel):
    match_id: str


class ConfidenceEvidenceQualityRequest(BaseModel):
    match_id: str


@router.post("/venn-diagram")
async def get_venn_diagram_data(
    request_body: VennDiagramRequest,
    request,
    db: Session = Depends(get_db)
):
    """Get Venn diagram data for profile and role"""
    try:
        # Get tenant_id from request state
        tenant_id = get_current_tenant_id(request)
        
        # Set tenant context in database session
        set_tenant_context(db, tenant_id)
        
        # Create visualization service
        viz_service = VisualizationService(db, tenant_id)
        
        # Generate Venn diagram data
        venn_data = viz_service.generate_venn_diagram_data(
            request_body.profile_id,
            request_body.role_id
        )
        
        return venn_data
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate Venn diagram data: {str(e)}"
        )


@router.post("/match-score-breakdown")
async def get_match_score_breakdown(
    request_body: MatchScoreBreakdownRequest,
    request,
    db: Session = Depends(get_db)
):
    """Get match score breakdown for visualization"""
    try:
        # Get tenant_id from request state
        tenant_id = get_current_tenant_id(request)
        
        # Set tenant context in database session
        set_tenant_context(db, tenant_id)
        
        # Create visualization service
        viz_service = VisualizationService(db, tenant_id)
        
        # Generate match score breakdown
        score_breakdown = viz_service.generate_match_score_breakdown(
            request_body.match_id
        )
        
        return score_breakdown
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate match score breakdown: {str(e)}"
        )


@router.post("/confidence-evidence-quality")
async def get_confidence_evidence_quality_data(
    request_body: ConfidenceEvidenceQualityRequest,
    request,
    db: Session = Depends(get_db)
):
    """Get confidence and evidence quality data for visualization"""
    try:
        # Get tenant_id from request state
        tenant_id = get_current_tenant_id(request)
        
        # Set tenant context in database session
        set_tenant_context(db, tenant_id)
        
        # Create visualization service
        viz_service = VisualizationService(db, tenant_id)
        
        # Generate confidence and evidence quality data
        confidence_data = viz_service.generate_confidence_evidence_quality_data(
            request_body.match_id
        )
        
        return confidence_data
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate confidence and evidence quality data: {str(e)}"
        )
