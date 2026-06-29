import uuid
from datetime import datetime

from sqlalchemy import Boolean
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import String
from sqlalchemy.sql import func
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from app.db.base import Base


class NotificationPreference(Base):
    __tablename__ = "notification_preferences"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )

    user_id: Mapped[str] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
        unique=True,
        index=True,
    )

    in_app_enabled: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
    )

    system_notifications: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
    )

    submission_updates: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
    )

    ai_verification_updates: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
    )

    impact_updates: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
    )

    reward_updates: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
    )

    campaign_updates: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
    )

    community_updates: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
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