"""Weight Configuration model"""
from sqlalchemy import Column, String, DateTime, Float
from sqlalchemy.sql import func
from src.core.database import Base


class WeightConfiguration(Base):
    """Weight Configuration model"""
    
    __tablename__ = "weight_configurations"
    
    # Primary key
    config_id = Column(String, primary_key=True)
    
    # Schema version
    schema_version = Column(String, nullable=False, default="1.0")
    
    # Scope
    scope = Column(String, nullable=False)  # "default" | "role" | "project" | "organization"
    scope_id = Column(String, nullable=True)
    
    # Weights
    skill_overlap_weight = Column(Float, nullable=False)
    aspiration_alignment_weight = Column(Float, nullable=False)
    availability_match_weight = Column(Float, nullable=False)
    platform_match_weight = Column(Float, nullable=False)
    
    # Approval
    approved_by = Column(String, nullable=False)
    approved_at = Column(DateTime(timezone=True), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
