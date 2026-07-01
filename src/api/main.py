"""Main application entry point"""
from fastapi import FastAPI
from fastapi.responses import JSONResponse

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
