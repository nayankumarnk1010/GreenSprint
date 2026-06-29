"""create admin control tables

Revision ID: l2a8c6d4f9b1
Revises: k1f7b5c2e9a8
Create Date: 2026-06-25 00:00:00.000000

"""
from typing import Sequence
from typing import Union

from alembic import op
import sqlalchemy as sa


revision: str = "l2a8c6d4f9b1"
down_revision: Union[str, Sequence[str], None] = "k1f7b5c2e9a8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "admin_audit_logs",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("actor_user_id", sa.String(length=36), nullable=False),
        sa.Column("action", sa.String(length=100), nullable=False),
        sa.Column("target_type", sa.String(length=100), nullable=False),
        sa.Column("target_id", sa.String(length=36), nullable=True),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("metadata_json", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["actor_user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        op.f("ix_admin_audit_logs_action"),
        "admin_audit_logs",
        ["action"],
        unique=False,
    )
    op.create_index(
        op.f("ix_admin_audit_logs_actor_user_id"),
        "admin_audit_logs",
        ["actor_user_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_admin_audit_logs_created_at"),
        "admin_audit_logs",
        ["created_at"],
        unique=False,
    )
    op.create_index(
        op.f("ix_admin_audit_logs_target_id"),
        "admin_audit_logs",
        ["target_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_admin_audit_logs_target_type"),
        "admin_audit_logs",
        ["target_type"],
        unique=False,
    )

    op.create_table(
        "platform_settings",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("setting_key", sa.String(length=100), nullable=False),
        sa.Column("setting_value", sa.Text(), nullable=False),
        sa.Column("value_type", sa.String(length=50), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("updated_by", sa.String(length=36), nullable=True),
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
        sa.ForeignKeyConstraint(["updated_by"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("setting_key"),
    )

    op.create_index(
        op.f("ix_platform_settings_setting_key"),
        "platform_settings",
        ["setting_key"],
        unique=True,
    )
    op.create_index(
        op.f("ix_platform_settings_updated_by"),
        "platform_settings",
        ["updated_by"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_platform_settings_updated_by"),
        table_name="platform_settings",
    )
    op.drop_index(
        op.f("ix_platform_settings_setting_key"),
        table_name="platform_settings",
    )
    op.drop_table("platform_settings")

    op.drop_index(
        op.f("ix_admin_audit_logs_target_type"),
        table_name="admin_audit_logs",
    )
    op.drop_index(
        op.f("ix_admin_audit_logs_target_id"),
        table_name="admin_audit_logs",
    )
    op.drop_index(
        op.f("ix_admin_audit_logs_created_at"),
        table_name="admin_audit_logs",
    )
    op.drop_index(
        op.f("ix_admin_audit_logs_actor_user_id"),
        table_name="admin_audit_logs",
    )
    op.drop_index(
        op.f("ix_admin_audit_logs_action"),
        table_name="admin_audit_logs",
    )
    op.drop_table("admin_audit_logs")