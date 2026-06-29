from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import status

from sqlalchemy.orm import Session

from app.api.dependencies.auth import get_current_user
from app.api.dependencies.rbac import require_role
from app.core.enums import UserRole
from app.db.dependencies import get_db
from app.models.user import User
from app.schemas.analytics import AdminDashboardAnalyticsResponse
from app.schemas.analytics import AIAnalyticsResponse
from app.schemas.analytics import ChallengeAnalyticsResponse
from app.schemas.analytics import GamificationAnalyticsResponse
from app.schemas.analytics import PlantHealthAnalyticsResponse
from app.schemas.analytics import UserAnalyticsResponse
from app.services.analytics_service import AnalyticsService


router = APIRouter()


@router.get(
    "/users/me",
    response_model=UserAnalyticsResponse,
)
def get_my_analytics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return AnalyticsService.get_user_analytics(
        db=db,
        user_id=current_user.id,
    )


@router.get(
    "/challenges/{challenge_id}",
    response_model=ChallengeAnalyticsResponse,
)
def get_challenge_analytics(
    challenge_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return AnalyticsService.get_challenge_analytics(
            db=db,
            challenge_id=challenge_id,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.get(
    "/admin/dashboard",
    response_model=AdminDashboardAnalyticsResponse,
)
def get_admin_dashboard_analytics(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role(
            UserRole.ADMIN,
            UserRole.ORGANIZATION,
        )
    ),
):
    return AnalyticsService.get_admin_dashboard_analytics(db=db)


@router.get(
    "/admin/ai",
    response_model=AIAnalyticsResponse,
)
def get_ai_analytics(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role(
            UserRole.ADMIN,
            UserRole.ORGANIZATION,
        )
    ),
):
    return AnalyticsService.get_ai_analytics(db=db)


@router.get(
    "/admin/plant-health",
    response_model=PlantHealthAnalyticsResponse,
)
def get_plant_health_analytics(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role(
            UserRole.ADMIN,
            UserRole.ORGANIZATION,
        )
    ),
):
    return AnalyticsService.get_plant_health_analytics(db=db)


@router.get(
    "/admin/gamification",
    response_model=GamificationAnalyticsResponse,
)
def get_gamification_analytics(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role(
            UserRole.ADMIN,
            UserRole.ORGANIZATION,
        )
    ),
):
    return AnalyticsService.get_gamification_analytics(db=db)