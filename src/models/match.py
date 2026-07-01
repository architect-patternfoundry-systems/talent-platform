"""Match Result model"""
from sqlalchemy import Column, String, DateTime, JSON, Float
from sqlalchemy.sql import func
from src.core.database import Base


class MatchResult(Base):
    """Match Result model"""
    
    __tablename__ = "match_results"
    
    # Primary key
    match_id = Column(String, primary_key=True)
    
    # Tenant context
    tenant_id = Column(String, nullable=False)
    
    # Schema version
    schema_version = Column(String, nullable=False, default="1.0")
    
    # Foreign keys
    profile_id = Column(String, nullable=False)
    role_id = Column(String, nullable=False)
    
    # Match scores
    skill_overlap = Column(Float, nullable=False)
    aspiration_alignment = Column(Float, nullable=False)
    availability_match = Column(Float, nullable=False)
    platform_match = Column(Float, nullable=False)
    overall_score = Column(Float, nullable=False)
    
    # Human exception alignment
    human_exception_alignment = Column(Float, nullable=False)
    human_exception_rationale = Column(String, nullable=True)
    
    # Confidence and evidence
    confidence = Column(String, nullable=False)  # "high" | "medium" | "low"
    evidence_quality = Column(String, nullable=False)  # "verified" | "self_reported" | "unverified"
    
    # Override fields
    override_reason = Column(String, nullable=True)
    override_author = Column(String, nullable=True)
    override_timestamp = Column(DateTime(timezone=True), nullable=True)
    original_score = Column(Float, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
