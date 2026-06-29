import uuid
from datetime import datetime

from sqlalchemy import DateTime
from sqlalchemy import Enum
from sqlalchemy import Float
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.sql import func
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from app.core.enums import LeaderboardPeriod
from app.db.base import Base


class LeaderboardSnapshot(Base):
    __tablename__ = "leaderboard_snapshots"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )

    user_id: Mapped[str] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )

    period: Mapped[LeaderboardPeriod] = mapped_column(
        Enum(
            LeaderboardPeriod,
            name="leaderboard_period",
            native_enum=False,
        ),
        nullable=False,
        default=LeaderboardPeriod.ALL_TIME,
        index=True,
    )

    rank: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        index=True,
    )

    total_points: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    green_reputation_score: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
    )

    generated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        index=True,
    )