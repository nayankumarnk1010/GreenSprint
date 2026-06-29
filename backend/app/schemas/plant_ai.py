from datetime import datetime
from typing import Any

from pydantic import BaseModel


class PlantTreatmentRecommendation(BaseModel):
    severity: str
    description: str
    organic_treatment: list[str]
    chemical_treatment: list[str]
    prevention: list[str]


class PlantDiseasePredictionResponse(BaseModel):
    predicted_class: str
    crop_name: str | None = None
    disease_name: str
    confidence_score: float
    confidence_level: str
    top_predictions: list[dict[str, Any]]
    treatment: PlantTreatmentRecommendation
    guide_answer: str
    query_answered: bool
    model_name: str
    model_source: str
    image_width: int
    image_height: int
    warning: str
    created_at: datetime


class PlantDiseaseModelHealthResponse(BaseModel):
    status: str
    model_available: bool
    class_names_available: bool
    classes_count: int
    model_path: str
    class_names_path: str
    message: str