import uuid
from datetime import datetime

from sqlalchemy import DateTime
from sqlalchemy import Enum
from sqlalchemy import ForeignKey
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy.sql import func
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from app.core.enums import ESGReportStatus
from app.core.enums import ESGReportType
from app.db.base import Base


class ESGReport(Base):
    __tablename__ = "esg_reports"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )

    organization_id: Mapped[str] = mapped_column(
        ForeignKey("organization_profiles.id"),
        nullable=False,
        index=True,
    )

    campaign_id: Mapped[str | None] = mapped_column(
        ForeignKey("campaigns.id"),
        nullable=True,
        index=True,
    )

    created_by: Mapped[str] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )

    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    report_type: Mapped[ESGReportType] = mapped_column(
        Enum(
            ESGReportType,
            name="esg_report_type",
            native_enum=False,
        ),
        nullable=False,
        index=True,
    )

    status: Mapped[ESGReportStatus] = mapped_column(
        Enum(
            ESGReportStatus,
            name="esg_report_status",
            native_enum=False,
        ),
        nullable=False,
        default=ESGReportStatus.GENERATED,
        index=True,
    )

    period_start: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True,
    )

    period_end: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True,
    )

    summary_json: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    published_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        index=True,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )