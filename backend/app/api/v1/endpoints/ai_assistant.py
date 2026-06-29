from fastapi import APIRouter
from fastapi import Depends

from sqlalchemy.orm import Session

from app.api.dependencies.rbac import require_role
from app.core.enums import UserRole
from app.db.dependencies import get_db
from app.models.user import User
from app.schemas.ai_assistant import AdminAIInsightRequest
from app.schemas.ai_assistant import AdminAIInsightResponse
from app.schemas.ai_assistant import AIChallengeGenerateRequest
from app.schemas.ai_assistant import AIChallengeGenerateResponse
from app.schemas.ai_assistant import AIChatRequest
from app.schemas.ai_assistant import AIChatResponse
from app.schemas.ai_assistant import AIExplanationRequest
from app.schemas.ai_assistant import AIExplanationResponse
from app.schemas.ai_assistant import SupportedLanguageResponse
from app.services.ai.greensprint_ai_service import GreenSprintAIService


router = APIRouter()


@router.get(
    "/languages",
    response_model=list[SupportedLanguageResponse],
)
def supported_languages():
    return GreenSprintAIService.supported_languages()


@router.post(
    "/chat",
    response_model=AIChatResponse,
)
def chat(
    payload: AIChatRequest,
    current_user: User = Depends(
        require_role(
            UserRole.USER,
            UserRole.ORGANIZATION,
            UserRole.ADMIN,
        )
    ),
):
    return GreenSprintAIService.chat(
        message=payload.message,
        language=payload.language,
        audio_enabled=payload.audio_enabled,
    )


@router.post(
    "/challenges/generate",
    response_model=AIChallengeGenerateResponse,
)
def generate_challenge(
    payload: AIChallengeGenerateRequest,
    current_user: User = Depends(
        require_role(
            UserRole.ORGANIZATION,
            UserRole.ADMIN,
        )
    ),
):
    return GreenSprintAIService.generate_challenge(
        prompt=payload.prompt,
        category=payload.category,
        difficulty=payload.difficulty,
        language=payload.language,
        audio_enabled=payload.audio_enabled,
    )


@router.post(
    "/submissions/{submission_id}/impact/explain",
    response_model=AIExplanationResponse,
)
def explain_impact(
    submission_id: str,
    payload: AIExplanationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role(
            UserRole.USER,
            UserRole.ORGANIZATION,
            UserRole.ADMIN,
        )
    ),
):
    return GreenSprintAIService.explain_impact(
        db=db,
        submission_id=submission_id,
        language=payload.language,
        audio_enabled=payload.audio_enabled,
    )


@router.post(
    "/esg/reports/{report_id}/explain",
    response_model=AIExplanationResponse,
)
def explain_esg_report(
    report_id: str,
    payload: AIExplanationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role(
            UserRole.ORGANIZATION,
            UserRole.ADMIN,
        )
    ),
):
    return GreenSprintAIService.explain_esg_report(
        db=db,
        report_id=report_id,
        language=payload.language,
        audio_enabled=payload.audio_enabled,
    )


@router.post(
    "/admin/insights",
    response_model=AdminAIInsightResponse,
)
def admin_insights(
    payload: AdminAIInsightRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role(
            UserRole.ADMIN,
        )
    ),
):
    return GreenSprintAIService.admin_insights(
        db=db,
        language=payload.language,
        audio_enabled=payload.audio_enabled,
    )