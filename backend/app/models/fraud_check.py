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

from app.core.enums import FraudCheckResult
from app.core.enums import FraudCheckType
from app.db.base import Base


class FraudCheck(Base):
    __tablename__ = "fraud_checks"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )

    verification_id: Mapped[str] = mapped_column(
        ForeignKey("ai_verifications.id"),
        nullable=False,
        index=True,
    )

    check_type: Mapped[FraudCheckType] = mapped_column(
        Enum(
            FraudCheckType,
            name="fraud_check_type",
            native_enum=False,
        ),
        nullable=False,
        index=True,
    )

    result: Mapped[FraudCheckResult] = mapped_column(
        Enum(
            FraudCheckResult,
            name="fraud_check_result",
            native_enum=False,
        ),
        nullable=False,
        index=True,
    )

    risk_score: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
    )

    message: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    details_json: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True,
    )

    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )