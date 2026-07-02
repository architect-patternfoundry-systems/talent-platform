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


@app.get("/about")
async def about():
    """About page with TAO philosophy connection"""
    return JSONResponse(
        content={
            "name": "Talent and Agent Orchestration Platform",
            "acronym": "TAO",
            "version": "0.1.0",
            "philosophy": {
                "title": "The TAO Connection",
                "description": "Tao (or Dao) is a foundational concept in Chinese philosophy and religion. Literally translating to 'way,' 'path,' or 'principle', it represents the natural, unnameable flow of the universe.",
                "key_aspects": [
                    {
                        "aspect": "The Unknowable Source",
                        "description": "In Taoism, the Tao is considered the ultimate, formless origin of all existence. It is the driving force behind the continuous cycle of change in nature."
                    },
                    {
                        "aspect": "The Path of Harmony",
                        "description": "It signifies the ideal way of living, which involves going with the flow of life rather than forcing, controlling, or resisting it."
                    },
                    {
                        "aspect": "Action Through Inaction (Wu Wei)",
                        "description": "Translates to effortless action. It means acting in alignment with the natural rhythm of things, allowing tasks and life events to unfold without unnecessary struggle."
                    },
                    {
                        "aspect": "The 'Way' of a Craft",
                        "description": "In a broader context, 'tao' is often used to describe the mastery, method, or guiding principle of any specific art or activity."
                    }
                ],
                "platform_connection": {
                    "title": "TAO Platform Philosophy",
                    "description": "Our Talent and Agent Orchestration Platform embodies these principles through:",
                    "alignments": [
                        "Natural Flow: Orchestrating talent and agents in seamless harmony",
                        "Effortless Action: Enabling human-AI collaboration without unnecessary friction",
                        "Balance of Opposites: Finding the perfect equilibrium between human creativity and AI capability",
                        "The Way of Craft: Mastering the art of talent orchestration through intelligent systems"
                    ]
                },
                "everyday_application": "To live in accordance with the Tao means to quiet the ego, reduce personal resistance, and embrace a mindset of balance, simplicity, and flexibility.",
                "note": "In Philippine languages (Tagalog/Bisaya), 'tao' simply means 'person,' 'human,' or 'alive' - a beautiful reminder that at the center of all orchestration, we serve people."
            }
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
