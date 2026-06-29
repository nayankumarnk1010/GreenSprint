from fastapi import APIRouter

from app.api.v1.endpoints import auth
from app.api.v1.endpoints import health
from app.api.v1.endpoints import users
from app.api.v1.endpoints import rbac_test
from app.api.v1.endpoints import challenges
from app.api.v1.endpoints import submissions
from app.api.v1.endpoints import ai_verification
from app.api.v1.endpoints import plant_health
from app.api.v1.endpoints import impact
from app.api.v1.endpoints import gamification
from app.api.v1.endpoints import analytics
from app.api.v1.endpoints import maps
from app.api.v1.endpoints import community
from app.api.v1.endpoints import organizations
from app.api.v1.endpoints import notifications
from app.api.v1.endpoints import esg
from app.api.v1.endpoints import admin
from app.api.v1.endpoints import system
from app.api.v1.endpoints import ai_assistant
from app.api.v1.endpoints import ai_vision
from app.api.v1.endpoints import plant_ai

api_router = APIRouter()

api_router.include_router(
    health.router,
    tags=["Health"],
)

api_router.include_router(
    auth.router,
)

api_router.include_router(
    users.router,
)

api_router.include_router(
    rbac_test.router,
)

api_router.include_router(
    challenges.router,
    prefix="/challenges",
    tags=["Challenges"],
)

api_router.include_router(
    submissions.router,
    prefix="/submissions",
    tags=["Submissions"],
)

api_router.include_router(
    ai_verification.router,
    prefix="/ai-verification",
    tags=["AI Verification"],
)

api_router.include_router(
    plant_health.router,
    prefix="/plant-health",
    tags=["Plant Health"],
)

api_router.include_router(
    impact.router,
    prefix="/impact",
    tags=["Environmental Impact"],
)

api_router.include_router(
    gamification.router,
    prefix="/gamification",
    tags=["Gamification"],
)

api_router.include_router(
    analytics.router,
    prefix="/analytics",
    tags=["Analytics"],
)

api_router.include_router(
    maps.router,
    prefix="/maps",
    tags=["Geospatial Maps"],
)

api_router.include_router(
    community.router,
    prefix="/community",
    tags=["Community"],
)


api_router.include_router(
    organizations.router,
    prefix="/organizations",
    tags=["Organizations & Campaigns"],
)

api_router.include_router(
    notifications.router,
    prefix="/notifications",
    tags=["Notifications"],
)

api_router.include_router(
    esg.router,
    prefix="/esg",
    tags=["ESG Reporting"],
)

api_router.include_router(
    admin.router,
    prefix="/admin",
    tags=["Admin Platform Control"],
)

api_router.include_router(
    system.router,
    prefix="/system",
    tags=["System Health"],
)

api_router.include_router(
    ai_assistant.router,
    prefix="/ai-assistant",
    tags=["AI Assistant"],
)

api_router.include_router(
    ai_vision.router,
    prefix="/ai-vision",
    tags=["AI Vision"],
)

api_router.include_router(
    plant_ai.router,
    prefix="/plant-ai",
    tags=["Plant AI"],
)