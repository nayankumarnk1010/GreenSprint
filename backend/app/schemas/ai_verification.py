from datetime import datetime

from pydantic import BaseModel
from pydantic import Field

from app.core.enums import AIVerificationDecision
from app.core.enums import AIVerificationStatus
from app.schemas.fraud_check import FraudCheckResponse


class AIVerificationResponse(BaseModel):
    id: str
    submission_id: str
    media_id: str | None
    status: AIVerificationStatus
    decision: AIVerificationDecision | None
    confidence_score: float | None
    fraud_risk_score: float | None
    model_name: str
    summary: str | None
    result_json: dict | None
    error_message: str | None
    created_at: datetime
    completed_at: datetime | None

    model_config = {
        "from_attributes": True
    }


class AIVerificationDetailResponse(AIVerificationResponse):
    fraud_checks: list[FraudCheckResponse] = Field(default_factory=list)