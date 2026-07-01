"""Agent Definition model"""
from sqlalchemy import Column, String, DateTime, JSON
from sqlalchemy.sql import func
from src.core.database import Base


class AgentDefinition(Base):
    """Agent Definition model"""
    
    __tablename__ = "agent_definitions"
    
    # Primary key
    agent_id = Column(String, primary_key=True)
    
    # Schema version
    schema_version = Column(String, nullable=False, default="1.0")
    
    # Basic fields
    name = Column(String, nullable=False)
    agent_type = Column(String, nullable=False)
    
    # Skills, scope, boundaries (JSONB)
    skills = Column(JSON, nullable=False)
    scope = Column(JSON, nullable=False)
    boundaries = Column(JSON, nullable=False)
    
    # Platform configuration
    platform = Column(String, nullable=False)
    platform_config = Column(JSON, nullable=False)
    
    # Personality (JSONB)
    personality = Column(JSON, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
