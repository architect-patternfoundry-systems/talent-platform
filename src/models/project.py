"""Project Definition model"""
from sqlalchemy import Column, String, DateTime, JSON
from sqlalchemy.sql import func
from src.core.database import Base


class ProjectDefinition(Base):
    """Project Definition model"""
    
    __tablename__ = "project_definitions"
    
    # Primary key
    project_id = Column(String, primary_key=True)
    
    # Tenant context
    tenant_id = Column(String, nullable=False)
    
    # Schema version
    schema_version = Column(String, nullable=False, default="1.0")
    
    # Basic fields
    name = Column(String, nullable=False)
    description = Column(String, nullable=False)
    
    # Phases (JSONB)
    phases = Column(JSON, nullable=False)
    
    # Roles (JSONB)
    roles = Column(JSON, nullable=False)
    
    # Agents (JSONB)
    agents = Column(JSON, nullable=False)
    
    # Platforms (JSONB)
    platforms = Column(JSON, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
