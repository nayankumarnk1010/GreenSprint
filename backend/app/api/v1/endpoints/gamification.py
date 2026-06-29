from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import Query
from fastapi import status

from sqlalchemy.orm import Session

from app.api.dependencies.auth import get_current_user
from app.api.dependencies.rbac import require_role
from app.core.enums import UserRole
from app.db.dependencies import get_db
from app.models.submission import Submission
from app.models.user import User
from app.schemas.gamification import BadgeResponse
from app.schemas.gamification import GamificationAwardResponse
from app.schemas.gamification import LeaderboardEntryResponse
from app.schemas.gamification import UserBadgeResponse
from app.schemas.gamification import UserGamificationDetailResponse
from app.services.gamification_service import GamificationService
from app.services.submission_service import SubmissionService

router = APIRouter()


def _ensure_submission_access(
    submission: Submission,
    current_user: User,
) -> None:
    if current_user.role in {
        UserRole.ADMIN,
        UserRole.ORGANIZATION,
    }:
        return

    if submission.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to reward this submission",
        )


def _get_accessible_submission(
    db: Session,
    submission_id: str,
    current_user: User,
) -> Submission:
    submission = SubmissionService.get_submission_by_id(
        db=db,
        submission_id=submission_id,
    )

    if not submission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Submission not found",
        )

    _ensure_submission_access(
        submission=submission,
        current_user=current_user,
    )

    return submission


@router.post(
    "/submissions/{submission_id}/award",
    response_model=GamificationAwardResponse,
    status_code=status.HTTP_201_CREATED,
)
def award_submission_points(
    submission_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _get_accessible_submission(
        db=db,
        submission_id=submission_id,
        current_user=current_user,
    )

    try:
        return GamificationService.award_submission_points(
            db=db,
            submission_id=submission_id,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


@router.get(
    "/users/me",
    response_model=UserGamificationDetailResponse,
)
def get_my_gamification_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return GamificationService.get_user_detail(
        db=db,
        user_id=current_user.id,
    )


@router.get(
    "/badges",
    response_model=list[BadgeResponse],
)
def get_available_badges(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return GamificationService.get_all_badges(db=db)


@router.get(
    "/users/me/badges",
    response_model=list[UserBadgeResponse],
)
def get_my_badges(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return GamificationService.get_user_badges(
        db=db,
        user_id=current_user.id,
    )


@router.get(
    "/leaderboard",
    response_model=list[LeaderboardEntryResponse],
)
def get_leaderboard(
    limit: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return GamificationService.get_leaderboard(
        db=db,
        limit=limit,
    )


@router.get(
    "/admin/users/{user_id}",
    response_model=UserGamificationDetailResponse,
)
def get_user_gamification_profile_admin(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role(
            UserRole.ADMIN,
            UserRole.ORGANIZATION,
        )
    ),
):
    return GamificationService.get_user_detail(
        db=db,
        user_id=user_id,
    )