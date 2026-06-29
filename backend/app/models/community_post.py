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

from app.core.enums import CommunityPostStatus
from app.core.enums import CommunityPostType
from app.core.enums import CommunityPostVisibility
from app.db.base import Base


class CommunityPost(Base):
    __tablename__ = "community_posts"

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
        index=True,
    )

    challenge_id: Mapped[str | None] = mapped_column(
        ForeignKey("challenges.id"),
        nullable=True,
        index=True,
    )

    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    post_type: Mapped[CommunityPostType] = mapped_column(
        Enum(
            CommunityPostType,
            name="community_post_type",
            native_enum=False,
        ),
        nullable=False,
        default=CommunityPostType.GENERAL,
        index=True,
    )

    visibility: Mapped[CommunityPostVisibility] = mapped_column(
        Enum(
            CommunityPostVisibility,
            name="community_post_visibility",
            native_enum=False,
        ),
        nullable=False,
        default=CommunityPostVisibility.PUBLIC,
        index=True,
    )

    status: Mapped[CommunityPostStatus] = mapped_column(
        Enum(
            CommunityPostStatus,
            name="community_post_status",
            native_enum=False,
        ),
        nullable=False,
        default=CommunityPostStatus.ACTIVE,
        index=True,
    )

    likes_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    comments_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    reports_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
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