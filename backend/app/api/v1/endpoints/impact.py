from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import status

from sqlalchemy.orm import Session

from app.api.dependencies.auth import get_current_user
from app.api.dependencies.rbac import require_role
from app.core.enums import UserRole
from app.db.dependencies import get_db
from app.models.submission import Submission
from app.models.user import User
from app.schemas.impact import ChallengeImpactSummaryResponse
from app.schemas.impact import ImpactMetricResponse
from app.schemas.impact import PlatformImpactSummaryResponse
from app.schemas.impact import UserImpactSummaryResponse
from app.services.impact_service import ImpactService
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
            detail="You do not have permission to access this impact record",
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
    "/submissions/{submission_id}/calculate",
    response_model=ImpactMetricResponse,
    status_code=status.HTTP_201_CREATED,
)
def calculate_submission_impact(
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
        return ImpactService.calculate_submission_impact(
            db=db,
            submission_id=submission_id,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.get(
    "/submissions/{submission_id}",
    response_model=ImpactMetricResponse,
)
def get_submission_impact(
    submission_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _get_accessible_submission(
        db=db,
        submission_id=submission_id,
        current_user=current_user,
    )

    impact = ImpactService.get_submission_impact(
        db=db,
        submission_id=submission_id,
    )

    if not impact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Impact metric not found for this submission",
        )

    return impact


@router.get(
    "/users/me",
    response_model=UserImpactSummaryResponse,
)
def get_my_impact_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return ImpactService.get_user_summary(
        db=db,
        user_id=current_user.id,
    )


@router.get(
    "/challenges/{challenge_id}",
    response_model=ChallengeImpactSummaryResponse,
)
def get_challenge_impact_summary(
    challenge_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return ImpactService.get_challenge_summary(
            db=db,
            challenge_id=challenge_id,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.get(
    "/platform-summary",
    response_model=PlatformImpactSummaryResponse,
)
def get_platform_impact_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role(
            UserRole.ADMIN,
            UserRole.ORGANIZATION,
        )
    ),
):
    return ImpactService.get_platform_summary(db=db)