from datetime import datetime
from datetime import timezone

from sqlalchemy.orm import Session

from app.core.enums import SubmissionStatus
from app.models.challenge import Challenge
from app.models.submission import Submission
from app.schemas.submission import SubmissionCreate


class SubmissionService:

    @staticmethod
    def create_submission(
        db: Session,
        submission_data: SubmissionCreate,
        user_id: str,
    ) -> Submission:

        if submission_data.challenge_id:
            challenge = (
                db.query(Challenge)
                .filter(Challenge.id == submission_data.challenge_id)
                .first()
            )

            if not challenge:
                raise ValueError("Challenge not found")

        submission = Submission(
            **submission_data.model_dump(),
            user_id=user_id,
            status=SubmissionStatus.PENDING,
        )

        db.add(submission)
        db.commit()
        db.refresh(submission)

        return submission

    @staticmethod
    def get_submission_by_id(
        db: Session,
        submission_id: str,
    ) -> Submission | None:
        return (
            db.query(Submission)
            .filter(Submission.id == submission_id)
            .first()
        )

    @staticmethod
    def get_user_submissions(
        db: Session,
        user_id: str,
    ) -> list[Submission]:
        return (
            db.query(Submission)
            .filter(Submission.user_id == user_id)
            .order_by(Submission.submitted_at.desc())
            .all()
        )

    @staticmethod
    def get_review_queue(
        db: Session,
    ) -> list[Submission]:
        return (
            db.query(Submission)
            .filter(
                Submission.status.in_(
                    [
                        SubmissionStatus.PENDING,
                        SubmissionStatus.MANUAL_REVIEW,
                        SubmissionStatus.AI_REVIEWING,
                    ]
                )
            )
            .order_by(Submission.submitted_at.asc())
            .all()
        )

    @staticmethod
    def update_submission_status(
        db: Session,
        submission_id: str,
        status: SubmissionStatus,
        admin_review_note: str | None = None,
    ) -> Submission:
        submission = SubmissionService.get_submission_by_id(
            db=db,
            submission_id=submission_id,
        )

        if not submission:
            raise ValueError("Submission not found")

        submission.status = status
        submission.admin_review_note = admin_review_note

        if status in {
            SubmissionStatus.APPROVED,
            SubmissionStatus.REJECTED,
            SubmissionStatus.AI_VERIFIED,
            SubmissionStatus.AI_REJECTED,
        }:
            submission.reviewed_at = datetime.now(timezone.utc)

        db.commit()
        db.refresh(submission)

        return submission
