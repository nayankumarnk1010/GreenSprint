from datetime import datetime

from pydantic import BaseModel
from pydantic import Field

from app.core.enums import CommunityCommentStatus
from app.core.enums import CommunityPostStatus
from app.core.enums import CommunityPostType
from app.core.enums import CommunityPostVisibility
from app.core.enums import CommunityReportReason
from app.core.enums import CommunityReportStatus
from app.core.enums import SubmissionStatus
from app.core.enums import SubmissionType


class CommunityImpactSummary(BaseModel):
    co2e_saved_kg: float = 0.0
    waste_diverted_kg: float = 0.0
    water_saved_liters: float = 0.0
    energy_saved_kwh: float = 0.0
    trees_planted: float = 0.0
    biodiversity_score: float = 0.0


class CommunitySubmissionSummary(BaseModel):
    id: str
    title: str
    submission_type: SubmissionType
    status: SubmissionStatus
    latitude: float | None = None
    longitude: float | None = None
    location_name: str | None = None
    impact: CommunityImpactSummary

class CommunityPostMediaResponse(BaseModel):
    id: str
    post_id: str
    user_id: str
    media_type: str
    original_file_name: str
    stored_file_name: str
    file_path: str
    media_url: str
    mime_type: str
    file_size_bytes: int
    file_sha256: str | None
    alt_text: str | None
    created_at: datetime

    model_config = {
        "from_attributes": True
    }
    
    
class CommunityPostCreateRequest(BaseModel):
    content: str = Field(..., min_length=1, max_length=2000)
    submission_id: str | None = None
    challenge_id: str | None = None
    visibility: CommunityPostVisibility = CommunityPostVisibility.PUBLIC


class CommunityPostUpdateRequest(BaseModel):
    content: str | None = Field(default=None, min_length=1, max_length=2000)
    visibility: CommunityPostVisibility | None = None


class CommunityPostResponse(BaseModel):
    id: str
    user_id: str
    user_full_name: str | None

    submission_id: str | None
    challenge_id: str | None

    content: str
    post_type: CommunityPostType
    visibility: CommunityPostVisibility
    status: CommunityPostStatus

    likes_count: int
    comments_count: int
    reports_count: int
    liked_by_current_user: bool = False

    submission: CommunitySubmissionSummary | None = None
    media: list[CommunityPostMediaResponse] = Field(default_factory=list)

    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }


class CommunityCommentCreateRequest(BaseModel):
    content: str = Field(..., min_length=1, max_length=1000)


class CommunityCommentResponse(BaseModel):
    id: str
    post_id: str
    user_id: str
    user_full_name: str | None
    content: str
    status: CommunityCommentStatus
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }


class CommunityLikeResponse(BaseModel):
    post_id: str
    liked: bool
    likes_count: int
    message: str


class CommunityReportCreateRequest(BaseModel):
    reason: CommunityReportReason
    details: str | None = Field(default=None, max_length=1000)


class CommunityReportResponse(BaseModel):
    id: str
    post_id: str
    user_id: str
    reason: CommunityReportReason
    details: str | None
    status: CommunityReportStatus
    created_at: datetime
    reviewed_at: datetime | None

    model_config = {
        "from_attributes": True
    }


class CommunityFeedResponse(BaseModel):
    items: list[CommunityPostResponse]
    total: int
    limit: int
    offset: int