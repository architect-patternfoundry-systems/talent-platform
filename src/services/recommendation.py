"""Recommendation service for profiles and roles"""
from typing import List, Optional
from sqlalchemy.orm import Session
from src.models.profile import PersonalProfile
from src.models.role import RoleDefinition
from src.models.match import MatchResult
from src.services.matching import MatchingService


class RecommendationService:
    """Service for generating recommendations for profiles and roles"""
    
    def __init__(self, db: Session, tenant_id: str):
        self.db = db
        self.tenant_id = tenant_id
        self.matching_service = MatchingService(db, tenant_id)
    
    def recommend_roles_for_profile(
        self,
        profile_id: str,
        limit: int = 10,
        min_score: float = 0.0
    ) -> List[dict]:
        """Recommend roles for a given profile"""
        # Get profile
        profile = self.db.query(PersonalProfile).filter(
            PersonalProfile.profile_id == profile_id,
            PersonalProfile.tenant_id == self.tenant_id
        ).first()
        
        if not profile:
            raise ValueError(f"Profile not found: {profile_id}")
        
        # Get all roles
        roles = self.db.query(RoleDefinition).filter(
            RoleDefinition.tenant_id == self.tenant_id
        ).all()
        
        # Calculate matches for all roles
        recommendations = []
        for role in roles:
            try:
                match = self.matching_service.calculate_match(profile_id, role.role_id)
                if match.overall_score >= min_score:
                    recommendations.append({
                        "role_id": role.role_id,
                        "role_name": role.name,
                        "match_id": match.match_id,
                        "overall_score": match.overall_score,
                        "skill_overlap": match.skill_overlap,
                        "aspiration_alignment": match.aspiration_alignment,
                        "availability_match": match.availability_match,
                        "platform_match": match.platform_match
                    })
            except Exception as e:
                # Skip roles that fail to match
                continue
        
        # Sort by overall score (descending)
        recommendations.sort(key=lambda x: x["overall_score"], reverse=True)
        
        # Limit results
        recommendations = recommendations[:limit]
        
        return recommendations
    
    def recommend_profiles_for_role(
        self,
        role_id: str,
        limit: int = 10,
        min_score: float = 0.0
    ) -> List[dict]:
        """Recommend profiles for a given role"""
        # Get role
        role = self.db.query(RoleDefinition).filter(
            RoleDefinition.role_id == role_id,
            RoleDefinition.tenant_id == self.tenant_id
        ).first()
        
        if not role:
            raise ValueError(f"Role not found: {role_id}")
        
        # Get all profiles
        profiles = self.db.query(PersonalProfile).filter(
            PersonalProfile.tenant_id == self.tenant_id
        ).all()
        
        # Calculate matches for all profiles
        recommendations = []
        for profile in profiles:
            try:
                match = self.matching_service.calculate_match(profile.profile_id, role_id)
                if match.overall_score >= min_score:
                    recommendations.append({
                        "profile_id": profile.profile_id,
                        "profile_name": profile.name,
                        "match_id": match.match_id,
                        "overall_score": match.overall_score,
                        "skill_overlap": match.skill_overlap,
                        "aspiration_alignment": match.aspiration_alignment,
                        "availability_match": match.availability_match,
                        "platform_match": match.platform_match
                    })
            except Exception as e:
                # Skip profiles that fail to match
                continue
        
        # Sort by overall score (descending)
        recommendations.sort(key=lambda x: x["overall_score"], reverse=True)
        
        # Limit results
        recommendations = recommendations[:limit]
        
        return recommendations
