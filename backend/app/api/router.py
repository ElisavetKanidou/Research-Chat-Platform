"""
Main API router for the Research Platform
"""
from fastapi import APIRouter

from app.api.v1.endpoints import auth, papers, chat, users, analytics, collaboration, notifications, websocket

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router, prefix="/v1/auth", tags=["authentication"])
api_router.include_router(papers.router, prefix="/v1/papers", tags=["papers"])
api_router.include_router(chat.router, prefix="/v1/chat", tags=["ai-chat"])
api_router.include_router(users.router, prefix="/v1/users", tags=["users"])
api_router.include_router(analytics.router, prefix="/v1/analytics", tags=["analytics"])
api_router.include_router(collaboration.router, prefix="/v1/collaborations", tags=["collaborations"])
api_router.include_router(notifications.router, prefix="/v1/notifications", tags=["notifications"])
api_router.include_router(websocket.router, prefix="/v1", tags=["websocket"])

# Health check endpoint
@api_router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "Research Platform API",
        "version": "1.0.0"
    }