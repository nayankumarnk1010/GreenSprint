from datetime import datetime
from typing import Any

from pydantic import BaseModel
from pydantic import Field


class SupportedLanguageResponse(BaseModel):
    code: str
    name: str
    native_name: str


class AIChatRequest(BaseModel):
    message: str = Field(..., min_length=2)
    language: str = "en"
    audio_enabled: bool = False


class AIChatResponse(BaseModel):
    answer: str
    language: str
    model_used: str
    response_source: str
    context_used: list[str]
    audio_url: str | None = None
    created_at: datetime


class AIChallengeGenerateRequest(BaseModel):
    prompt: str = Field(..., min_length=3)
    category: str | None = None
    difficulty: str | None = None
    language: str = "en"
    audio_enabled: bool = False


class AIChallengeGenerateResponse(BaseModel):
    title: str
    description: str
    category: str
    difficulty: str
    suggested_points: int
    rules: list[str]
    language: str
    model_used: str
    response_source: str
    audio_url: str | None = None
    created_at: datetime


class AIExplanationRequest(BaseModel):
    language: str = "en"
    audio_enabled: bool = False


class AIExplanationResponse(BaseModel):
    explanation: str
    language: str
    model_used: str
    response_source: str
    audio_url: str | None = None
    created_at: datetime


class AdminAIInsightRequest(BaseModel):
    language: str = "en"
    audio_enabled: bool = False


class AdminAIInsightResponse(BaseModel):
    insight: str
    recommendations: list[str]
    language: str
    model_used: str
    response_source: str
    audio_url: str | None = None
    platform_snapshot: dict[str, Any]
    created_at: datetime