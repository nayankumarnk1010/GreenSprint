from datetime import datetime

from pydantic import BaseModel
from pydantic import Field

from app.core.enums import CampaignChallengeStatus
from app.core.enums import CampaignMemberRole
from app.core.enums import CampaignMemberStatus
from app.core.enums import CampaignStatus
from app.core.enums import ChallengeCategory
from app.core.enums import ChallengeDifficulty
from app.core.enums import ChallengeStatus
from app.core.enums import ChallengeType
from app.core.enums import OrganizationProfileStatus
from app.core.enums import OrganizationType


class OrganizationProfileCreateRequest(BaseModel):
    organization_name: str = Field(..., min_length=2, max_length=255)
    organization_type: OrganizationType = OrganizationType.OTHER
    description: str | None = None
    website_url: str | None = None
    contact_email: str | None = None
    contact_phone: str | None = None
    city: str | None = None
    state: str | None = None
    country: str = "India"


class OrganizationProfileUpdateRequest(BaseModel):
    organization_name: str | None = Field(default=None, min_length=2, max_length=255)
    organization_type: OrganizationType | None = None
    description: str | None = None
    website_url: str | None = None
    contact_email: str | None = None
    contact_phone: str | None = None
    city: str | None = None
    state: str | None = None
    country: str | None = None
    status: OrganizationProfileStatus | None = None


class OrganizationProfileResponse(BaseModel):
    id: str
    user_id: str
    organization_name: str
    organization_type: OrganizationType
    description: str | None
    website_url: str | None
    contact_email: str | None
    contact_phone: str | None
    city: str | None
    state: str | None
    country: str
    status: OrganizationProfileStatus
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }


class CampaignCreateRequest(BaseModel):
    title: str = Field(..., min_length=3, max_length=255)
    description: str = Field(..., min_length=5)
    status: CampaignStatus = CampaignStatus.DRAFT
    start_date: datetime | None = None
    end_date: datetime | None = None
    target_participants: int = 0
    target_co2e_saved_kg: int = 0
    target_trees_planted: int = 0
    city: str | None = None
    state: str | None = None
    country: str = "India"


class CampaignUpdateRequest(BaseModel):
    title: str | None = Field(default=None, min_length=3, max_length=255)
    description: str | None = Field(default=None, min_length=5)
    status: CampaignStatus | None = None
    start_date: datetime | None = None
    end_date: datetime | None = None
    target_participants: int | None = None
    target_co2e_saved_kg: int | None = None
    target_trees_planted: int | None = None
    city: str | None = None
    state: str | None = None
    country: str | None = None


class CampaignResponse(BaseModel):
    id: str
    organization_id: str
    created_by: str
    title: str
    description: str
    status: CampaignStatus
    start_date: datetime | None
    end_date: datetime | None
    target_participants: int
    target_co2e_saved_kg: int
    target_trees_planted: int
    city: str | None
    state: str | None
    country: str
    members_count: int = 0
    challenges_count: int = 0
    submissions_count: int = 0
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }


class CampaignMemberCreateRequest(BaseModel):
    user_id: str
    role: CampaignMemberRole = CampaignMemberRole.PARTICIPANT


class CampaignMemberResponse(BaseModel):
    id: str
    campaign_id: str
    user_id: str
    user_full_name: str | None
    user_email: str | None
    role: CampaignMemberRole
    status: CampaignMemberStatus
    joined_at: datetime

    model_config = {
        "from_attributes": True
    }


class CampaignChallengeResponse(BaseModel):
    id: str
    campaign_id: str
    challenge_id: str
    challenge_title: str | None
    category: ChallengeCategory | None
    challenge_type: ChallengeType | None
    difficulty: ChallengeDifficulty | None
    challenge_status: ChallengeStatus | None
    status: CampaignChallengeStatus
    added_by: str
    added_at: datetime

    model_config = {
        "from_attributes": True
    }


class OrganizationDashboardResponse(BaseModel):
    organization_id: str
    organization_name: str
    campaigns_count: int
    active_campaigns_count: int
    members_count: int
    linked_challenges_count: int
    submissions_count: int
    unique_participants_count: int
    community_posts_count: int
    total_co2e_saved_kg: float
    total_trees_planted: float
    total_biodiversity_score: float


class CampaignDashboardResponse(BaseModel):
    campaign_id: str
    campaign_title: str
    status: CampaignStatus
    members_count: int
    linked_challenges_count: int
    submissions_count: int
    unique_participants_count: int
    community_posts_count: int
    total_co2e_saved_kg: float
    total_trees_planted: float
    total_biodiversity_score: float
    target_participants: int
    target_co2e_saved_kg: int
    target_trees_planted: int
    participant_progress_percent: float
    co2e_progress_percent: float
    tree_progress_percent: float