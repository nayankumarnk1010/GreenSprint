import uuid
from datetime import datetime

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

from app.core.enums import PlantDiagnosisStatus
from app.core.enums import PlantDiseaseSeverity
from app.db.base import Base


class PlantDiagnosis(Base):
    __tablename__ = "plant_diagnoses"

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

    submission_id: Mapped[str] = mapped_column(
        ForeignKey("submissions.id"),
        nullable=False,
        index=True,
    )

    media_id: Mapped[str] = mapped_column(
        ForeignKey("submission_media.id"),
        nullable=False,
        index=True,
    )

    plant_name: Mapped[str | None] = mapped_column(
        String(120),
        nullable=True,
    )

    disease_name: Mapped[str] = mapped_column(
        String(180),
        nullable=False,
        index=True,
    )

    severity: Mapped[PlantDiseaseSeverity] = mapped_column(
        Enum(
            PlantDiseaseSeverity,
            name="plant_disease_severity",
            native_enum=False,
        ),
        nullable=False,
        default=PlantDiseaseSeverity.LOW,
        index=True,
    )

    status: Mapped[PlantDiagnosisStatus] = mapped_column(
        Enum(
            PlantDiagnosisStatus,
            name="plant_diagnosis_status",
            native_enum=False,
        ),
        nullable=False,
        default=PlantDiagnosisStatus.COMPLETED,
        index=True,
    )

    confidence_score: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
    )

    model_name: Mapped[str] = mapped_column(
        String(120),
        nullable=False,
        default="local_plant_health_rules_v1",
    )

    symptoms_json: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True,
    )

    cure_summary: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    prevention_tips: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    raw_result_json: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True,
    )

    error_message: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )