"""create environmental impact tables

Revision ID: e4f8b2c7a9d3
Revises: d2e7a9c1f4b6
Create Date: 2026-06-18 00:00:00.000000

"""
from typing import Sequence
from typing import Union

from alembic import op
import sqlalchemy as sa


revision: str = "e4f8b2c7a9d3"
down_revision: Union[str, Sequence[str], None] = "d2e7a9c1f4b6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "impact_metrics",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("user_id", sa.String(length=36), nullable=False),
        sa.Column("challenge_id", sa.String(length=36), nullable=True),
        sa.Column("submission_id", sa.String(length=36), nullable=False),
        sa.Column(
            "metric_type",
            sa.Enum(
                "TREE_PLANTATION",
                "WASTE_DIVERSION",
                "WATER_SAVED",
                "ENERGY_SAVED",
                "TRANSPORT_EMISSION_SAVED",
                "PLANT_HEALTH",
                "MIXED",
                name="impact_metric_type",
                native_enum=False,
            ),
            nullable=False,
        ),
        sa.Column(
            "calculation_status",
            sa.Enum(
                "ESTIMATED",
                "CONFIRMED",
                "NEEDS_REVIEW",
                "FAILED",
                name="impact_calculation_status",
                native_enum=False,
            ),
            nullable=False,
        ),
        sa.Column("co2e_saved_kg", sa.Float(), nullable=False),
        sa.Column("waste_diverted_kg", sa.Float(), nullable=False),
        sa.Column("water_saved_liters", sa.Float(), nullable=False),
        sa.Column("energy_saved_kwh", sa.Float(), nullable=False),
        sa.Column("trees_planted", sa.Float(), nullable=False),
        sa.Column("transport_distance_km", sa.Float(), nullable=False),
        sa.Column("biodiversity_score", sa.Float(), nullable=False),
        sa.Column("confidence_score", sa.Float(), nullable=False),
        sa.Column("calculation_method", sa.String(length=120), nullable=False),
        sa.Column("assumptions_json", sa.JSON(), nullable=True),
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
        sa.UniqueConstraint("submission_id"),
    )

    op.create_index(
        op.f("ix_impact_metrics_calculation_status"),
        "impact_metrics",
        ["calculation_status"],
        unique=False,
    )

    op.create_index(
        op.f("ix_impact_metrics_challenge_id"),
        "impact_metrics",
        ["challenge_id"],
        unique=False,
    )

    op.create_index(
        op.f("ix_impact_metrics_metric_type"),
        "impact_metrics",
        ["metric_type"],
        unique=False,
    )

    op.create_index(
        op.f("ix_impact_metrics_submission_id"),
        "impact_metrics",
        ["submission_id"],
        unique=False,
    )

    op.create_index(
        op.f("ix_impact_metrics_user_id"),
        "impact_metrics",
        ["user_id"],
        unique=False,
    )

    op.create_table(
        "user_impact_summaries",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("user_id", sa.String(length=36), nullable=False),
        sa.Column("total_co2e_saved_kg", sa.Float(), nullable=False),
        sa.Column("total_waste_diverted_kg", sa.Float(), nullable=False),
        sa.Column("total_water_saved_liters", sa.Float(), nullable=False),
        sa.Column("total_energy_saved_kwh", sa.Float(), nullable=False),
        sa.Column("total_trees_planted", sa.Float(), nullable=False),
        sa.Column("total_transport_distance_km", sa.Float(), nullable=False),
        sa.Column("total_biodiversity_score", sa.Float(), nullable=False),
        sa.Column("impact_actions_count", sa.Integer(), nullable=False),
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
        op.f("ix_user_impact_summaries_user_id"),
        "user_impact_summaries",
        ["user_id"],
        unique=True,
    )

    op.create_table(
        "challenge_impact_summaries",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("challenge_id", sa.String(length=36), nullable=False),
        sa.Column("total_co2e_saved_kg", sa.Float(), nullable=False),
        sa.Column("total_waste_diverted_kg", sa.Float(), nullable=False),
        sa.Column("total_water_saved_liters", sa.Float(), nullable=False),
        sa.Column("total_energy_saved_kwh", sa.Float(), nullable=False),
        sa.Column("total_trees_planted", sa.Float(), nullable=False),
        sa.Column("total_transport_distance_km", sa.Float(), nullable=False),
        sa.Column("total_biodiversity_score", sa.Float(), nullable=False),
        sa.Column("impact_actions_count", sa.Integer(), nullable=False),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["challenge_id"], ["challenges.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("challenge_id"),
    )

    op.create_index(
        op.f("ix_challenge_impact_summaries_challenge_id"),
        "challenge_impact_summaries",
        ["challenge_id"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_challenge_impact_summaries_challenge_id"),
        table_name="challenge_impact_summaries",
    )
    op.drop_table("challenge_impact_summaries")

    op.drop_index(
        op.f("ix_user_impact_summaries_user_id"),
        table_name="user_impact_summaries",
    )
    op.drop_table("user_impact_summaries")

    op.drop_index(
        op.f("ix_impact_metrics_user_id"),
        table_name="impact_metrics",
    )

    op.drop_index(
        op.f("ix_impact_metrics_submission_id"),
        table_name="impact_metrics",
    )

    op.drop_index(
        op.f("ix_impact_metrics_metric_type"),
        table_name="impact_metrics",
    )

    op.drop_index(
        op.f("ix_impact_metrics_challenge_id"),
        table_name="impact_metrics",
    )

    op.drop_index(
        op.f("ix_impact_metrics_calculation_status"),
        table_name="impact_metrics",
    )

    op.drop_table("impact_metrics")