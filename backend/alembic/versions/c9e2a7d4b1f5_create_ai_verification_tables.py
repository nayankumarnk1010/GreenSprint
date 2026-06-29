"""create ai verification and fraud check tables

Revision ID: c9e2a7d4b1f5
Revises: b4f6b3d9c8a1
Create Date: 2026-06-18 00:00:00.000000

"""
from typing import Sequence
from typing import Union

from alembic import op
import sqlalchemy as sa


revision: str = "c9e2a7d4b1f5"
down_revision: Union[str, Sequence[str], None] = "b4f6b3d9c8a1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("submission_media") as batch_op:
        batch_op.add_column(
            sa.Column(
                "file_sha256",
                sa.String(length=64),
                nullable=True,
            )
        )

        batch_op.add_column(
            sa.Column(
                "image_width",
                sa.Integer(),
                nullable=True,
            )
        )

        batch_op.add_column(
            sa.Column(
                "image_height",
                sa.Integer(),
                nullable=True,
            )
        )

        batch_op.create_index(
            "ix_submission_media_file_sha256",
            ["file_sha256"],
            unique=False,
        )

    op.create_table(
        "ai_verifications",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("submission_id", sa.String(length=36), nullable=False),
        sa.Column("media_id", sa.String(length=36), nullable=True),
        sa.Column(
            "status",
            sa.Enum(
                "QUEUED",
                "RUNNING",
                "COMPLETED",
                "FAILED",
                name="ai_verification_status",
                native_enum=False,
            ),
            nullable=False,
        ),
        sa.Column(
            "decision",
            sa.Enum(
                "VERIFIED",
                "REJECTED",
                "MANUAL_REVIEW",
                name="ai_verification_decision",
                native_enum=False,
            ),
            nullable=True,
        ),
        sa.Column("confidence_score", sa.Float(), nullable=True),
        sa.Column("fraud_risk_score", sa.Float(), nullable=True),
        sa.Column("model_name", sa.String(length=100), nullable=False),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("result_json", sa.JSON(), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["media_id"], ["submission_media.id"]),
        sa.ForeignKeyConstraint(["submission_id"], ["submissions.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        op.f("ix_ai_verifications_decision"),
        "ai_verifications",
        ["decision"],
        unique=False,
    )

    op.create_index(
        op.f("ix_ai_verifications_fraud_risk_score"),
        "ai_verifications",
        ["fraud_risk_score"],
        unique=False,
    )

    op.create_index(
        op.f("ix_ai_verifications_media_id"),
        "ai_verifications",
        ["media_id"],
        unique=False,
    )

    op.create_index(
        op.f("ix_ai_verifications_status"),
        "ai_verifications",
        ["status"],
        unique=False,
    )

    op.create_index(
        op.f("ix_ai_verifications_submission_id"),
        "ai_verifications",
        ["submission_id"],
        unique=False,
    )

    op.create_table(
        "fraud_checks",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("verification_id", sa.String(length=36), nullable=False),
        sa.Column(
            "check_type",
            sa.Enum(
                "FILE_INTEGRITY",
                "DUPLICATE_IMAGE",
                "SCREENSHOT_DETECTION",
                "IMAGE_QUALITY",
                "GPS_VALIDATION",
                "CONTENT_RELEVANCE",
                name="fraud_check_type",
                native_enum=False,
            ),
            nullable=False,
        ),
        sa.Column(
            "result",
            sa.Enum(
                "PASS",
                "WARNING",
                "FAIL",
                "NOT_APPLICABLE",
                name="fraud_check_result",
                native_enum=False,
            ),
            nullable=False,
        ),
        sa.Column("risk_score", sa.Float(), nullable=False),
        sa.Column("message", sa.Text(), nullable=True),
        sa.Column("details_json", sa.JSON(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["verification_id"], ["ai_verifications.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        op.f("ix_fraud_checks_check_type"),
        "fraud_checks",
        ["check_type"],
        unique=False,
    )

    op.create_index(
        op.f("ix_fraud_checks_result"),
        "fraud_checks",
        ["result"],
        unique=False,
    )

    op.create_index(
        op.f("ix_fraud_checks_verification_id"),
        "fraud_checks",
        ["verification_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_fraud_checks_verification_id"),
        table_name="fraud_checks",
    )

    op.drop_index(
        op.f("ix_fraud_checks_result"),
        table_name="fraud_checks",
    )

    op.drop_index(
        op.f("ix_fraud_checks_check_type"),
        table_name="fraud_checks",
    )

    op.drop_table("fraud_checks")

    op.drop_index(
        op.f("ix_ai_verifications_submission_id"),
        table_name="ai_verifications",
    )

    op.drop_index(
        op.f("ix_ai_verifications_status"),
        table_name="ai_verifications",
    )

    op.drop_index(
        op.f("ix_ai_verifications_media_id"),
        table_name="ai_verifications",
    )

    op.drop_index(
        op.f("ix_ai_verifications_fraud_risk_score"),
        table_name="ai_verifications",
    )

    op.drop_index(
        op.f("ix_ai_verifications_decision"),
        table_name="ai_verifications",
    )

    op.drop_table("ai_verifications")

    with op.batch_alter_table("submission_media") as batch_op:
        batch_op.drop_index("ix_submission_media_file_sha256")
        batch_op.drop_column("image_height")
        batch_op.drop_column("image_width")
        batch_op.drop_column("file_sha256")