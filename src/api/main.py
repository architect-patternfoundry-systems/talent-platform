"""Main application entry point"""
from fastapi import FastAPI, Request, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from src.core.database import get_db
from src.core.middleware import tenant_context_middleware, get_current_tenant_id, get_db_with_tenant_context
from src.core.auth import create_access_token
from src.api import roles, profiles, matching, visualization, recommendation, override, governance

app = FastAPI(
    title="Talent and Agent Orchestration Platform",
    description="Human-centered talent matching system with people operations and agent governance",
    version="0.1.0",
)

# Add tenant context middleware
app.middleware("http")(tenant_context_middleware)

# Include routers
app.include_router(roles.router)
app.include_router(profiles.router)
app.include_router(matching.router)
app.include_router(visualization.router)
app.include_router(recommendation.router)
app.include_router(override.router)
app.include_router(governance.router)


@app.get("/")
async def root():
    """Root endpoint"""
    return JSONResponse(
        content={
            "message": "Talent and Agent Orchestration Platform",
            "version": "0.1.0",
            "status": "operational"
        }
    )


@app.get("/health")
async def health():
    """Health check endpoint"""
    return JSONResponse(
        content={
            "status": "healthy"
        }
    )


@app.get("/db-health")
async def db_health():
    """Database health check endpoint"""
    try:
        from sqlalchemy import text
        db = next(get_db())
        db.execute(text("SELECT 1"))
        db.close()
        return JSONResponse(
            content={
                "status": "healthy",
                "database": "connected"
            }
        )
    except Exception as e:
        return JSONResponse(
            content={
                "status": "unhealthy",
                "database": "disconnected",
                "error": str(e)
            },
            status_code=503
        )


@app.get("/auth/token")
async def get_token(tenant_id: str = "default_tenant"):
    """Get test token (for development only)"""
    token_data = {
        "sub": "test_user",
        "tenant_id": tenant_id
    }
    token = create_access_token(token_data)
    return JSONResponse(
        content={
            "access_token": token,
            "token_type": "bearer",
            "tenant_id": tenant_id
        }
    )


@app.get("/auth/tenant")
async def get_tenant(request: Request):
    """Get current tenant from request state"""
    try:
        tenant_id = get_current_tenant_id(request)
        return JSONResponse(
            content={
                "tenant_id": tenant_id
            }
        )
    except HTTPException as e:
        return JSONResponse(
            content={
                "error": str(e.detail)
            },
            status_code=e.status_code
        )
