import uuid

from sqlalchemy import Boolean
from sqlalchemy import DateTime
from sqlalchemy import Enum
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy.sql import func
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from app.db.base import Base
from app.core.enums import (
    ChallengeCategory,
    ChallengeDifficulty,
    ChallengeStatus,
    ChallengeType,
)


class Challenge(Base):
    __tablename__ = "challenges"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )

    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    category: Mapped[ChallengeCategory] = mapped_column(
        Enum(
            ChallengeCategory,
            name="challenge_category",
            native_enum=False,
        ),
        nullable=False,
    )

    challenge_type: Mapped[ChallengeType] = mapped_column(
        Enum(
            ChallengeType,
            name="challenge_type",
            native_enum=False,
        ),
        nullable=False,
        default=ChallengeType.SOLO,
    )

    difficulty: Mapped[ChallengeDifficulty] = mapped_column(
        Enum(
            ChallengeDifficulty,
            name="challenge_difficulty",
            native_enum=False,
        ),
        nullable=False,
        default=ChallengeDifficulty.MEDIUM,
    )

    status: Mapped[ChallengeStatus] = mapped_column(
        Enum(
            ChallengeStatus,
            name="challenge_status",
            native_enum=False,
        ),
        nullable=False,
        default=ChallengeStatus.DRAFT,
    )

    points: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=100,
    )

    target_value: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=1,
    )

    duration_days: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=7,
    )

    ai_generated: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    created_by: Mapped[str] = mapped_column(
        String(36),
        nullable=False,
    )

    approved_by: Mapped[str | None] = mapped_column(
        String(36),
        nullable=True,
    )

    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )