"""
Main FastAPI application for OpenAI-compatible chat completions API.

This application provides a Databricks-compatible FastAPI service that exposes
an OpenAI-compatible chat completions endpoint.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.v1 import completions, healthcheck

app = FastAPI(
    title="Databricks OpenAI-Compatible API",
    description="OpenAI-compatible chat completions endpoint for Databricks",
    version="1.0.0",
)

# CORS configuration - allow all origins for development
# Restrict in production as needed
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers with /api/v1 prefix (required for Databricks OAuth2)
app.include_router(healthcheck.router, prefix="/api/v1", tags=["health"])
app.include_router(completions.router, prefix="/api/v1", tags=["completions"])


@app.get("/")
async def root():
    """
    Root endpoint providing basic API information.

    Returns:
        dict: API status and available endpoints
    """
    return {
        "message": "OpenAI-Compatible API Server",
        "status": "running",
        "docs": "/docs",
        "healthcheck": "/api/v1/healthcheck",
        "completions": "/api/v1/chat/completions",
    }
