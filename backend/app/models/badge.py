import uuid
from datetime import datetime

from sqlalchemy import Boolean
from sqlalchemy import DateTime
from sqlalchemy import Enum
from sqlalchemy import Integer
from sqlalchemy import JSON
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy.sql import func
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from app.core.enums import BadgeCategory
from app.db.base import Base


class Badge(Base):
    __tablename__ = "badges"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )

    code: Mapped[str] = mapped_column(
        String(80),
        nullable=False,
        unique=True,
        index=True,
    )

    name: Mapped[str] = mapped_column(
        String(120),
        nullable=False,
    )

    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    category: Mapped[BadgeCategory] = mapped_column(
        Enum(
            BadgeCategory,
            name="badge_category",
            native_enum=False,
        ),
        nullable=False,
        index=True,
    )

    points_threshold: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    badge_points_bonus: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    requirements_json: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        index=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )