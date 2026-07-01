"""Personal Profile API endpoints"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
from datetime import datetime
import uuid

from src.core.database import get_db
from src.core.middleware import get_current_tenant_id
from src.core.tenant import set_tenant_context
from src.models.profile import PersonalProfile


router = APIRouter(prefix="/v1/profiles", tags=["profiles"])


# Pydantic models for request/response
class PersonalProfileCreate(BaseModel):
    name: str
    skills: dict
    aspirations: dict
    experience: dict
    availability: dict
    platform_preferences: dict
    human_exception: str
    confidence: str  # "high" | "medium" | "low"
    evidence_quality: str  # "verified" | "self_reported" | "unverified"
    evidence_sources: List[str]


class PersonalProfileUpdate(BaseModel):
    name: str
    skills: dict
    aspirations: dict
    experience: dict
    availability: dict
    platform_preferences: dict
    human_exception: str
    confidence: str  # "high" | "medium" | "low"
    evidence_quality: str  # "verified" | "self_reported" | "unverified"
    evidence_sources: List[str]


class PersonalProfileResponse(BaseModel):
    profile_id: str
    tenant_id: str
    schema_version: str
    name: str
    skills: dict
    aspirations: dict
    experience: dict
    availability: dict
    platform_preferences: dict
    human_exception: str
    confidence: str
    evidence_quality: str
    evidence_sources: List[str]
    created_at: datetime
    updated_at: datetime


@router.post("/", response_model=PersonalProfileResponse, status_code=status.HTTP_201_CREATED)
async def create_profile(
    profile: PersonalProfileCreate,
    request,
    db: Session = Depends(get_db)
):
    """Create a new personal profile"""
    try:
        # Get tenant_id from request state
        tenant_id = get_current_tenant_id(request)
        
        # Set tenant context in database session
        set_tenant_context(db, tenant_id)
        
        # Generate profile_id
        profile_id = f"profile_{uuid.uuid4().hex[:8]}"
        
        # Create personal profile
        db_profile = PersonalProfile(
            profile_id=profile_id,
            tenant_id=tenant_id,
            schema_version="1.0",
            name=profile.name,
            skills=profile.skills,
            aspirations=profile.aspirations,
            experience=profile.experience,
            availability=profile.availability,
            platform_preferences=profile.platform_preferences,
            human_exception=profile.human_exception,
            confidence=profile.confidence,
            evidence_quality=profile.evidence_quality,
            evidence_sources=profile.evidence_sources
        )
        
        db.add(db_profile)
        db.commit()
        db.refresh(db_profile)
        
        return db_profile
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create profile: {str(e)}"
        )


@router.get("/{profile_id}", response_model=PersonalProfileResponse)
async def get_profile(
    profile_id: str,
    request,
    db: Session = Depends(get_db)
):
    """Get a personal profile by ID"""
    try:
        # Get tenant_id from request state
        tenant_id = get_current_tenant_id(request)
        
        # Set tenant context in database session
        set_tenant_context(db, tenant_id)
        
        # Query profile
        profile = db.query(PersonalProfile).filter(PersonalProfile.profile_id == profile_id).first()
        
        if profile is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Profile not found: {profile_id}"
            )
        
        return profile
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get profile: {str(e)}"
        )


@router.put("/{profile_id}", response_model=PersonalProfileResponse)
async def update_profile(
    profile_id: str,
    profile: PersonalProfileUpdate,
    request,
    db: Session = Depends(get_db)
):
    """Update a personal profile (full replacement)"""
    try:
        # Get tenant_id from request state
        tenant_id = get_current_tenant_id(request)
        
        # Set tenant context in database session
        set_tenant_context(db, tenant_id)
        
        # Query profile
        db_profile = db.query(PersonalProfile).filter(PersonalProfile.profile_id == profile_id).first()
        
        if db_profile is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Profile not found: {profile_id}"
            )
        
        # Update profile (full replacement)
        db_profile.name = profile.name
        db_profile.skills = profile.skills
        db_profile.aspirations = profile.aspirations
        db_profile.experience = profile.experience
        db_profile.availability = profile.availability
        db_profile.platform_preferences = profile.platform_preferences
        db_profile.human_exception = profile.human_exception
        db_profile.confidence = profile.confidence
        db_profile.evidence_quality = profile.evidence_quality
        db_profile.evidence_sources = profile.evidence_sources
        
        db.commit()
        db.refresh(db_profile)
        
        return db_profile
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update profile: {str(e)}"
        )


@router.delete("/{profile_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_profile(
    profile_id: str,
    request,
    db: Session = Depends(get_db)
):
    """Delete a personal profile"""
    try:
        # Get tenant_id from request state
        tenant_id = get_current_tenant_id(request)
        
        # Set tenant context in database session
        set_tenant_context(db, tenant_id)
        
        # Query profile
        profile = db.query(PersonalProfile).filter(PersonalProfile.profile_id == profile_id).first()
        
        if profile is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Profile not found: {profile_id}"
            )
        
        # Delete profile
        db.delete(profile)
        db.commit()
        
        return None
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete profile: {str(e)}"
        )


@router.get("/", response_model=List[PersonalProfileResponse])
async def list_profiles(
    request,
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100
):
    """List all personal profiles for the current tenant"""
    try:
        # Get tenant_id from request state
        tenant_id = get_current_tenant_id(request)
        
        # Set tenant context in database session
        set_tenant_context(db, tenant_id)
        
        # Query profiles
        profiles = db.query(PersonalProfile).offset(skip).limit(limit).all()
        
        return profiles
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list profiles: {str(e)}"
        )
