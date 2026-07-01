"""Recommendation API endpoints"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel

from src.core.database import get_db
from src.core.middleware import get_current_tenant_id
from src.core.tenant import set_tenant_context
from src.services.recommendation import RecommendationService


router = APIRouter(prefix="/v1/recommendation", tags=["recommendation"])


# Pydantic models for request/response
class RoleRecommendationRequest(BaseModel):
    profile_id: str
    limit: int = 10
    min_score: float = 0.0


class ProfileRecommendationRequest(BaseModel):
    role_id: str
    limit: int = 10
    min_score: float = 0.0


@router.post("/roles")
async def recommend_roles(
    request_body: RoleRecommendationRequest,
    request,
    db: Session = Depends(get_db)
):
    """Recommend roles for a given profile"""
    try:
        # Get tenant_id from request state
        tenant_id = get_current_tenant_id(request)
        
        # Set tenant context in database session
        set_tenant_context(db, tenant_id)
        
        # Create recommendation service
        rec_service = RecommendationService(db, tenant_id)
        
        # Generate recommendations
        recommendations = rec_service.recommend_roles_for_profile(
            request_body.profile_id,
            request_body.limit,
            request_body.min_score
        )
        
        return {
            "profile_id": request_body.profile_id,
            "recommendations": recommendations,
            "count": len(recommendations)
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate role recommendations: {str(e)}"
        )


@router.post("/profiles")
async def recommend_profiles(
    request_body: ProfileRecommendationRequest,
    request,
    db: Session = Depends(get_db)
):
    """Recommend profiles for a given role"""
    try:
        # Get tenant_id from request state
        tenant_id = get_current_tenant_id(request)
        
        # Set tenant context in database session
        set_tenant_context(db, tenant_id)
        
        # Create recommendation service
        rec_service = RecommendationService(db, tenant_id)
        
        # Generate recommendations
        recommendations = rec_service.recommend_profiles_for_role(
            request_body.role_id,
            request_body.limit,
            request_body.min_score
        )
        
        return {
            "role_id": request_body.role_id,
            "recommendations": recommendations,
            "count": len(recommendations)
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate profile recommendations: {str(e)}"
        )
