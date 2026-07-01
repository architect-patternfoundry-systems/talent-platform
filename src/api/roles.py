"""Role Definition API endpoints"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
from datetime import datetime
import uuid

from src.core.database import get_db
from src.core.middleware import get_current_tenant_id, get_db_with_tenant_context
from src.core.tenant import set_tenant_context
from src.models.role import RoleDefinition
from src.core.auth import verify_token


router = APIRouter(prefix="/v1/roles", tags=["roles"])


# Pydantic models for request/response
class RoleDefinitionCreate(BaseModel):
    name: str
    description: str
    skills: dict
    scope: dict
    success_criteria: List[str]
    platform_requirements: dict
    human_exception: str
    confidence: str  # "high" | "medium" | "low"
    evidence_quality: str  # "verified" | "self_reported" | "unverified"
    evidence_sources: List[str]


class RoleDefinitionUpdate(BaseModel):
    name: str
    description: str
    skills: dict
    scope: dict
    success_criteria: List[str]
    platform_requirements: dict
    human_exception: str
    confidence: str  # "high" | "medium" | "low"
    evidence_quality: str  # "verified" | "self_reported" | "unverified"
    evidence_sources: List[str]


class RoleDefinitionResponse(BaseModel):
    role_id: str
    tenant_id: str
    schema_version: str
    name: str
    description: str
    skills: dict
    scope: dict
    success_criteria: List[str]
    platform_requirements: dict
    human_exception: str
    confidence: str
    evidence_quality: str
    evidence_sources: List[str]
    created_at: datetime
    updated_at: datetime


@router.post("/", response_model=RoleDefinitionResponse, status_code=status.HTTP_201_CREATED)
async def create_role(
    role: RoleDefinitionCreate,
    request,
    db: Session = Depends(get_db)
):
    """Create a new role definition"""
    try:
        # Get tenant_id from request state
        tenant_id = get_current_tenant_id(request)
        
        # Set tenant context in database session
        set_tenant_context(db, tenant_id)
        
        # Generate role_id
        role_id = f"role_{uuid.uuid4().hex[:8]}"
        
        # Create role definition
        db_role = RoleDefinition(
            role_id=role_id,
            tenant_id=tenant_id,
            schema_version="1.0",
            name=role.name,
            description=role.description,
            skills=role.skills,
            scope=role.scope,
            success_criteria=role.success_criteria,
            platform_requirements=role.platform_requirements,
            human_exception=role.human_exception,
            confidence=role.confidence,
            evidence_quality=role.evidence_quality,
            evidence_sources=role.evidence_sources
        )
        
        db.add(db_role)
        db.commit()
        db.refresh(db_role)
        
        return db_role
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create role: {str(e)}"
        )


@router.get("/{role_id}", response_model=RoleDefinitionResponse)
async def get_role(
    role_id: str,
    request,
    db: Session = Depends(get_db)
):
    """Get a role definition by ID"""
    try:
        # Get tenant_id from request state
        tenant_id = get_current_tenant_id(request)
        
        # Set tenant context in database session
        set_tenant_context(db, tenant_id)
        
        # Query role
        role = db.query(RoleDefinition).filter(RoleDefinition.role_id == role_id).first()
        
        if role is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Role not found: {role_id}"
            )
        
        return role
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get role: {str(e)}"
        )


@router.put("/{role_id}", response_model=RoleDefinitionResponse)
async def update_role(
    role_id: str,
    role: RoleDefinitionUpdate,
    request,
    db: Session = Depends(get_db)
):
    """Update a role definition (full replacement)"""
    try:
        # Get tenant_id from request state
        tenant_id = get_current_tenant_id(request)
        
        # Set tenant context in database session
        set_tenant_context(db, tenant_id)
        
        # Query role
        db_role = db.query(RoleDefinition).filter(RoleDefinition.role_id == role_id).first()
        
        if db_role is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Role not found: {role_id}"
            )
        
        # Update role (full replacement)
        db_role.name = role.name
        db_role.description = role.description
        db_role.skills = role.skills
        db_role.scope = role.scope
        db_role.success_criteria = role.success_criteria
        db_role.platform_requirements = role.platform_requirements
        db_role.human_exception = role.human_exception
        db_role.confidence = role.confidence
        db_role.evidence_quality = role.evidence_quality
        db_role.evidence_sources = role.evidence_sources
        
        db.commit()
        db.refresh(db_role)
        
        return db_role
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update role: {str(e)}"
        )


@router.delete("/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_role(
    role_id: str,
    request,
    db: Session = Depends(get_db)
):
    """Delete a role definition"""
    try:
        # Get tenant_id from request state
        tenant_id = get_current_tenant_id(request)
        
        # Set tenant context in database session
        set_tenant_context(db, tenant_id)
        
        # Query role
        role = db.query(RoleDefinition).filter(RoleDefinition.role_id == role_id).first()
        
        if role is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Role not found: {role_id}"
            )
        
        # Delete role
        db.delete(role)
        db.commit()
        
        return None
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete role: {str(e)}"
        )


@router.get("/", response_model=List[RoleDefinitionResponse])
async def list_roles(
    request,
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100
):
    """List all role definitions for the current tenant"""
    try:
        # Get tenant_id from request state
        tenant_id = get_current_tenant_id(request)
        
        # Set tenant context in database session
        set_tenant_context(db, tenant_id)
        
        # Query roles
        roles = db.query(RoleDefinition).offset(skip).limit(limit).all()
        
        return roles
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list roles: {str(e)}"
        )
