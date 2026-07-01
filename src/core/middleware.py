"""Middleware for tenant context and authentication"""
from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from src.core.auth import verify_token
from src.core.tenant import set_tenant_context
from src.core.database import get_db


security = HTTPBearer()


async def tenant_context_middleware(request: Request, call_next):
    """Middleware to set tenant context from JWT token"""
    
    # Get authorization header
    authorization = request.headers.get("Authorization")
    
    if authorization:
        try:
            # Extract token
            scheme, token = authorization.split()
            if scheme.lower() != "bearer":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid authentication scheme"
                )
            
            # Verify token
            payload = verify_token(token)
            if payload is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token"
                )
            
            # Extract tenant_id from token
            tenant_id = payload.get("tenant_id")
            if tenant_id is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Tenant ID not found in token"
                )
            
            # Store tenant_id in request state for later use
            request.state.tenant_id = tenant_id
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Authentication error: {str(e)}"
            )
    
    # Process request
    response = await call_next(request)
    
    return response


def get_current_tenant_id(request: Request) -> str:
    """Get current tenant ID from request state"""
    tenant_id = getattr(request.state, "tenant_id", None)
    if tenant_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Tenant ID not found in request state"
        )
    return tenant_id


def get_db_with_tenant_context(request: Request):
    """Get database session with tenant context set"""
    db = next(get_db())
    try:
        tenant_id = get_current_tenant_id(request)
        set_tenant_context(db, tenant_id)
        yield db
    finally:
        db.close()
