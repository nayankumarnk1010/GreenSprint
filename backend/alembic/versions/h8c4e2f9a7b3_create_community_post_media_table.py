"""create community post media table

Revision ID: h8c4e2f9a7b3
Revises: g7b2d9e4f6a1
Create Date: 2026-06-19 00:00:00.000000

"""
from typing import Sequence
from typing import Union

from alembic import op
import sqlalchemy as sa


revision: str = "h8c4e2f9a7b3"
down_revision: Union[str, Sequence[str], None] = "g7b2d9e4f6a1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "community_post_media",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("post_id", sa.String(length=36), nullable=False),
        sa.Column("user_id", sa.String(length=36), nullable=False),
        sa.Column(
            "media_type",
            sa.Enum(
                "IMAGE",
                "VIDEO",
                "DOCUMENT",
                name="community_post_media_type",
                native_enum=False,
            ),
            nullable=False,
        ),
        sa.Column("original_file_name", sa.String(length=255), nullable=False),
        sa.Column("stored_file_name", sa.String(length=255), nullable=False),
        sa.Column("file_path", sa.Text(), nullable=False),
        sa.Column("media_url", sa.Text(), nullable=False),
        sa.Column("mime_type", sa.String(length=100), nullable=False),
        sa.Column("file_size_bytes", sa.Integer(), nullable=False),
        sa.Column("file_sha256", sa.String(length=64), nullable=True),
        sa.Column("alt_text", sa.String(length=255), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["post_id"], ["community_posts.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        op.f("ix_community_post_media_created_at"),
        "community_post_media",
        ["created_at"],
        unique=False,
    )

    op.create_index(
        op.f("ix_community_post_media_file_sha256"),
        "community_post_media",
        ["file_sha256"],
        unique=False,
    )

    op.create_index(
        op.f("ix_community_post_media_media_type"),
        "community_post_media",
        ["media_type"],
        unique=False,
    )

    op.create_index(
        op.f("ix_community_post_media_post_id"),
        "community_post_media",
        ["post_id"],
        unique=False,
    )

    op.create_index(
        op.f("ix_community_post_media_user_id"),
        "community_post_media",
        ["user_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_community_post_media_user_id"),
        table_name="community_post_media",
    )

    op.drop_index(
        op.f("ix_community_post_media_post_id"),
        table_name="community_post_media",
    )

    op.drop_index(
        op.f("ix_community_post_media_media_type"),
        table_name="community_post_media",
    )

    op.drop_index(
        op.f("ix_community_post_media_file_sha256"),
        table_name="community_post_media",
    )

    op.drop_index(
        op.f("ix_community_post_media_created_at"),
        table_name="community_post_media",
    )

    op.drop_table("community_post_media")