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


class ChallengeImpactSummary(Base):
    __tablename__ = "challenge_impact_summaries"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )

    challenge_id: Mapped[str] = mapped_column(
        ForeignKey("challenges.id"),
        nullable=False,
        unique=True,
        index=True,
    )

    total_co2e_saved_kg: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
    )

    total_waste_diverted_kg: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
    )

    total_water_saved_liters: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
    )

    total_energy_saved_kwh: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
    )

    total_trees_planted: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
    )

    total_transport_distance_km: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
    )

    total_biodiversity_score: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
    )

    impact_actions_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )