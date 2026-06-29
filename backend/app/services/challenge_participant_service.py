from sqlalchemy.orm import Session

from app.models.challenge import Challenge
from app.models.challenge_participant import (
    ChallengeParticipant,
)


class ChallengeParticipantService:

    @staticmethod
    def join_challenge(
        db: Session,
        challenge_id: str,
        user_id: str,
    ):
        existing = (
            db.query(ChallengeParticipant)
            .filter(
                ChallengeParticipant.challenge_id
                == challenge_id,
                ChallengeParticipant.user_id
                == user_id,
            )
            .first()
        )

        if existing:
            return existing

        participant = ChallengeParticipant(
            challenge_id=challenge_id,
            user_id=user_id,
        )

        db.add(participant)

        db.commit()

        db.refresh(participant)

        return participant

    @staticmethod
    def get_user_challenges(
        db: Session,
        user_id: str,
    ):
        return (
            db.query(ChallengeParticipant)
            .filter(
                ChallengeParticipant.user_id
                == user_id
            )
            .all()
        )

    @staticmethod
    def update_progress(
        db: Session,
        challenge_id: str,
        user_id: str,
        progress: int,
    ):
        participant = (
            db.query(ChallengeParticipant)
            .filter(
                ChallengeParticipant.challenge_id
                == challenge_id,
                ChallengeParticipant.user_id
                == user_id,
            )
            .first()
        )

        if not participant:
            raise ValueError(
                "Challenge participation not found"
            )

        challenge = (
            db.query(Challenge)
            .filter(
                Challenge.id == challenge_id
            )
            .first()
        )

        if not challenge:
            raise ValueError(
                "Challenge not found"
            )

        # Clamp progress between 0 and 100
        progress = max(
            0,
            min(progress, 100),
        )

        participant.progress = progress

        if progress >= 100:
            participant.completed = True
            participant.points_awarded = (
                challenge.points
            )
        else:
            participant.completed = False
            participant.points_awarded = 0

        db.commit()

        db.refresh(participant)

        return participant