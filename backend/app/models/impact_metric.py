import uuid
from datetime import datetime

from sqlalchemy import DateTime
from sqlalchemy import Enum
from sqlalchemy import Float
from sqlalchemy import ForeignKey
from sqlalchemy import JSON
from sqlalchemy import String
from sqlalchemy.sql import func
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from app.core.enums import ImpactCalculationStatus
from app.core.enums import ImpactMetricType
from app.db.base import Base


class ImpactMetric(Base):
    __tablename__ = "impact_metrics"

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

    challenge_id: Mapped[str | None] = mapped_column(
        ForeignKey("challenges.id"),
        nullable=True,
        index=True,
    )

    submission_id: Mapped[str] = mapped_column(
        ForeignKey("submissions.id"),
        nullable=False,
        unique=True,
        index=True,
    )

    metric_type: Mapped[ImpactMetricType] = mapped_column(
        Enum(
            ImpactMetricType,
            name="impact_metric_type",
            native_enum=False,
        ),
        nullable=False,
        index=True,
    )

    calculation_status: Mapped[ImpactCalculationStatus] = mapped_column(
        Enum(
            ImpactCalculationStatus,
            name="impact_calculation_status",
            native_enum=False,
        ),
        nullable=False,
        default=ImpactCalculationStatus.ESTIMATED,
        index=True,
    )

    co2e_saved_kg: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
    )

    waste_diverted_kg: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
    )

    water_saved_liters: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
    )

    energy_saved_kwh: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
    )

    trees_planted: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
    )

    transport_distance_km: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
    )

    biodiversity_score: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
    )

    confidence_score: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.75,
    )

    calculation_method: Mapped[str] = mapped_column(
        String(120),
        nullable=False,
        default="local_impact_estimator_v1",
    )

    assumptions_json: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )