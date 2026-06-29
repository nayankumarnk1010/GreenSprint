"""create gamification tables

Revision ID: f6a9c3d8e2b1
Revises: e4f8b2c7a9d3
Create Date: 2026-06-19 00:00:00.000000

"""
from typing import Sequence
from typing import Union

from alembic import op
import sqlalchemy as sa


revision: str = "f6a9c3d8e2b1"
down_revision: Union[str, Sequence[str], None] = "e4f8b2c7a9d3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "user_gamification_profiles",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("user_id", sa.String(length=36), nullable=False),
        sa.Column("total_points", sa.Integer(), nullable=False),
        sa.Column("current_level", sa.Integer(), nullable=False),
        sa.Column("green_reputation_score", sa.Float(), nullable=False),
        sa.Column("total_badges", sa.Integer(), nullable=False),
        sa.Column("impact_actions_rewarded", sa.Integer(), nullable=False),
        sa.Column("ai_verified_actions", sa.Integer(), nullable=False),
        sa.Column("approved_actions", sa.Integer(), nullable=False),
        sa.Column("rejected_actions", sa.Integer(), nullable=False),
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
        op.f("ix_user_gamification_profiles_user_id"),
        "user_gamification_profiles",
        ["user_id"],
        unique=True,
    )

    op.create_table(
        "points_ledger",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("user_id", sa.String(length=36), nullable=False),
        sa.Column("submission_id", sa.String(length=36), nullable=True),
        sa.Column("points", sa.Integer(), nullable=False),
        sa.Column(
            "transaction_type",
            sa.Enum(
                "EARNED",
                "BONUS",
                "PENALTY",
                "ADJUSTMENT",
                name="points_transaction_type",
                native_enum=False,
            ),
            nullable=False,
        ),
        sa.Column(
            "source_type",
            sa.Enum(
                "SUBMISSION",
                "AI_VERIFICATION",
                "ADMIN_APPROVAL",
                "BADGE_BONUS",
                "SYSTEM",
                name="points_source_type",
                native_enum=False,
            ),
            nullable=False,
        ),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("metadata_json", sa.JSON(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["submission_id"], ["submissions.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("submission_id"),
    )

    op.create_index(
        op.f("ix_points_ledger_source_type"),
        "points_ledger",
        ["source_type"],
        unique=False,
    )

    op.create_index(
        op.f("ix_points_ledger_submission_id"),
        "points_ledger",
        ["submission_id"],
        unique=True,
    )

    op.create_index(
        op.f("ix_points_ledger_transaction_type"),
        "points_ledger",
        ["transaction_type"],
        unique=False,
    )

    op.create_index(
        op.f("ix_points_ledger_user_id"),
        "points_ledger",
        ["user_id"],
        unique=False,
    )

    op.create_table(
        "badges",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("code", sa.String(length=80), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column(
            "category",
            sa.Enum(
                "STARTER",
                "TREE_PLANTATION",
                "RECYCLING",
                "CLEANUP",
                "WATER",
                "ENERGY",
                "TRANSPORT",
                "PLANT_HEALTH",
                "IMPACT",
                "COMMUNITY",
                name="badge_category",
                native_enum=False,
            ),
            nullable=False,
        ),
        sa.Column("points_threshold", sa.Integer(), nullable=False),
        sa.Column("badge_points_bonus", sa.Integer(), nullable=False),
        sa.Column("requirements_json", sa.JSON(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code"),
    )

    op.create_index(
        op.f("ix_badges_category"),
        "badges",
        ["category"],
        unique=False,
    )

    op.create_index(
        op.f("ix_badges_code"),
        "badges",
        ["code"],
        unique=True,
    )

    op.create_index(
        op.f("ix_badges_is_active"),
        "badges",
        ["is_active"],
        unique=False,
    )

    op.create_table(
        "user_badges",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("user_id", sa.String(length=36), nullable=False),
        sa.Column("badge_id", sa.String(length=36), nullable=False),
        sa.Column("awarded_from_submission_id", sa.String(length=36), nullable=True),
        sa.Column(
            "awarded_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["awarded_from_submission_id"], ["submissions.id"]),
        sa.ForeignKeyConstraint(["badge_id"], ["badges.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "user_id",
            "badge_id",
            name="uq_user_badge_user_id_badge_id",
        ),
    )

    op.create_index(
        op.f("ix_user_badges_awarded_from_submission_id"),
        "user_badges",
        ["awarded_from_submission_id"],
        unique=False,
    )

    op.create_index(
        op.f("ix_user_badges_badge_id"),
        "user_badges",
        ["badge_id"],
        unique=False,
    )

    op.create_index(
        op.f("ix_user_badges_user_id"),
        "user_badges",
        ["user_id"],
        unique=False,
    )

    op.create_table(
        "leaderboard_snapshots",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("user_id", sa.String(length=36), nullable=False),
        sa.Column(
            "period",
            sa.Enum(
                "ALL_TIME",
                "MONTHLY",
                "WEEKLY",
                name="leaderboard_period",
                native_enum=False,
            ),
            nullable=False,
        ),
        sa.Column("rank", sa.Integer(), nullable=False),
        sa.Column("total_points", sa.Integer(), nullable=False),
        sa.Column("green_reputation_score", sa.Float(), nullable=False),
        sa.Column(
            "generated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        op.f("ix_leaderboard_snapshots_generated_at"),
        "leaderboard_snapshots",
        ["generated_at"],
        unique=False,
    )

    op.create_index(
        op.f("ix_leaderboard_snapshots_period"),
        "leaderboard_snapshots",
        ["period"],
        unique=False,
    )

    op.create_index(
        op.f("ix_leaderboard_snapshots_rank"),
        "leaderboard_snapshots",
        ["rank"],
        unique=False,
    )

    op.create_index(
        op.f("ix_leaderboard_snapshots_user_id"),
        "leaderboard_snapshots",
        ["user_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_leaderboard_snapshots_user_id"),
        table_name="leaderboard_snapshots",
    )

    op.drop_index(
        op.f("ix_leaderboard_snapshots_rank"),
        table_name="leaderboard_snapshots",
    )

    op.drop_index(
        op.f("ix_leaderboard_snapshots_period"),
        table_name="leaderboard_snapshots",
    )

    op.drop_index(
        op.f("ix_leaderboard_snapshots_generated_at"),
        table_name="leaderboard_snapshots",
    )

    op.drop_table("leaderboard_snapshots")

    op.drop_index(
        op.f("ix_user_badges_user_id"),
        table_name="user_badges",
    )

    op.drop_index(
        op.f("ix_user_badges_badge_id"),
        table_name="user_badges",
    )

    op.drop_index(
        op.f("ix_user_badges_awarded_from_submission_id"),
        table_name="user_badges",
    )

    op.drop_table("user_badges")

    op.drop_index(
        op.f("ix_badges_is_active"),
        table_name="badges",
    )

    op.drop_index(
        op.f("ix_badges_code"),
        table_name="badges",
    )

    op.drop_index(
        op.f("ix_badges_category"),
        table_name="badges",
    )

    op.drop_table("badges")

    op.drop_index(
        op.f("ix_points_ledger_user_id"),
        table_name="points_ledger",
    )

    op.drop_index(
        op.f("ix_points_ledger_transaction_type"),
        table_name="points_ledger",
    )

    op.drop_index(
        op.f("ix_points_ledger_submission_id"),
        table_name="points_ledger",
    )

    op.drop_index(
        op.f("ix_points_ledger_source_type"),
        table_name="points_ledger",
    )

    op.drop_table("points_ledger")

    op.drop_index(
        op.f("ix_user_gamification_profiles_user_id"),
        table_name="user_gamification_profiles",
    )

    op.drop_table("user_gamification_profiles")