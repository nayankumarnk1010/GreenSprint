"""create organization campaign tables

Revision ID: i9d5f3a2c8b4
Revises: h8c4e2f9a7b3
Create Date: 2026-06-23 00:00:00.000000

"""
from typing import Sequence
from typing import Union

from alembic import op
import sqlalchemy as sa


revision: str = "i9d5f3a2c8b4"
down_revision: Union[str, Sequence[str], None] = "h8c4e2f9a7b3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "organization_profiles",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("user_id", sa.String(length=36), nullable=False),
        sa.Column("organization_name", sa.String(length=255), nullable=False),
        sa.Column(
            "organization_type",
            sa.Enum(
                "NGO",
                "CORPORATE",
                "COLLEGE",
                "SCHOOL",
                "GOVERNMENT",
                "COMMUNITY_GROUP",
                "OTHER",
                name="organization_type",
                native_enum=False,
            ),
            nullable=False,
        ),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("website_url", sa.String(length=500), nullable=True),
        sa.Column("contact_email", sa.String(length=255), nullable=True),
        sa.Column("contact_phone", sa.String(length=50), nullable=True),
        sa.Column("city", sa.String(length=100), nullable=True),
        sa.Column("state", sa.String(length=100), nullable=True),
        sa.Column("country", sa.String(length=100), nullable=False),
        sa.Column(
            "status",
            sa.Enum(
                "ACTIVE",
                "INACTIVE",
                "VERIFICATION_PENDING",
                "SUSPENDED",
                name="organization_profile_status",
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
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id"),
    )

    op.create_index(
        op.f("ix_organization_profiles_city"),
        "organization_profiles",
        ["city"],
        unique=False,
    )
    op.create_index(
        op.f("ix_organization_profiles_country"),
        "organization_profiles",
        ["country"],
        unique=False,
    )
    op.create_index(
        op.f("ix_organization_profiles_created_at"),
        "organization_profiles",
        ["created_at"],
        unique=False,
    )
    op.create_index(
        op.f("ix_organization_profiles_organization_name"),
        "organization_profiles",
        ["organization_name"],
        unique=False,
    )
    op.create_index(
        op.f("ix_organization_profiles_organization_type"),
        "organization_profiles",
        ["organization_type"],
        unique=False,
    )
    op.create_index(
        op.f("ix_organization_profiles_state"),
        "organization_profiles",
        ["state"],
        unique=False,
    )
    op.create_index(
        op.f("ix_organization_profiles_status"),
        "organization_profiles",
        ["status"],
        unique=False,
    )
    op.create_index(
        op.f("ix_organization_profiles_user_id"),
        "organization_profiles",
        ["user_id"],
        unique=True,
    )

    op.create_table(
        "campaigns",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("organization_id", sa.String(length=36), nullable=False),
        sa.Column("created_by", sa.String(length=36), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column(
            "status",
            sa.Enum(
                "DRAFT",
                "ACTIVE",
                "PAUSED",
                "COMPLETED",
                "CANCELLED",
                name="campaign_status",
                native_enum=False,
            ),
            nullable=False,
        ),
        sa.Column("start_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("end_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("target_participants", sa.Integer(), nullable=False),
        sa.Column("target_co2e_saved_kg", sa.Integer(), nullable=False),
        sa.Column("target_trees_planted", sa.Integer(), nullable=False),
        sa.Column("city", sa.String(length=100), nullable=True),
        sa.Column("state", sa.String(length=100), nullable=True),
        sa.Column("country", sa.String(length=100), nullable=False),
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
        sa.ForeignKeyConstraint(["created_by"], ["users.id"]),
        sa.ForeignKeyConstraint(["organization_id"], ["organization_profiles.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(op.f("ix_campaigns_city"), "campaigns", ["city"], unique=False)
    op.create_index(op.f("ix_campaigns_country"), "campaigns", ["country"], unique=False)
    op.create_index(op.f("ix_campaigns_created_at"), "campaigns", ["created_at"], unique=False)
    op.create_index(op.f("ix_campaigns_created_by"), "campaigns", ["created_by"], unique=False)
    op.create_index(op.f("ix_campaigns_end_date"), "campaigns", ["end_date"], unique=False)
    op.create_index(op.f("ix_campaigns_organization_id"), "campaigns", ["organization_id"], unique=False)
    op.create_index(op.f("ix_campaigns_start_date"), "campaigns", ["start_date"], unique=False)
    op.create_index(op.f("ix_campaigns_state"), "campaigns", ["state"], unique=False)
    op.create_index(op.f("ix_campaigns_status"), "campaigns", ["status"], unique=False)
    op.create_index(op.f("ix_campaigns_title"), "campaigns", ["title"], unique=False)

    op.create_table(
        "campaign_members",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("campaign_id", sa.String(length=36), nullable=False),
        sa.Column("user_id", sa.String(length=36), nullable=False),
        sa.Column(
            "role",
            sa.Enum(
                "OWNER",
                "MANAGER",
                "PARTICIPANT",
                "VOLUNTEER",
                name="campaign_member_role",
                native_enum=False,
            ),
            nullable=False,
        ),
        sa.Column(
            "status",
            sa.Enum(
                "ACTIVE",
                "REMOVED",
                name="campaign_member_status",
                native_enum=False,
            ),
            nullable=False,
        ),
        sa.Column(
            "joined_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["campaign_id"], ["campaigns.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "campaign_id",
            "user_id",
            name="uq_campaign_member_campaign_user",
        ),
    )

    op.create_index(
        op.f("ix_campaign_members_campaign_id"),
        "campaign_members",
        ["campaign_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_campaign_members_joined_at"),
        "campaign_members",
        ["joined_at"],
        unique=False,
    )
    op.create_index(
        op.f("ix_campaign_members_role"),
        "campaign_members",
        ["role"],
        unique=False,
    )
    op.create_index(
        op.f("ix_campaign_members_status"),
        "campaign_members",
        ["status"],
        unique=False,
    )
    op.create_index(
        op.f("ix_campaign_members_user_id"),
        "campaign_members",
        ["user_id"],
        unique=False,
    )

    op.create_table(
        "campaign_challenges",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("campaign_id", sa.String(length=36), nullable=False),
        sa.Column("challenge_id", sa.String(length=36), nullable=False),
        sa.Column(
            "status",
            sa.Enum(
                "ACTIVE",
                "REMOVED",
                name="campaign_challenge_status",
                native_enum=False,
            ),
            nullable=False,
        ),
        sa.Column("added_by", sa.String(length=36), nullable=False),
        sa.Column(
            "added_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["added_by"], ["users.id"]),
        sa.ForeignKeyConstraint(["campaign_id"], ["campaigns.id"]),
        sa.ForeignKeyConstraint(["challenge_id"], ["challenges.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "campaign_id",
            "challenge_id",
            name="uq_campaign_challenge_campaign_challenge",
        ),
    )

    op.create_index(
        op.f("ix_campaign_challenges_added_at"),
        "campaign_challenges",
        ["added_at"],
        unique=False,
    )
    op.create_index(
        op.f("ix_campaign_challenges_added_by"),
        "campaign_challenges",
        ["added_by"],
        unique=False,
    )
    op.create_index(
        op.f("ix_campaign_challenges_campaign_id"),
        "campaign_challenges",
        ["campaign_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_campaign_challenges_challenge_id"),
        "campaign_challenges",
        ["challenge_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_campaign_challenges_status"),
        "campaign_challenges",
        ["status"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_campaign_challenges_status"), table_name="campaign_challenges")
    op.drop_index(op.f("ix_campaign_challenges_challenge_id"), table_name="campaign_challenges")
    op.drop_index(op.f("ix_campaign_challenges_campaign_id"), table_name="campaign_challenges")
    op.drop_index(op.f("ix_campaign_challenges_added_by"), table_name="campaign_challenges")
    op.drop_index(op.f("ix_campaign_challenges_added_at"), table_name="campaign_challenges")
    op.drop_table("campaign_challenges")

    op.drop_index(op.f("ix_campaign_members_user_id"), table_name="campaign_members")
    op.drop_index(op.f("ix_campaign_members_status"), table_name="campaign_members")
    op.drop_index(op.f("ix_campaign_members_role"), table_name="campaign_members")
    op.drop_index(op.f("ix_campaign_members_joined_at"), table_name="campaign_members")
    op.drop_index(op.f("ix_campaign_members_campaign_id"), table_name="campaign_members")
    op.drop_table("campaign_members")

    op.drop_index(op.f("ix_campaigns_title"), table_name="campaigns")
    op.drop_index(op.f("ix_campaigns_status"), table_name="campaigns")
    op.drop_index(op.f("ix_campaigns_state"), table_name="campaigns")
    op.drop_index(op.f("ix_campaigns_start_date"), table_name="campaigns")
    op.drop_index(op.f("ix_campaigns_organization_id"), table_name="campaigns")
    op.drop_index(op.f("ix_campaigns_end_date"), table_name="campaigns")
    op.drop_index(op.f("ix_campaigns_created_by"), table_name="campaigns")
    op.drop_index(op.f("ix_campaigns_created_at"), table_name="campaigns")
    op.drop_index(op.f("ix_campaigns_country"), table_name="campaigns")
    op.drop_index(op.f("ix_campaigns_city"), table_name="campaigns")
    op.drop_table("campaigns")

    op.drop_index(op.f("ix_organization_profiles_user_id"), table_name="organization_profiles")
    op.drop_index(op.f("ix_organization_profiles_status"), table_name="organization_profiles")
    op.drop_index(op.f("ix_organization_profiles_state"), table_name="organization_profiles")
    op.drop_index(op.f("ix_organization_profiles_organization_type"), table_name="organization_profiles")
    op.drop_index(op.f("ix_organization_profiles_organization_name"), table_name="organization_profiles")
    op.drop_index(op.f("ix_organization_profiles_created_at"), table_name="organization_profiles")
    op.drop_index(op.f("ix_organization_profiles_country"), table_name="organization_profiles")
    op.drop_index(op.f("ix_organization_profiles_city"), table_name="organization_profiles")
    op.drop_table("organization_profiles")