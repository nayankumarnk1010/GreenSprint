from app.core.enums import (
    ChallengeCategory,
    ChallengeDifficulty,
    ChallengeType,
)

from app.schemas.challenge_ai import (
    ChallengeGenerationResponse,
)


class ChallengeAIService:

    @staticmethod
    def generate_challenge(
        goal: str,
    ) -> ChallengeGenerationResponse:

        goal_lower = goal.lower()

        if "plastic" in goal_lower:
            return ChallengeGenerationResponse(
                title="Plastic-Free Campus Week",
                description=(
                    "Avoid single-use plastics for seven days "
                    "and encourage sustainable alternatives."
                ),
                category=ChallengeCategory.RECYCLING,
                challenge_type=ChallengeType.COMMUNITY,
                difficulty=ChallengeDifficulty.MEDIUM,
                points=500,
                target_value=100,
                duration_days=7,
            )

        if "tree" in goal_lower:
            return ChallengeGenerationResponse(
                title="Tree Plantation Drive",
                description=(
                    "Plant trees in your locality and "
                    "promote environmental sustainability."
                ),
                category=ChallengeCategory.TREE_PLANTATION,
                challenge_type=ChallengeType.COMMUNITY,
                difficulty=ChallengeDifficulty.MEDIUM,
                points=700,
                target_value=50,
                duration_days=30,
            )

        if "water" in goal_lower:
            return ChallengeGenerationResponse(
                title="Water Conservation Week",
                description=(
                    "Reduce water consumption and adopt "
                    "water-saving habits."
                ),
                category=ChallengeCategory.WATER_CONSERVATION,
                challenge_type=ChallengeType.SOLO,
                difficulty=ChallengeDifficulty.EASY,
                points=300,
                target_value=7,
                duration_days=7,
            )

        return ChallengeGenerationResponse(
            title="Green Impact Challenge",
            description=(
                "Take sustainability-focused actions "
                "and contribute to a greener future."
            ),
            category=ChallengeCategory.COMMUNITY_SERVICE,
            challenge_type=ChallengeType.SOLO,
            difficulty=ChallengeDifficulty.MEDIUM,
            points=200,
            target_value=10,
            duration_days=14,
        )