from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException

from sqlalchemy.orm import Session

from app.api.dependencies.rbac import require_role
from app.core.enums import UserRole
from app.db.dependencies import get_db
from app.models.submission import Submission
from app.models.submission_media import SubmissionMedia
from app.models.user import User
from app.schemas.ai_vision import LocalVisionHealthResponse
from app.schemas.ai_vision import LocalVisionSubmissionAnalysisResponse
from app.services.ai.local_vision_service import LocalVisionService


router = APIRouter()


def _role_value(
    user: User,
) -> str:
    return str(
        getattr(
            user.role,
            "value",
            user.role,
        )
    )


@router.get(
    "/health",
    response_model=LocalVisionHealthResponse,
)
def health():
    return LocalVisionService.health()


@router.post(
    "/submissions/{submission_id}/analyze",
    response_model=LocalVisionSubmissionAnalysisResponse,
)
def analyze_submission_images(
    submission_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role(
            UserRole.USER,
            UserRole.ORGANIZATION,
            UserRole.ADMIN,
        )
    ),
):
    submission = (
        db.query(Submission)
        .filter(Submission.id == submission_id)
        .first()
    )

    if not submission:
        raise HTTPException(
            status_code=404,
            detail="Submission not found.",
        )

    if (
        _role_value(current_user) == UserRole.USER.value
        and str(submission.user_id) != str(current_user.id)
    ):
        raise HTTPException(
            status_code=403,
            detail="You can analyze only your own submissions.",
        )

    media_items = (
        db.query(SubmissionMedia)
        .filter(SubmissionMedia.submission_id == submission_id)
        .all()
    )

    if not media_items:
        raise HTTPException(
            status_code=404,
            detail="No media found for this submission.",
        )

    try:
        return LocalVisionService.analyze_submission_images(
            submission=submission,
            media_items=media_items,
        )

    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )