"""Tenant context management"""
from sqlalchemy import event
from sqlalchemy.orm import Session
from src.core.config import settings


def set_tenant_context(db: Session, tenant_id: str):
    """Set tenant context for the current database session"""
    db.execute(f"SET LOCAL app.current_tenant_id = '{tenant_id}'")


def get_tenant_context(db: Session) -> str:
    """Get tenant context for the current database session"""
    result = db.execute("SELECT current_setting('app.current_tenant_id', true)")
    return result.scalar() or None


def clear_tenant_context(db: Session):
    """Clear tenant context for the current database session"""
    db.execute("RESET app.current_tenant_id")
