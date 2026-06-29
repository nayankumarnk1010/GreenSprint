"""create community tables

Revision ID: g7b2d9e4f6a1
Revises: f6a9c3d8e2b1
Create Date: 2026-06-19 00:00:00.000000

"""
from typing import Sequence
from typing import Union

from alembic import op
import sqlalchemy as sa


revision: str = "g7b2d9e4f6a1"
down_revision: Union[str, Sequence[str], None] = "f6a9c3d8e2b1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "community_posts",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("user_id", sa.String(length=36), nullable=False),
        sa.Column("submission_id", sa.String(length=36), nullable=True),
        sa.Column("challenge_id", sa.String(length=36), nullable=True),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column(
            "post_type",
            sa.Enum(
                "GENERAL",
                "SUBMISSION_SHARE",
                "CHALLENGE_UPDATE",
                "ACHIEVEMENT_SHARE",
                name="community_post_type",
                native_enum=False,
            ),
            nullable=False,
        ),
        sa.Column(
            "visibility",
            sa.Enum(
                "PUBLIC",
                "CHALLENGE_ONLY",
                "PRIVATE",
                name="community_post_visibility",
                native_enum=False,
            ),
            nullable=False,
        ),
        sa.Column(
            "status",
            sa.Enum(
                "ACTIVE",
                "HIDDEN",
                "DELETED",
                name="community_post_status",
                native_enum=False,
            ),
            nullable=False,
        ),
        sa.Column("likes_count", sa.Integer(), nullable=False),
        sa.Column("comments_count", sa.Integer(), nullable=False),
        sa.Column("reports_count", sa.Integer(), nullable=False),
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
        sa.ForeignKeyConstraint(["challenge_id"], ["challenges.id"]),
        sa.ForeignKeyConstraint(["submission_id"], ["submissions.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        op.f("ix_community_posts_challenge_id"),
        "community_posts",
        ["challenge_id"],
        unique=False,
    )

    op.create_index(
        op.f("ix_community_posts_created_at"),
        "community_posts",
        ["created_at"],
        unique=False,
    )

    op.create_index(
        op.f("ix_community_posts_post_type"),
        "community_posts",
        ["post_type"],
        unique=False,
    )

    op.create_index(
        op.f("ix_community_posts_status"),
        "community_posts",
        ["status"],
        unique=False,
    )

    op.create_index(
        op.f("ix_community_posts_submission_id"),
        "community_posts",
        ["submission_id"],
        unique=False,
    )

    op.create_index(
        op.f("ix_community_posts_user_id"),
        "community_posts",
        ["user_id"],
        unique=False,
    )

    op.create_index(
        op.f("ix_community_posts_visibility"),
        "community_posts",
        ["visibility"],
        unique=False,
    )

    op.create_table(
        "community_comments",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("post_id", sa.String(length=36), nullable=False),
        sa.Column("user_id", sa.String(length=36), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column(
            "status",
            sa.Enum(
                "ACTIVE",
                "HIDDEN",
                "DELETED",
                name="community_comment_status",
                native_enum=False,
            ),
            nullable=False,
        ),
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
        sa.ForeignKeyConstraint(["post_id"], ["community_posts.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        op.f("ix_community_comments_created_at"),
        "community_comments",
        ["created_at"],
        unique=False,
    )

    op.create_index(
        op.f("ix_community_comments_post_id"),
        "community_comments",
        ["post_id"],
        unique=False,
    )

    op.create_index(
        op.f("ix_community_comments_status"),
        "community_comments",
        ["status"],
        unique=False,
    )

    op.create_index(
        op.f("ix_community_comments_user_id"),
        "community_comments",
        ["user_id"],
        unique=False,
    )

    op.create_table(
        "community_likes",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("post_id", sa.String(length=36), nullable=False),
        sa.Column("user_id", sa.String(length=36), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["post_id"], ["community_posts.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "post_id",
            "user_id",
            name="uq_community_like_post_user",
        ),
    )

    op.create_index(
        op.f("ix_community_likes_post_id"),
        "community_likes",
        ["post_id"],
        unique=False,
    )

    op.create_index(
        op.f("ix_community_likes_user_id"),
        "community_likes",
        ["user_id"],
        unique=False,
    )

    op.create_table(
        "community_reports",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("post_id", sa.String(length=36), nullable=False),
        sa.Column("user_id", sa.String(length=36), nullable=False),
        sa.Column(
            "reason",
            sa.Enum(
                "SPAM",
                "INAPPROPRIATE",
                "HARASSMENT",
                "MISINFORMATION",
                "OTHER",
                name="community_report_reason",
                native_enum=False,
            ),
            nullable=False,
        ),
        sa.Column("details", sa.Text(), nullable=True),
        sa.Column(
            "status",
            sa.Enum(
                "PENDING",
                "REVIEWED",
                "DISMISSED",
                "ACTION_TAKEN",
                name="community_report_status",
                native_enum=False,
            ),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["post_id"], ["community_posts.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "post_id",
            "user_id",
            name="uq_community_report_post_user",
        ),
    )

    op.create_index(
        op.f("ix_community_reports_created_at"),
        "community_reports",
        ["created_at"],
        unique=False,
    )

    op.create_index(
        op.f("ix_community_reports_post_id"),
        "community_reports",
        ["post_id"],
        unique=False,
    )

    op.create_index(
        op.f("ix_community_reports_reason"),
        "community_reports",
        ["reason"],
        unique=False,
    )

    op.create_index(
        op.f("ix_community_reports_status"),
        "community_reports",
        ["status"],
        unique=False,
    )

    op.create_index(
        op.f("ix_community_reports_user_id"),
        "community_reports",
        ["user_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_community_reports_user_id"),
        table_name="community_reports",
    )
    op.drop_index(
        op.f("ix_community_reports_status"),
        table_name="community_reports",
    )
    op.drop_index(
        op.f("ix_community_reports_reason"),
        table_name="community_reports",
    )
    op.drop_index(
        op.f("ix_community_reports_post_id"),
        table_name="community_reports",
    )
    op.drop_index(
        op.f("ix_community_reports_created_at"),
        table_name="community_reports",
    )
    op.drop_table("community_reports")

    op.drop_index(
        op.f("ix_community_likes_user_id"),
        table_name="community_likes",
    )
    op.drop_index(
        op.f("ix_community_likes_post_id"),
        table_name="community_likes",
    )
    op.drop_table("community_likes")

    op.drop_index(
        op.f("ix_community_comments_user_id"),
        table_name="community_comments",
    )
    op.drop_index(
        op.f("ix_community_comments_status"),
        table_name="community_comments",
    )
    op.drop_index(
        op.f("ix_community_comments_post_id"),
        table_name="community_comments",
    )
    op.drop_index(
        op.f("ix_community_comments_created_at"),
        table_name="community_comments",
    )
    op.drop_table("community_comments")

    op.drop_index(
        op.f("ix_community_posts_visibility"),
        table_name="community_posts",
    )
    op.drop_index(
        op.f("ix_community_posts_user_id"),
        table_name="community_posts",
    )
    op.drop_index(
        op.f("ix_community_posts_submission_id"),
        table_name="community_posts",
    )
    op.drop_index(
        op.f("ix_community_posts_status"),
        table_name="community_posts",
    )
    op.drop_index(
        op.f("ix_community_posts_post_type"),
        table_name="community_posts",
    )
    op.drop_index(
        op.f("ix_community_posts_created_at"),
        table_name="community_posts",
    )
    op.drop_index(
        op.f("ix_community_posts_challenge_id"),
        table_name="community_posts",
    )
    op.drop_table("community_posts")