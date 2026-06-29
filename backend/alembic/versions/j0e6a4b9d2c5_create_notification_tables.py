"""create notification tables

Revision ID: j0e6a4b9d2c5
Revises: i9d5f3a2c8b4
Create Date: 2026-06-24 00:00:00.000000

"""
from typing import Sequence
from typing import Union

from alembic import op
import sqlalchemy as sa


revision: str = "j0e6a4b9d2c5"
down_revision: Union[str, Sequence[str], None] = "i9d5f3a2c8b4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "notifications",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("user_id", sa.String(length=36), nullable=False),
        sa.Column("actor_user_id", sa.String(length=36), nullable=True),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column(
            "notification_type",
            sa.Enum(
                "GENERAL",
                "SYSTEM",
                "SUBMISSION_STATUS",
                "AI_VERIFICATION",
                "IMPACT_CALCULATED",
                "POINTS_AWARDED",
                "BADGE_EARNED",
                "CAMPAIGN_UPDATE",
                "COMMUNITY_INTERACTION",
                name="notification_type",
                native_enum=False,
            ),
            nullable=False,
        ),
        sa.Column(
            "status",
            sa.Enum(
                "UNREAD",
                "READ",
                "ARCHIVED",
                name="notification_status",
                native_enum=False,
            ),
            nullable=False,
        ),
        sa.Column(
            "priority",
            sa.Enum(
                "LOW",
                "NORMAL",
                "HIGH",
                "URGENT",
                name="notification_priority",
                native_enum=False,
            ),
            nullable=False,
        ),
        sa.Column(
            "reference_type",
            sa.Enum(
                "SYSTEM",
                "USER",
                "SUBMISSION",
                "CHALLENGE",
                "CAMPAIGN",
                "COMMUNITY_POST",
                "BADGE",
                name="notification_reference_type",
                native_enum=False,
            ),
            nullable=True,
        ),
        sa.Column("reference_id", sa.String(length=36), nullable=True),
        sa.Column("action_url", sa.String(length=500), nullable=True),
        sa.Column("metadata_json", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
        sa.Column("read_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["actor_user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        op.f("ix_notifications_actor_user_id"),
        "notifications",
        ["actor_user_id"],
        unique=False,
    )

    op.create_index(
        op.f("ix_notifications_created_at"),
        "notifications",
        ["created_at"],
        unique=False,
    )

    op.create_index(
        op.f("ix_notifications_notification_type"),
        "notifications",
        ["notification_type"],
        unique=False,
    )

    op.create_index(
        op.f("ix_notifications_priority"),
        "notifications",
        ["priority"],
        unique=False,
    )

    op.create_index(
        op.f("ix_notifications_reference_id"),
        "notifications",
        ["reference_id"],
        unique=False,
    )

    op.create_index(
        op.f("ix_notifications_reference_type"),
        "notifications",
        ["reference_type"],
        unique=False,
    )

    op.create_index(
        op.f("ix_notifications_status"),
        "notifications",
        ["status"],
        unique=False,
    )

    op.create_index(
        op.f("ix_notifications_user_id"),
        "notifications",
        ["user_id"],
        unique=False,
    )

    op.create_table(
        "notification_preferences",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("user_id", sa.String(length=36), nullable=False),
        sa.Column("in_app_enabled", sa.Boolean(), nullable=False),
        sa.Column("system_notifications", sa.Boolean(), nullable=False),
        sa.Column("submission_updates", sa.Boolean(), nullable=False),
        sa.Column("ai_verification_updates", sa.Boolean(), nullable=False),
        sa.Column("impact_updates", sa.Boolean(), nullable=False),
        sa.Column("reward_updates", sa.Boolean(), nullable=False),
        sa.Column("campaign_updates", sa.Boolean(), nullable=False),
        sa.Column("community_updates", sa.Boolean(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id"),
    )

    op.create_index(
        op.f("ix_notification_preferences_user_id"),
        "notification_preferences",
        ["user_id"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_notification_preferences_user_id"),
        table_name="notification_preferences",
    )
    op.drop_table("notification_preferences")

    op.drop_index(op.f("ix_notifications_user_id"), table_name="notifications")
    op.drop_index(op.f("ix_notifications_status"), table_name="notifications")
    op.drop_index(op.f("ix_notifications_reference_type"), table_name="notifications")
    op.drop_index(op.f("ix_notifications_reference_id"), table_name="notifications")
    op.drop_index(op.f("ix_notifications_priority"), table_name="notifications")
    op.drop_index(op.f("ix_notifications_notification_type"), table_name="notifications")
    op.drop_index(op.f("ix_notifications_created_at"), table_name="notifications")
    op.drop_index(op.f("ix_notifications_actor_user_id"), table_name="notifications")
    op.drop_table("notifications")