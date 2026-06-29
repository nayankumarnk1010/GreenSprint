from datetime import datetime

from pydantic import BaseModel

from app.core.enums import FraudCheckResult
from app.core.enums import FraudCheckType


class FraudCheckResponse(BaseModel):
    id: str
    verification_id: str
    check_type: FraudCheckType
    result: FraudCheckResult
    risk_score: float
    message: str | None
    details_json: dict | None
    created_at: datetime

    model_config = {
        "from_attributes": True
    }