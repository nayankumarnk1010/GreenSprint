from fastapi import APIRouter
from fastapi import Depends
from fastapi import File
from fastapi import HTTPException
from fastapi import UploadFile
from fastapi import status

from sqlalchemy.orm import Session

from app.api.dependencies.auth import get_current_user
from app.api.dependencies.rbac import require_role
from app.core.enums import UserRole
from app.db.dependencies import get_db
from app.models.submission import Submission
from app.models.user import User
from app.schemas.submission import (
    SubmissionCreate,
    SubmissionResponse,
    SubmissionStatusUpdate,
)
from app.schemas.submission_media import SubmissionMediaResponse
from app.services.media_service import MediaService
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
            detail="You do not have permission to access this submission",
        )


@router.post(
    "/",
    response_model=SubmissionResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_submission(
    submission_data: SubmissionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return SubmissionService.create_submission(
            db=db,
            submission_data=submission_data,
            user_id=current_user.id,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.get(
    "/my",
    response_model=list[SubmissionResponse],
)
def get_my_submissions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return SubmissionService.get_user_submissions(
        db=db,
        user_id=current_user.id,
    )


@router.get(
    "/admin/review",
    response_model=list[SubmissionResponse],
)
def get_submission_review_queue(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role(
            UserRole.ADMIN,
            UserRole.ORGANIZATION,
        )
    ),
):
    return SubmissionService.get_review_queue(db=db)


@router.get(
    "/{submission_id}",
    response_model=SubmissionResponse,
)
def get_submission(
    submission_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
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
    "/{submission_id}/media",
    response_model=SubmissionMediaResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_submission_media(
    submission_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
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

    try:
        return await MediaService.save_submission_media(
            db=db,
            submission_id=submission_id,
            file=file,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


@router.patch(
    "/{submission_id}/status",
    response_model=SubmissionResponse,
)
def update_submission_status(
    submission_id: str,
    request: SubmissionStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role(
            UserRole.ADMIN,
            UserRole.ORGANIZATION,
        )
    ),
):
    try:
        return SubmissionService.update_submission_status(
            db=db,
            submission_id=submission_id,
            status=request.status,
            admin_review_note=request.admin_review_note,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
