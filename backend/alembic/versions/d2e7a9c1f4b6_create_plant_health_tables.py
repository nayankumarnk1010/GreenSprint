"""create plant health diagnosis tables

Revision ID: d2e7a9c1f4b6
Revises: c9e2a7d4b1f5
Create Date: 2026-06-18 00:00:00.000000

"""
from typing import Sequence
from typing import Union

from alembic import op
import sqlalchemy as sa


revision: str = "d2e7a9c1f4b6"
down_revision: Union[str, Sequence[str], None] = "c9e2a7d4b1f5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "plant_diagnoses",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("user_id", sa.String(length=36), nullable=False),
        sa.Column("submission_id", sa.String(length=36), nullable=False),
        sa.Column("media_id", sa.String(length=36), nullable=False),
        sa.Column("plant_name", sa.String(length=120), nullable=True),
        sa.Column("disease_name", sa.String(length=180), nullable=False),
        sa.Column(
            "severity",
            sa.Enum(
                "HEALTHY",
                "LOW",
                "MODERATE",
                "HIGH",
                "CRITICAL",
                name="plant_disease_severity",
                native_enum=False,
            ),
            nullable=False,
        ),
        sa.Column(
            "status",
            sa.Enum(
                "COMPLETED",
                "FAILED",
                "MANUAL_REVIEW",
                name="plant_diagnosis_status",
                native_enum=False,
            ),
            nullable=False,
        ),
        sa.Column("confidence_score", sa.Float(), nullable=False),
        sa.Column("model_name", sa.String(length=120), nullable=False),
        sa.Column("symptoms_json", sa.JSON(), nullable=True),
        sa.Column("cure_summary", sa.Text(), nullable=True),
        sa.Column("prevention_tips", sa.Text(), nullable=True),
        sa.Column("raw_result_json", sa.JSON(), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["media_id"], ["submission_media.id"]),
        sa.ForeignKeyConstraint(["submission_id"], ["submissions.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        op.f("ix_plant_diagnoses_disease_name"),
        "plant_diagnoses",
        ["disease_name"],
        unique=False,
    )

    op.create_index(
        op.f("ix_plant_diagnoses_media_id"),
        "plant_diagnoses",
        ["media_id"],
        unique=False,
    )

    op.create_index(
        op.f("ix_plant_diagnoses_severity"),
        "plant_diagnoses",
        ["severity"],
        unique=False,
    )

    op.create_index(
        op.f("ix_plant_diagnoses_status"),
        "plant_diagnoses",
        ["status"],
        unique=False,
    )

    op.create_index(
        op.f("ix_plant_diagnoses_submission_id"),
        "plant_diagnoses",
        ["submission_id"],
        unique=False,
    )

    op.create_index(
        op.f("ix_plant_diagnoses_user_id"),
        "plant_diagnoses",
        ["user_id"],
        unique=False,
    )

    op.create_table(
        "plant_care_recommendations",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("diagnosis_id", sa.String(length=36), nullable=False),
        sa.Column(
            "recommendation_type",
            sa.Enum(
                "CURE",
                "PREVENTION",
                "CARE",
                "FOLLOW_UP",
                name="plant_recommendation_type",
                native_enum=False,
            ),
            nullable=False,
        ),
        sa.Column("title", sa.String(length=180), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("priority_order", sa.Integer(), nullable=False),
        sa.Column("safety_note", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["diagnosis_id"], ["plant_diagnoses.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        op.f("ix_plant_care_recommendations_diagnosis_id"),
        "plant_care_recommendations",
        ["diagnosis_id"],
        unique=False,
    )

    op.create_index(
        op.f("ix_plant_care_recommendations_recommendation_type"),
        "plant_care_recommendations",
        ["recommendation_type"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_plant_care_recommendations_recommendation_type"),
        table_name="plant_care_recommendations",
    )

    op.drop_index(
        op.f("ix_plant_care_recommendations_diagnosis_id"),
        table_name="plant_care_recommendations",
    )

    op.drop_table("plant_care_recommendations")

    op.drop_index(
        op.f("ix_plant_diagnoses_user_id"),
        table_name="plant_diagnoses",
    )

    op.drop_index(
        op.f("ix_plant_diagnoses_submission_id"),
        table_name="plant_diagnoses",
    )

    op.drop_index(
        op.f("ix_plant_diagnoses_status"),
        table_name="plant_diagnoses",
    )

    op.drop_index(
        op.f("ix_plant_diagnoses_severity"),
        table_name="plant_diagnoses",
    )

    op.drop_index(
        op.f("ix_plant_diagnoses_media_id"),
        table_name="plant_diagnoses",
    )

    op.drop_index(
        op.f("ix_plant_diagnoses_disease_name"),
        table_name="plant_diagnoses",
    )

    op.drop_table("plant_diagnoses")