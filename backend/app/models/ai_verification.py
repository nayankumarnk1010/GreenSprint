import uuid

from sqlalchemy import DateTime
from sqlalchemy import Enum
from sqlalchemy import Float
from sqlalchemy import ForeignKey
from sqlalchemy import JSON
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy.sql import func
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from app.core.enums import AIVerificationDecision
from app.core.enums import AIVerificationStatus
from app.db.base import Base


class AIVerification(Base):
    __tablename__ = "ai_verifications"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )

    submission_id: Mapped[str] = mapped_column(
        ForeignKey("submissions.id"),
        nullable=False,
        index=True,
    )

    media_id: Mapped[str | None] = mapped_column(
        ForeignKey("submission_media.id"),
        nullable=True,
        index=True,
    )

    status: Mapped[AIVerificationStatus] = mapped_column(
        Enum(
            AIVerificationStatus,
            name="ai_verification_status",
            native_enum=False,
        ),
        nullable=False,
        default=AIVerificationStatus.QUEUED,
        index=True,
    )

    decision: Mapped[AIVerificationDecision | None] = mapped_column(
        Enum(
            AIVerificationDecision,
            name="ai_verification_decision",
            native_enum=False,
        ),
        nullable=True,
        index=True,
    )

    confidence_score: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    fraud_risk_score: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
        index=True,
    )

    model_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        default="local_fraud_rules_v1",
    )

    summary: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    result_json: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True,
    )

    error_message: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    completed_at: Mapped[DateTime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )