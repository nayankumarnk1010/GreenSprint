from sqlalchemy.orm import Session

from app.models.challenge import Challenge
from app.schemas.challenge import ChallengeCreate


class ChallengeService:

    @staticmethod
    def create_challenge(
        db: Session,
        challenge_data: ChallengeCreate,
        user_id: str,
    ) -> Challenge:

        challenge = Challenge(
            **challenge_data.model_dump(),
            created_by=user_id,
        )

        db.add(challenge)

        db.commit()

        db.refresh(challenge)

        return challenge

    @staticmethod
    def get_all_challenges(
        db: Session,
    ):
        return (
            db.query(Challenge)
            .all()
        )

    @staticmethod
    def get_challenge_by_id(
        db: Session,
        challenge_id: str,
    ):
        return (
            db.query(Challenge)
            .filter(
                Challenge.id == challenge_id
            )
            .first()
        )