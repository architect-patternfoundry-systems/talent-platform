"""Override Log model"""
from sqlalchemy import Column, String, DateTime, JSON
from sqlalchemy.sql import func
from src.core.database import Base


class OverrideLog(Base):
    """Override Log model"""
    
    __tablename__ = "override_logs"
    
    # Primary key
    override_id = Column(String, primary_key=True)
    
    # Schema version
    schema_version = Column(String, nullable=False, default="1.0")
    
    # Entity information
    entity_type = Column(String, nullable=False)  # "match" | "agent_config"
    entity_id = Column(String, nullable=False)
    
    # Override information
    override_reason = Column(String, nullable=False)
    override_author = Column(String, nullable=False)
    override_timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Values
    original_value = Column(JSON, nullable=False)
    override_value = Column(JSON, nullable=False)
    
    # Impact
    impact = Column(String, nullable=False)  # "increased" | "decreased" | "neutral"
    
    # Timestamp
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
