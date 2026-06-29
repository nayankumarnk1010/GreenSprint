import uuid
from datetime import datetime

from sqlalchemy import DateTime
from sqlalchemy import Enum
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy.sql import func
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from app.core.enums import PlantRecommendationType
from app.db.base import Base


class PlantCareRecommendation(Base):
    __tablename__ = "plant_care_recommendations"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )

    diagnosis_id: Mapped[str] = mapped_column(
        ForeignKey("plant_diagnoses.id"),
        nullable=False,
        index=True,
    )

    recommendation_type: Mapped[PlantRecommendationType] = mapped_column(
        Enum(
            PlantRecommendationType,
            name="plant_recommendation_type",
            native_enum=False,
        ),
        nullable=False,
        index=True,
    )

    title: Mapped[str] = mapped_column(
        String(180),
        nullable=False,
    )

    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    priority_order: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=1,
    )

    safety_note: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )