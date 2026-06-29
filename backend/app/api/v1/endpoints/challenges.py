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

from app.schemas.challenge import (
    ChallengeCreate,
    ChallengeResponse,
)

from app.schemas.challenge_ai import (
    ChallengeGenerationRequest,
    ChallengeGenerationResponse,
)

from app.schemas.challenge_participant import (
    ChallengeJoinResponse,
    UserChallengeResponse,
)

from app.schemas.challenge_progress import (
    ChallengeProgressUpdate,
    ChallengeProgressResponse,
)

from app.services.challenge_service import (
    ChallengeService,
)

from app.services.challenge_ai_service import (
    ChallengeAIService,
)

from app.services.challenge_participant_service import (
    ChallengeParticipantService,
)

router = APIRouter()


@router.post(
    "/",
    response_model=ChallengeResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_challenge(
    challenge_data: ChallengeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role(
            UserRole.ADMIN,
            UserRole.ORGANIZATION,
        )
    ),
):
    challenge = ChallengeService.create_challenge(
        db=db,
        challenge_data=challenge_data,
        user_id=current_user.id,
    )

    return challenge


@router.get(
    "/",
    response_model=list[ChallengeResponse],
)
def get_challenges(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):
    return ChallengeService.get_all_challenges(
        db=db,
    )


@router.post(
    "/generate",
    response_model=ChallengeGenerationResponse,
)
def generate_challenge(
    request: ChallengeGenerationRequest,
    current_user: User = Depends(
        require_role(
            UserRole.ADMIN,
            UserRole.ORGANIZATION,
        )
    ),
):
    return ChallengeAIService.generate_challenge(
        goal=request.goal,
    )


@router.get(
    "/my",
    response_model=list[UserChallengeResponse],
)
def get_my_challenges(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):
    return (
        ChallengeParticipantService
        .get_user_challenges(
            db=db,
            user_id=current_user.id,
        )
    )


@router.post(
    "/{challenge_id}/join",
    response_model=ChallengeJoinResponse,
)
def join_challenge(
    challenge_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):
    return (
        ChallengeParticipantService
        .join_challenge(
            db=db,
            challenge_id=challenge_id,
            user_id=current_user.id,
        )
    )


@router.patch(
    "/{challenge_id}/progress",
    response_model=ChallengeProgressResponse,
)
def update_progress(
    challenge_id: str,
    request: ChallengeProgressUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):
    participant = (
        ChallengeParticipantService
        .update_progress(
            db=db,
            challenge_id=challenge_id,
            user_id=current_user.id,
            progress=request.progress,
        )
    )

    return {
        "challenge_id": challenge_id,
        "progress": participant.progress,
        "completed": participant.completed,
        "points_awarded": participant.points_awarded,
    }


@router.get(
    "/{challenge_id}",
    response_model=ChallengeResponse,
)
def get_challenge(
    challenge_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):
    challenge = (
        ChallengeService.get_challenge_by_id(
            db=db,
            challenge_id=challenge_id,
        )
    )

    if not challenge:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Challenge not found",
        )

    return challenge