"""
Research Platform API - Main FastAPI Application
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import logging
from contextlib import asynccontextmanager

from app.api.router import api_router
from app.core.config import settings
from app.core.exceptions import ResearchPlatformException
from app.database.connection import engine
from app.database.session import DatabaseSession
from app.models.base import Base
from app.services.scheduler_service import scheduler_service
from app.services.presence_service import presence_service

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("Starting up Research Platform API...")

    # Create database tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    logger.info("Database tables created successfully")

    # Start scheduler for notifications and reports
    try:
        scheduler_service.start()
        logger.info("✅ Scheduler service started (weekly reports, deadline reminders, AI suggestions)")
    except Exception as e:
        logger.warning(f"⚠️ Scheduler service failed to start: {str(e)}")

    # Load recent user activity into presence cache
    try:
        async with DatabaseSession() as db:
            await presence_service.load_recent_activity(db)
        logger.info("✅ Presence cache loaded with recent user activity")
    except Exception as e:
        logger.warning(f"⚠️ Failed to load presence cache: {str(e)}")

    yield

    # Shutdown
    logger.info("Shutting down Research Platform API...")

    # Stop scheduler
    try:
        scheduler_service.stop()
        logger.info("⏹️ Scheduler service stopped")
    except Exception as e:
        logger.warning(f"⚠️ Scheduler service failed to stop: {str(e)}")


# Create FastAPI application
app = FastAPI(
    title="Research Platform API",
    description="Comprehensive academic research management platform with AI assistance",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)


# Global exception handler
@app.exception_handler(ResearchPlatformException)
async def research_platform_exception_handler(request: Request, exc: ResearchPlatformException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "code": exc.error_code,
                "message": exc.message,
                "details": exc.details
            },
            "timestamp": exc.timestamp.isoformat()
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred",
                "details": str(exc) if settings.DEBUG else None
            }
        }
    )


# Health check endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "Research Platform API",
        "version": "1.0.0"
    }


# Include API router
app.include_router(api_router, prefix="/api")

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="info"
    )