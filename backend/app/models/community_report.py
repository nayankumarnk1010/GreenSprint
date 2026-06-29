import uuid
from datetime import datetime

from sqlalchemy import DateTime
from sqlalchemy import Enum
from sqlalchemy import ForeignKey
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy import UniqueConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from app.core.enums import CommunityReportReason
from app.core.enums import CommunityReportStatus
from app.db.base import Base


class CommunityReport(Base):
    __tablename__ = "community_reports"

    __table_args__ = (
        UniqueConstraint(
            "post_id",
            "user_id",
            name="uq_community_report_post_user",
        ),
    )

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )

    post_id: Mapped[str] = mapped_column(
        ForeignKey("community_posts.id"),
        nullable=False,
        index=True,
    )

    user_id: Mapped[str] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )

    reason: Mapped[CommunityReportReason] = mapped_column(
        Enum(
            CommunityReportReason,
            name="community_report_reason",
            native_enum=False,
        ),
        nullable=False,
        index=True,
    )

    details: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    status: Mapped[CommunityReportStatus] = mapped_column(
        Enum(
            CommunityReportStatus,
            name="community_report_status",
            native_enum=False,
        ),
        nullable=False,
        default=CommunityReportStatus.PENDING,
        index=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        index=True,
    )

    reviewed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )