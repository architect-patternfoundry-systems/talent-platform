"""Personal Profile model"""
from sqlalchemy import Column, String, DateTime, JSON
from sqlalchemy.sql import func
from src.core.database import Base


class PersonalProfile(Base):
    """Personal Profile model"""
    
    __tablename__ = "personal_profiles"
    
    # Primary key
    profile_id = Column(String, primary_key=True)
    
    # Tenant context
    tenant_id = Column(String, nullable=False)
    
    # Schema version
    schema_version = Column(String, nullable=False, default="1.0")
    
    # Basic fields
    name = Column(String, nullable=False)
    
    # Skills (JSONB)
    skills = Column(JSON, nullable=False)
    
    # Aspirations (JSONB)
    aspirations = Column(JSON, nullable=False)
    
    # Experience (JSONB)
    experience = Column(JSON, nullable=False)
    
    # Availability (JSONB)
    availability = Column(JSON, nullable=False)
    
    # Platform preferences (JSONB)
    platform_preferences = Column(JSON, nullable=False)
    
    # Human exception
    human_exception = Column(String, nullable=False)
    
    # Confidence and evidence
    confidence = Column(String, nullable=False)  # "high" | "medium" | "low"
    evidence_quality = Column(String, nullable=False)  # "verified" | "self_reported" | "unverified"
    evidence_sources = Column(JSON, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
