import uuid
from datetime import datetime

from sqlalchemy import DateTime
from sqlalchemy import Float
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.sql import func
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from app.db.base import Base


class UserGamificationProfile(Base):
    __tablename__ = "user_gamification_profiles"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )

    user_id: Mapped[str] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
        unique=True,
        index=True,
    )

    total_points: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    current_level: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=1,
    )

    green_reputation_score: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
    )

    total_badges: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    impact_actions_rewarded: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    ai_verified_actions: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    approved_actions: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    rejected_actions: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )