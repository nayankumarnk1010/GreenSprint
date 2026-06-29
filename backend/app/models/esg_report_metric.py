import uuid
from datetime import datetime

from sqlalchemy import DateTime
from sqlalchemy import Enum
from sqlalchemy import Float
from sqlalchemy import ForeignKey
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy.sql import func
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from app.core.enums import ESGMetricCategory
from app.db.base import Base


class ESGReportMetric(Base):
    __tablename__ = "esg_report_metrics"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )

    report_id: Mapped[str] = mapped_column(
        ForeignKey("esg_reports.id"),
        nullable=False,
        index=True,
    )

    category: Mapped[ESGMetricCategory] = mapped_column(
        Enum(
            ESGMetricCategory,
            name="esg_metric_category",
            native_enum=False,
        ),
        nullable=False,
        index=True,
    )

    metric_key: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )

    metric_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    value_number: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    value_text: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    unit: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )