from pydantic import BaseModel
from pydantic import Field

from app.core.enums import (
    ChallengeCategory,
    ChallengeDifficulty,
    ChallengeStatus,
    ChallengeType,
)


class ChallengeCreate(BaseModel):
    title: str = Field(
        min_length=3,
        max_length=255,
    )

    description: str = Field(
        min_length=10,
    )

    category: ChallengeCategory

    challenge_type: ChallengeType = ChallengeType.SOLO

    difficulty: ChallengeDifficulty = ChallengeDifficulty.MEDIUM

    points: int = Field(
        ge=1,
        le=10000,
    )

    target_value: int = Field(
        ge=1,
    )

    duration_days: int = Field(
        ge=1,
        le=365,
    )


class ChallengeResponse(BaseModel):
    id: str

    title: str

    description: str

    category: ChallengeCategory

    challenge_type: ChallengeType

    difficulty: ChallengeDifficulty

    status: ChallengeStatus

    points: int

    target_value: int

    duration_days: int

    ai_generated: bool

    created_by: str

    approved_by: str | None

    model_config = {
        "from_attributes": True
    }