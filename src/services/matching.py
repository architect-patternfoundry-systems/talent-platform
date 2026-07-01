"""Matching service for calculating match scores between profiles and roles"""
from typing import Dict, List, Optional
from sqlalchemy.orm import Session
from src.models.role import RoleDefinition
from src.models.profile import PersonalProfile
from src.models.match import MatchResult
from src.models.weight import WeightConfiguration


class MatchingService:
    """Service for calculating match scores between profiles and roles"""
    
    def __init__(self, db: Session, tenant_id: str):
        self.db = db
        self.tenant_id = tenant_id
    
    def calculate_skill_overlap(self, profile_skills: Dict, role_skills: Dict) -> float:
        """Calculate skill overlap score between profile and role"""
        # Extract skill categories
        profile_technical = profile_skills.get("technical", {})
        profile_soft = profile_skills.get("soft", {})
        profile_platform = profile_skills.get("platform", {})
        
        role_technical = role_skills.get("technical", {})
        role_soft = role_skills.get("soft", {})
        role_platform = role_skills.get("platform", {})
        
        # Calculate overlap for each category
        technical_overlap = self._calculate_dict_overlap(profile_technical, role_technical)
        soft_overlap = self._calculate_dict_overlap(profile_soft, role_soft)
        platform_overlap = self._calculate_dict_overlap(profile_platform, role_platform)
        
        # Weighted average (equal weights for now)
        if (technical_overlap + soft_overlap + platform_overlap) == 0:
            return 0.0
        
        return (technical_overlap + soft_overlap + platform_overlap) / 3
    
    def _calculate_dict_overlap(self, dict1: Dict, dict2: Dict) -> float:
        """Calculate overlap between two dictionaries"""
        if not dict1 or not dict2:
            return 0.0
        
        # Calculate intersection and union
        keys1 = set(dict1.keys())
        keys2 = set(dict2.keys())
        
        intersection = keys1 & keys2
        union = keys1 | keys2
        
        if not union:
            return 0.0
        
        # Calculate Jaccard similarity
        jaccard = len(intersection) / len(union)
        
        # Calculate skill level match for overlapping skills
        level_match = 0.0
        if intersection:
            for key in intersection:
                level1 = dict1.get(key, "")
                level2 = dict2.get(key, "")
                level_match += self._calculate_level_match(level1, level2)
            level_match = level_match / len(intersection)
        
        # Combine Jaccard similarity and level match
        return (jaccard + level_match) / 2
    
    def _calculate_level_match(self, level1: str, level2: str) -> float:
        """Calculate match between skill levels"""
        level_mapping = {
            "beginner": 1,
            "intermediate": 2,
            "advanced": 3,
            "expert": 4
        }
        
        num1 = level_mapping.get(level1.lower(), 0)
        num2 = level_mapping.get(level2.lower(), 0)
        
        if num1 == 0 or num2 == 0:
            return 0.0
        
        # Calculate match (1.0 if profile meets or exceeds requirement)
        if num1 >= num2:
            return 1.0
        else:
            return num1 / num2
    
    def calculate_aspiration_alignment(self, profile_aspirations: Dict, role_scope: Dict) -> float:
        """Calculate aspiration alignment between profile and role"""
        # Extract interests and career goals
        interests = profile_aspirations.get("interests", [])
        career_goals = profile_aspirations.get("career_goals", [])
        preferred_work = profile_aspirations.get("preferred_work", [])
        
        # Extract role responsibilities
        responsibilities = role_scope.get("responsibilities", [])
        
        # Calculate alignment
        interest_alignment = self._calculate_list_alignment(interests, responsibilities)
        goal_alignment = self._calculate_list_alignment(career_goals, responsibilities)
        work_alignment = self._calculate_list_alignment(preferred_work, responsibilities)
        
        # Weighted average
        if (interest_alignment + goal_alignment + work_alignment) == 0:
            return 0.0
        
        return (interest_alignment + goal_alignment + work_alignment) / 3
    
    def _calculate_list_alignment(self, list1: List[str], list2: List[str]) -> float:
        """Calculate alignment between two lists"""
        if not list1 or not list2:
            return 0.0
        
        # Convert to lowercase for comparison
        list1_lower = [item.lower() for item in list1]
        list2_lower = [item.lower() for item in list2]
        
        # Calculate overlap
        set1 = set(list1_lower)
        set2 = set(list2_lower)
        
        intersection = set1 & set2
        union = set1 | set2
        
        if not union:
            return 0.0
        
        return len(intersection) / len(union)
    
    def calculate_availability_match(self, profile_availability: Dict, role_requirements: Dict) -> float:
        """Calculate availability match between profile and role"""
        # Extract hours per week
        profile_hours = profile_availability.get("hours_per_week", 0)
        
        # For now, return 1.0 if profile has availability, 0.0 otherwise
        # In a real implementation, this would check against role requirements
        if profile_hours > 0:
            return 1.0
        else:
            return 0.0
    
    def calculate_platform_match(self, profile_preferences: Dict, role_platform_requirements: Dict) -> float:
        """Calculate platform preference match between profile and role"""
        # Extract platform preferences
        profile_platforms = profile_preferences
        
        # Extract role platform requirements
        role_platforms = role_platform_requirements
        
        # Calculate match
        platform_match = self._calculate_dict_overlap(profile_platforms, role_platforms)
        
        return platform_match
    
    def calculate_overall_score(
        self,
        skill_overlap: float,
        aspiration_alignment: float,
        availability_match: float,
        platform_match: float,
        weights: Optional[Dict[str, float]] = None
    ) -> float:
        """Calculate overall match score using weights"""
        if weights is None:
            # Default weights
            weights = {
                "skill_overlap_weight": 0.4,
                "aspiration_alignment_weight": 0.3,
                "availability_match_weight": 0.2,
                "platform_match_weight": 0.1
            }
        
        overall_score = (
            skill_overlap * weights["skill_overlap_weight"] +
            aspiration_alignment * weights["aspiration_alignment_weight"] +
            availability_match * weights["availability_match_weight"] +
            platform_match * weights["platform_match_weight"]
        )
        
        return overall_score
    
    def calculate_human_exception_alignment(
        self,
        profile_human_exception: str,
        role_human_exception: str
    ) -> float:
        """Calculate human exception alignment (informational in v1)"""
        # For v1, this is informational only
        # In a real implementation, this would use embedding-based semantic similarity
        # For now, return a placeholder value
        return 0.5
    
    def get_weight_configuration(self, scope: str = "default", scope_id: Optional[str] = None) -> Dict[str, float]:
        """Get weight configuration for matching"""
        # Query weight configuration
        if scope_id:
            config = self.db.query(WeightConfiguration).filter(
                WeightConfiguration.scope == scope,
                WeightConfiguration.scope_id == scope_id,
                WeightConfiguration.tenant_id == self.tenant_id
            ).first()
        else:
            config = self.db.query(WeightConfiguration).filter(
                WeightConfiguration.scope == scope,
                WeightConfiguration.tenant_id == self.tenant_id
            ).first()
        
        if config:
            return {
                "skill_overlap_weight": config.skill_overlap_weight,
                "aspiration_alignment_weight": config.aspiration_alignment_weight,
                "availability_match_weight": config.availability_match_weight,
                "platform_match_weight": config.platform_match_weight
            }
        else:
            # Return default weights
            return {
                "skill_overlap_weight": 0.4,
                "aspiration_alignment_weight": 0.3,
                "availability_match_weight": 0.2,
                "platform_match_weight": 0.1
            }
    
    def calculate_match(
        self,
        profile_id: str,
        role_id: str,
        weights: Optional[Dict[str, float]] = None
    ) -> MatchResult:
        """Calculate match between profile and role"""
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
        
        # Calculate component scores
        skill_overlap = self.calculate_skill_overlap(profile.skills, role.skills)
        aspiration_alignment = self.calculate_aspiration_alignment(profile.aspirations, role.scope)
        availability_match = self.calculate_availability_match(profile.availability, role.platform_requirements)
        platform_match = self.calculate_platform_match(profile.platform_preferences, role.platform_requirements)
        
        # Get weights
        if weights is None:
            weights = self.get_weight_configuration()
        
        # Calculate overall score
        overall_score = self.calculate_overall_score(
            skill_overlap,
            aspiration_alignment,
            availability_match,
            platform_match,
            weights
        )
        
        # Calculate human exception alignment (informational in v1)
        human_exception_alignment = self.calculate_human_exception_alignment(
            profile.human_exception,
            role.human_exception
        )
        
        # Create match result
        import uuid
        match_id = f"match_{uuid.uuid4().hex[:8]}"
        
        match_result = MatchResult(
            match_id=match_id,
            tenant_id=self.tenant_id,
            schema_version="1.0",
            profile_id=profile_id,
            role_id=role_id,
            skill_overlap=skill_overlap,
            aspiration_alignment=aspiration_alignment,
            availability_match=availability_match,
            platform_match=platform_match,
            overall_score=overall_score,
            human_exception_alignment=human_exception_alignment,
            human_exception_rationale="Informational in v1",
            confidence=profile.confidence,
            evidence_quality=profile.evidence_quality
        )
        
        return match_result
