from datetime import datetime

from pydantic import BaseModel
from pydantic import Field

from app.core.enums import SubmissionStatus, SubmissionType


class SubmissionCreate(BaseModel):
    challenge_id: str | None = None

    submission_type: SubmissionType

    title: str = Field(
        min_length=3,
        max_length=255,
    )

    description: str | None = Field(
        default=None,
        max_length=2000,
    )

    latitude: float | None = Field(
        default=None,
        ge=-90,
        le=90,
    )

    longitude: float | None = Field(
        default=None,
        ge=-180,
        le=180,
    )

    location_name: str | None = Field(
        default=None,
        max_length=255,
    )


class SubmissionStatusUpdate(BaseModel):
    status: SubmissionStatus

    admin_review_note: str | None = Field(
        default=None,
        max_length=2000,
    )


class SubmissionResponse(BaseModel):
    id: str
    user_id: str
    challenge_id: str | None
    submission_type: SubmissionType
    title: str
    description: str | None
    latitude: float | None
    longitude: float | None
    location_name: str | None
    status: SubmissionStatus
    admin_review_note: str | None
    submitted_at: datetime
    reviewed_at: datetime | None
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }
