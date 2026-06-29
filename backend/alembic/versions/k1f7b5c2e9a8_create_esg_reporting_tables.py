"""create esg reporting tables

Revision ID: k1f7b5c2e9a8
Revises: j0e6a4b9d2c5
Create Date: 2026-06-24 00:00:00.000000

"""
from typing import Sequence
from typing import Union

from alembic import op
import sqlalchemy as sa


revision: str = "k1f7b5c2e9a8"
down_revision: Union[str, Sequence[str], None] = "j0e6a4b9d2c5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "esg_reports",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("organization_id", sa.String(length=36), nullable=False),
        sa.Column("campaign_id", sa.String(length=36), nullable=True),
        sa.Column("created_by", sa.String(length=36), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column(
            "report_type",
            sa.Enum(
                "ORGANIZATION",
                "CAMPAIGN",
                name="esg_report_type",
                native_enum=False,
            ),
            nullable=False,
        ),
        sa.Column(
            "status",
            sa.Enum(
                "DRAFT",
                "GENERATED",
                "PUBLISHED",
                "ARCHIVED",
                name="esg_report_status",
                native_enum=False,
            ),
            nullable=False,
        ),
        sa.Column("period_start", sa.DateTime(timezone=True), nullable=True),
        sa.Column("period_end", sa.DateTime(timezone=True), nullable=True),
        sa.Column("summary_json", sa.Text(), nullable=True),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
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
        sa.ForeignKeyConstraint(["campaign_id"], ["campaigns.id"]),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"]),
        sa.ForeignKeyConstraint(["organization_id"], ["organization_profiles.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        op.f("ix_esg_reports_campaign_id"),
        "esg_reports",
        ["campaign_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_esg_reports_created_at"),
        "esg_reports",
        ["created_at"],
        unique=False,
    )
    op.create_index(
        op.f("ix_esg_reports_created_by"),
        "esg_reports",
        ["created_by"],
        unique=False,
    )
    op.create_index(
        op.f("ix_esg_reports_organization_id"),
        "esg_reports",
        ["organization_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_esg_reports_period_end"),
        "esg_reports",
        ["period_end"],
        unique=False,
    )
    op.create_index(
        op.f("ix_esg_reports_period_start"),
        "esg_reports",
        ["period_start"],
        unique=False,
    )
    op.create_index(
        op.f("ix_esg_reports_report_type"),
        "esg_reports",
        ["report_type"],
        unique=False,
    )
    op.create_index(
        op.f("ix_esg_reports_status"),
        "esg_reports",
        ["status"],
        unique=False,
    )

    op.create_table(
        "esg_report_metrics",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("report_id", sa.String(length=36), nullable=False),
        sa.Column(
            "category",
            sa.Enum(
                "ENVIRONMENTAL",
                "SOCIAL",
                "GOVERNANCE",
                "ENGAGEMENT",
                "VERIFICATION",
                name="esg_metric_category",
                native_enum=False,
            ),
            nullable=False,
        ),
        sa.Column("metric_key", sa.String(length=100), nullable=False),
        sa.Column("metric_name", sa.String(length=255), nullable=False),
        sa.Column("value_number", sa.Float(), nullable=True),
        sa.Column("value_text", sa.Text(), nullable=True),
        sa.Column("unit", sa.String(length=50), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["report_id"], ["esg_reports.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        op.f("ix_esg_report_metrics_category"),
        "esg_report_metrics",
        ["category"],
        unique=False,
    )
    op.create_index(
        op.f("ix_esg_report_metrics_metric_key"),
        "esg_report_metrics",
        ["metric_key"],
        unique=False,
    )
    op.create_index(
        op.f("ix_esg_report_metrics_report_id"),
        "esg_report_metrics",
        ["report_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_esg_report_metrics_report_id"),
        table_name="esg_report_metrics",
    )
    op.drop_index(
        op.f("ix_esg_report_metrics_metric_key"),
        table_name="esg_report_metrics",
    )
    op.drop_index(
        op.f("ix_esg_report_metrics_category"),
        table_name="esg_report_metrics",
    )
    op.drop_table("esg_report_metrics")

    op.drop_index(op.f("ix_esg_reports_status"), table_name="esg_reports")
    op.drop_index(op.f("ix_esg_reports_report_type"), table_name="esg_reports")
    op.drop_index(op.f("ix_esg_reports_period_start"), table_name="esg_reports")
    op.drop_index(op.f("ix_esg_reports_period_end"), table_name="esg_reports")
    op.drop_index(op.f("ix_esg_reports_organization_id"), table_name="esg_reports")
    op.drop_index(op.f("ix_esg_reports_created_by"), table_name="esg_reports")
    op.drop_index(op.f("ix_esg_reports_created_at"), table_name="esg_reports")
    op.drop_index(op.f("ix_esg_reports_campaign_id"), table_name="esg_reports")
    op.drop_table("esg_reports")