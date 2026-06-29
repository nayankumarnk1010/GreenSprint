from datetime import datetime
from typing import Any

from pydantic import BaseModel


class LocalVisionImageAnalysisResponse(BaseModel):
    media_id: str
    file_name: str | None = None
    file_path: str
    width: int
    height: int
    blur_score: float
    brightness_score: float
    contrast_score: float
    green_ratio: float
    brown_ratio: float
    blue_ratio: float
    white_ratio: float
    gray_ratio: float
    edge_density: float
    quality_score: float
    relevance_score: float
    confidence_score: float
    detected_labels: list[str]
    decision: str
    explanation: str
    recommendations: list[str]


class LocalVisionSubmissionAnalysisResponse(BaseModel):
    submission_id: str
    submission_type: str
    images_analyzed: int
    final_decision: str
    final_relevance_score: float
    final_confidence_score: float
    analysis_summary: str
    analyses: list[LocalVisionImageAnalysisResponse]
    created_at: datetime


class LocalVisionHealthResponse(BaseModel):
    status: str
    opencv_available: bool
    message: str
    details: dict[str, Any]