from datetime import datetime

from pydantic import BaseModel
from pydantic import Field

from app.core.enums import BadgeCategory
from app.core.enums import PointsSourceType
from app.core.enums import PointsTransactionType


class BadgeResponse(BaseModel):
    id: str
    code: str
    name: str
    description: str
    category: BadgeCategory
    points_threshold: int
    badge_points_bonus: int
    requirements_json: dict | None
    is_active: bool
    created_at: datetime

    model_config = {
        "from_attributes": True
    }


class UserBadgeResponse(BaseModel):
    id: str
    user_id: str
    badge_id: str
    awarded_from_submission_id: str | None
    awarded_at: datetime
    badge: BadgeResponse | None = None

    model_config = {
        "from_attributes": True
    }


class PointsLedgerResponse(BaseModel):
    id: str
    user_id: str
    submission_id: str | None
    points: int
    transaction_type: PointsTransactionType
    source_type: PointsSourceType
    description: str
    metadata_json: dict | None
    created_at: datetime

    model_config = {
        "from_attributes": True
    }


class UserGamificationProfileResponse(BaseModel):
    id: str
    user_id: str
    total_points: int
    current_level: int
    green_reputation_score: float
    total_badges: int
    impact_actions_rewarded: int
    ai_verified_actions: int
    approved_actions: int
    rejected_actions: int
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }


class GamificationAwardResponse(BaseModel):
    profile: UserGamificationProfileResponse
    ledger_entry: PointsLedgerResponse
    badges_awarded: list[BadgeResponse] = Field(default_factory=list)
    message: str


class LeaderboardEntryResponse(BaseModel):
    rank: int
    user_id: str
    full_name: str | None
    total_points: int
    current_level: int
    green_reputation_score: float
    total_badges: int
    impact_actions_rewarded: int


class UserGamificationDetailResponse(BaseModel):
    profile: UserGamificationProfileResponse
    badges: list[BadgeResponse] = Field(default_factory=list)
    recent_points: list[PointsLedgerResponse] = Field(default_factory=list)