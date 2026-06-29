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
from app.schemas.ai_verification import AIVerificationDetailResponse
from app.services.ai_verification_service import AIVerificationService
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
            detail="You do not have permission to access this verification",
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
    "/submissions/{submission_id}/run",
    response_model=AIVerificationDetailResponse,
    status_code=status.HTTP_201_CREATED,
)
def run_submission_verification(
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
        return AIVerificationService.run_submission_verification(
            db=db,
            submission_id=submission_id,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.get(
    "/submissions/{submission_id}/latest",
    response_model=AIVerificationDetailResponse,
)
def get_latest_submission_verification(
    submission_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _get_accessible_submission(
        db=db,
        submission_id=submission_id,
        current_user=current_user,
    )

    verification = AIVerificationService.get_latest_submission_verification(
        db=db,
        submission_id=submission_id,
    )

    if not verification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Verification not found",
        )

    return verification


@router.get(
    "/admin/manual-review",
    response_model=list[AIVerificationDetailResponse],
)
def get_ai_manual_review_queue(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role(
            UserRole.ADMIN,
            UserRole.ORGANIZATION,
        )
    ),
):
    return AIVerificationService.get_manual_review_queue(db=db)


@router.get(
    "/{verification_id}",
    response_model=AIVerificationDetailResponse,
)
def get_verification_detail(
    verification_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    verification = AIVerificationService.get_verification_detail(
        db=db,
        verification_id=verification_id,
    )

    if not verification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Verification not found",
        )

    _get_accessible_submission(
        db=db,
        submission_id=verification["submission_id"],
        current_user=current_user,
    )

    return verification