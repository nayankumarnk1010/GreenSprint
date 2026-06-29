from pydantic import BaseModel

from app.core.enums import (
    ChallengeCategory,
    ChallengeDifficulty,
    ChallengeType,
)


class ChallengeGenerationRequest(BaseModel):
    goal: str


class ChallengeGenerationResponse(BaseModel):
    title: str

    description: str

    category: ChallengeCategory

    challenge_type: ChallengeType

    difficulty: ChallengeDifficulty

    points: int

    target_value: int

    duration_days: int