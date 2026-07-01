"""Visualization service for match results"""
from typing import Dict, List, Optional
from sqlalchemy.orm import Session
from src.models.match import MatchResult
from src.models.profile import PersonalProfile
from src.models.role import RoleDefinition


class VisualizationService:
    """Service for generating visualization data for match results"""
    
    def __init__(self, db: Session, tenant_id: str):
        self.db = db
        self.tenant_id = tenant_id
    
    def generate_venn_diagram_data(self, profile_id: str, role_id: str) -> Dict:
        """Generate data for Venn diagram visualization"""
        # Get profile
        profile = self.db.query(PersonalProfile).filter(
            PersonalProfile.profile_id == profile_id,
            PersonalProfile.tenant_id == self.tenant_id
        ).first()
        
        if not profile:
            raise ValueError(f"Profile not found: {profile_id}")
        
        # Get role
        role = self.db.query(RoleDefinition).filter(
            RoleDefinition.role_id == role_id,
            RoleDefinition.tenant_id == self.tenant_id
        ).first()
        
        if not role:
            raise ValueError(f"Role not found: {role_id}")
        
        # Extract skills
        profile_skills = profile.skills
        role_skills = role.skills
        
        # Calculate skill sets
        profile_technical = set(profile_skills.get("technical", {}).keys())
        profile_soft = set(profile_skills.get("soft", {}).keys())
        profile_platform = set(profile_skills.get("platform", {}).keys())
        
        role_technical = set(role_skills.get("technical", {}).keys())
        role_soft = set(role_skills.get("soft", {}).keys())
        role_platform = set(role_skills.get("platform", {}).keys())
        
        # Calculate intersections
        technical_intersection = profile_technical & role_technical
        soft_intersection = profile_soft & role_soft
        platform_intersection = profile_platform & role_platform
        
        # Generate Venn diagram data
        venn_data = {
            "profile_only": {
                "technical": list(profile_technical - role_technical),
                "soft": list(profile_soft - role_soft),
                "platform": list(profile_platform - role_platform)
            },
            "role_only": {
                "technical": list(role_technical - profile_technical),
                "soft": list(role_soft - profile_soft),
                "platform": list(role_platform - profile_platform)
            },
            "intersection": {
                "technical": list(technical_intersection),
                "soft": list(soft_intersection),
                "platform": list(platform_intersection)
            },
            "counts": {
                "profile_only_count": len(profile_technical - role_technical) + len(profile_soft - role_soft) + len(profile_platform - role_platform),
                "role_only_count": len(role_technical - profile_technical) + len(role_soft - profile_soft) + len(role_platform - profile_platform),
                "intersection_count": len(technical_intersection) + len(soft_intersection) + len(platform_intersection)
            }
        }
        
        return venn_data
    
    def generate_match_score_breakdown(self, match_id: str) -> Dict:
        """Generate data for match score visualization"""
        # Get match
        match = self.db.query(MatchResult).filter(
            MatchResult.match_id == match_id,
            MatchResult.tenant_id == self.tenant_id
        ).first()
        
        if not match:
            raise ValueError(f"Match not found: {match_id}")
        
        # Generate score breakdown
        score_breakdown = {
            "skill_overlap": {
                "value": match.skill_overlap,
                "label": "Skill Overlap",
                "description": "Alignment between profile skills and role requirements"
            },
            "aspiration_alignment": {
                "value": match.aspiration_alignment,
                "label": "Aspiration Alignment",
                "description": "Alignment between profile aspirations and role scope"
            },
            "availability_match": {
                "value": match.availability_match,
                "label": "Availability Match",
                "description": "Alignment between profile availability and role requirements"
            },
            "platform_match": {
                "value": match.platform_match,
                "label": "Platform Match",
                "description": "Alignment between platform preferences and role requirements"
            },
            "overall_score": {
                "value": match.overall_score,
                "label": "Overall Score",
                "description": "Weighted average of all component scores"
            }
        }
        
        return score_breakdown
    
    def generate_confidence_evidence_quality_data(self, match_id: str) -> Dict:
        """Generate data for confidence and evidence quality visualization"""
        # Get match
        match = self.db.query(MatchResult).filter(
            MatchResult.match_id == match_id,
            MatchResult.tenant_id == self.tenant_id
        ).first()
        
        if not match:
            raise ValueError(f"Match not found: {match_id}")
        
        # Generate confidence and evidence quality data
        confidence_data = {
            "confidence": {
                "value": match.confidence,
                "label": "Confidence",
                "description": "Level of confidence in the match",
                "levels": ["low", "medium", "high"]
            },
            "evidence_quality": {
                "value": match.evidence_quality,
                "label": "Evidence Quality",
                "description": "Quality of evidence supporting the match",
                "levels": ["unverified", "self_reported", "verified"]
            },
            "evidence_sources": {
                "value": match.evidence_sources,
                "label": "Evidence Sources",
                "description": "Sources of evidence for the match"
            }
        }
        
        return confidence_data
