from datetime import datetime
from typing import Any

from pydantic import BaseModel
from pydantic import ConfigDict

from app.core.enums import PlantDiagnosisStatus
from app.core.enums import PlantDiseaseSeverity
from app.core.enums import PlantRecommendationType


class PlantDiagnosisRequest(BaseModel):
    plant_name: str | None = None
    user_question: str | None = None


class PlantCareRecommendationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    diagnosis_id: str
    recommendation_type: PlantRecommendationType
    title: str
    description: str
    priority_order: int
    safety_note: str | None = None
    created_at: datetime


class PlantDiagnosisResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    submission_id: str
    media_id: str | None = None
    plant_name: str | None = None
    disease_name: str
    severity: PlantDiseaseSeverity
    status: PlantDiagnosisStatus
    confidence_score: float
    model_name: str
    symptoms_json: dict[str, Any] | None = None
    cure_summary: str | None = None
    prevention_tips: str | None = None
    raw_result_json: dict[str, Any] | None = None
    error_message: str | None = None
    created_at: datetime
    recommendations: list[PlantCareRecommendationResponse] = []