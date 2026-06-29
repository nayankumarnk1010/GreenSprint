from datetime import datetime
from typing import Any

from pydantic import BaseModel
from pydantic import Field

from app.core.enums import UserRole


class AdminAuditLogResponse(BaseModel):
    id: str
    actor_user_id: str
    action: str
    target_type: str
    target_id: str | None
    description: str
    metadata: dict[str, Any] | None
    created_at: datetime


class AuditLogListResponse(BaseModel):
    items: list[AdminAuditLogResponse]
    total: int
    limit: int
    offset: int


class PlatformSettingResponse(BaseModel):
    id: str
    setting_key: str
    setting_value: str
    value_type: str
    description: str | None
    updated_by: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }


class PlatformSettingUpdateRequest(BaseModel):
    setting_value: str = Field(..., min_length=1)
    value_type: str = "string"
    description: str | None = None


class AdminDashboardResponse(BaseModel):
    users: dict[str, Any]
    organizations: dict[str, Any]
    campaigns: dict[str, Any]
    submissions: dict[str, Any]
    ai_verification: dict[str, Any]
    community: dict[str, Any]
    esg_reports: dict[str, Any]
    platform_settings: dict[str, Any]


class AdminUserResponse(BaseModel):
    id: str
    email: str
    full_name: str | None
    role: UserRole
    is_active: bool
    is_verified: bool
    created_at: datetime | None
    updated_at: datetime | None

    model_config = {
        "from_attributes": True
    }


class AdminUserListResponse(BaseModel):
    items: list[AdminUserResponse]
    total: int
    limit: int
    offset: int


class AdminUserUpdateRequest(BaseModel):
    full_name: str | None = None
    role: UserRole | None = None
    is_active: bool | None = None
    is_verified: bool | None = None


class AdminOrganizationStatusUpdateRequest(BaseModel):
    status: str
    notes: str | None = None


class AdminModerationDecisionRequest(BaseModel):
    decision: str = Field(
        ...,
        description="APPROVE, REJECT, HIDE, RESTORE, DISMISS, RESOLVE",
    )
    notes: str | None = None


class AdminModerationListResponse(BaseModel):
    items: list[dict[str, Any]]
    total: int
    limit: int
    offset: int