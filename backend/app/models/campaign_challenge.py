import uuid
from datetime import datetime

from sqlalchemy import DateTime
from sqlalchemy import Enum
from sqlalchemy import ForeignKey
from sqlalchemy import String
from sqlalchemy import UniqueConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from app.core.enums import CampaignChallengeStatus
from app.db.base import Base


class CampaignChallenge(Base):
    __tablename__ = "campaign_challenges"

    __table_args__ = (
        UniqueConstraint(
            "campaign_id",
            "challenge_id",
            name="uq_campaign_challenge_campaign_challenge",
        ),
    )

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )

    campaign_id: Mapped[str] = mapped_column(
        ForeignKey("campaigns.id"),
        nullable=False,
        index=True,
    )

    challenge_id: Mapped[str] = mapped_column(
        ForeignKey("challenges.id"),
        nullable=False,
        index=True,
    )

    status: Mapped[CampaignChallengeStatus] = mapped_column(
        Enum(
            CampaignChallengeStatus,
            name="campaign_challenge_status",
            native_enum=False,
        ),
        nullable=False,
        default=CampaignChallengeStatus.ACTIVE,
        index=True,
    )

    added_by: Mapped[str] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )

    added_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        index=True,
    )