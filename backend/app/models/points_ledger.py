import uuid
from datetime import datetime

from sqlalchemy import DateTime
from sqlalchemy import Enum
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import JSON
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy.sql import func
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from app.core.enums import PointsSourceType
from app.core.enums import PointsTransactionType
from app.db.base import Base


class PointsLedger(Base):
    __tablename__ = "points_ledger"

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

    submission_id: Mapped[str | None] = mapped_column(
        ForeignKey("submissions.id"),
        nullable=True,
        unique=True,
        index=True,
    )

    points: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    transaction_type: Mapped[PointsTransactionType] = mapped_column(
        Enum(
            PointsTransactionType,
            name="points_transaction_type",
            native_enum=False,
        ),
        nullable=False,
        index=True,
    )

    source_type: Mapped[PointsSourceType] = mapped_column(
        Enum(
            PointsSourceType,
            name="points_source_type",
            native_enum=False,
        ),
        nullable=False,
        index=True,
    )

    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    metadata_json: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )