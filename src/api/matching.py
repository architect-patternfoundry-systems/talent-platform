"""Matching API endpoints"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from src.core.database import get_db
from src.core.middleware import get_current_tenant_id
from src.core.tenant import set_tenant_context
from src.services.matching import MatchingService
from src.models.match import MatchResult


router = APIRouter(prefix="/v1/match", tags=["matching"])


# Pydantic models for request/response
class MatchRequest(BaseModel):
    profile_id: str
    role_id: str
    weights: Optional[dict] = None


class MatchResponse(BaseModel):
    match_id: str
    tenant_id: str
    schema_version: str
    profile_id: str
    role_id: str
    skill_overlap: float
    aspiration_alignment: float
    availability_match: float
    platform_match: float
    overall_score: float
    human_exception_alignment: float
    human_exception_rationale: str
    confidence: str
    evidence_quality: str
    override_reason: Optional[str] = None
    override_author: Optional[str] = None
    override_timestamp: Optional[datetime] = None
    original_score: Optional[float] = None
    created_at: datetime
    updated_at: datetime


@router.post("/", response_model=MatchResponse, status_code=status.HTTP_201_CREATED)
async def calculate_match(
    match_request: MatchRequest,
    request,
    db: Session = Depends(get_db)
):
    """Calculate match between profile and role"""
    try:
        # Get tenant_id from request state
        tenant_id = get_current_tenant_id(request)
        
        # Set tenant context in database session
        set_tenant_context(db, tenant_id)
        
        # Create matching service
        matching_service = MatchingService(db, tenant_id)
        
        # Calculate match
        match_result = matching_service.calculate_match(
            match_request.profile_id,
            match_request.role_id,
            match_request.weights
        )
        
        # Save match result
        db.add(match_result)
        db.commit()
        db.refresh(match_result)
        
        return match_result
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to calculate match: {str(e)}"
        )


@router.get("/{match_id}", response_model=MatchResponse)
async def get_match(
    match_id: str,
    request,
    db: Session = Depends(get_db)
):
    """Get a match result by ID"""
    try:
        # Get tenant_id from request state
        tenant_id = get_current_tenant_id(request)
        
        # Set tenant context in database session
        set_tenant_context(db, tenant_id)
        
        # Query match
        match = db.query(MatchResult).filter(MatchResult.match_id == match_id).first()
        
        if match is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Match not found: {match_id}"
            )
        
        return match
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get match: {str(e)}"
        )


@router.get("/", response_model=List[MatchResponse])
async def list_matches(
    request,
    db: Session = Depends(get_db),
    profile_id: Optional[str] = None,
    role_id: Optional[str] = None,
    skip: int = 0,
    limit: int = 100
):
    """List match results for the current tenant"""
    try:
        # Get tenant_id from request state
        tenant_id = get_current_tenant_id(request)
        
        # Set tenant context in database session
        set_tenant_context(db, tenant_id)
        
        # Query matches
        query = db.query(MatchResult)
        
        if profile_id:
            query = query.filter(MatchResult.profile_id == profile_id)
        
        if role_id:
            query = query.filter(MatchResult.role_id == role_id)
        
        matches = query.offset(skip).limit(limit).all()
        
        return matches
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list matches: {str(e)}"
        )
