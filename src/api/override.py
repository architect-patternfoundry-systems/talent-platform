"""Override API endpoints"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
import uuid

from src.core.database import get_db
from src.core.middleware import get_current_tenant_id
from src.core.tenant import set_tenant_context
from src.models.match import MatchResult
from src.models.override import OverrideLog


router = APIRouter(prefix="/v1/override", tags=["override"])


# Pydantic models for request/response
class OverrideRequest(BaseModel):
    match_id: str
    new_score: float
    reason: str


class OverrideResponse(BaseModel):
    override_id: str
    tenant_id: str
    schema_version: str
    entity_type: str
    entity_id: str
    override_reason: str
    override_author: str
    override_timestamp: datetime
    original_value: dict
    override_value: dict
    impact: str
    created_at: datetime


@router.post("/", response_model=OverrideResponse, status_code=status.HTTP_201_CREATED)
async def create_override(
    override_request: OverrideRequest,
    request,
    db: Session = Depends(get_db)
):
    """Create an override for a match score"""
    try:
        # Get tenant_id from request state
        tenant_id = get_current_tenant_id(request)
        
        # Set tenant context in database session
        set_tenant_context(db, tenant_id)
        
        # Get match
        match = db.query(MatchResult).filter(
            MatchResult.match_id == override_request.match_id,
            MatchResult.tenant_id == tenant_id
        ).first()
        
        if not match:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Match not found: {override_request.match_id}"
            )
        
        # Store original score
        original_score = match.overall_score
        
        # Update match score
        match.overall_score = override_request.new_score
        match.override_reason = override_request.reason
        match.override_author = "current_user"  # In production, this would be from JWT
        match.override_timestamp = datetime.utcnow()
        match.original_score = original_score
        
        # Determine impact
        if override_request.new_score > original_score:
            impact = "increased"
        elif override_request.new_score < original_score:
            impact = "decreased"
        else:
            impact = "neutral"
        
        # Create override log
        override_id = f"override_{uuid.uuid4().hex[:8]}"
        
        override_log = OverrideLog(
            override_id=override_id,
            tenant_id=tenant_id,
            schema_version="1.0",
            entity_type="match",
            entity_id=override_request.match_id,
            override_reason=override_request.reason,
            override_author="current_user",  # In production, this would be from JWT
            override_timestamp=datetime.utcnow(),
            original_value={"overall_score": original_score},
            override_value={"overall_score": override_request.new_score},
            impact=impact
        )
        
        db.add(override_log)
        db.commit()
        db.refresh(override_log)
        
        return override_log
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create override: {str(e)}"
        )


@router.get("/{override_id}", response_model=OverrideResponse)
async def get_override(
    override_id: str,
    request,
    db: Session = Depends(get_db)
):
    """Get an override log by ID"""
    try:
        # Get tenant_id from request state
        tenant_id = get_current_tenant_id(request)
        
        # Set tenant context in database session
        set_tenant_context(db, tenant_id)
        
        # Query override
        override = db.query(OverrideLog).filter(
            OverrideLog.override_id == override_id
        ).first()
        
        if override is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Override not found: {override_id}"
            )
        
        return override
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get override: {str(e)}"
        )


@router.get("/", response_model=List[OverrideResponse])
async def list_overrides(
    request,
    db: Session = Depends(get_db),
    entity_type: Optional[str] = None,
    entity_id: Optional[str] = None,
    skip: int = 0,
    limit: int = 100
):
    """List override logs for the current tenant"""
    try:
        # Get tenant_id from request state
        tenant_id = get_current_tenant_id(request)
        
        # Set tenant context in database session
        set_tenant_context(db, tenant_id)
        
        # Query overrides
        query = db.query(OverrideLog)
        
        if entity_type:
            query = query.filter(OverrideLog.entity_type == entity_type)
        
        if entity_id:
            query = query.filter(OverrideLog.entity_id == entity_id)
        
        overrides = query.offset(skip).limit(limit).all()
        
        return overrides
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list overrides: {str(e)}"
        )
