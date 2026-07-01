"""Main application entry point"""
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from src.core.database import get_db

app = FastAPI(
    title="Talent and Agent Orchestration Platform",
    description="Human-centered talent matching system with people operations and agent governance",
    version="0.1.0",
)


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
