from datetime import datetime
from typing import Any

from pydantic import BaseModel
from pydantic import Field

from app.core.enums import NotificationPriority
from app.core.enums import NotificationReferenceType
from app.core.enums import NotificationStatus
from app.core.enums import NotificationType


class NotificationResponse(BaseModel):
    id: str
    user_id: str
    actor_user_id: str | None
    title: str
    message: str
    notification_type: NotificationType
    status: NotificationStatus
    priority: NotificationPriority
    reference_type: NotificationReferenceType | None
    reference_id: str | None
    action_url: str | None
    metadata: dict[str, Any] | None
    created_at: datetime
    read_at: datetime | None


class NotificationListResponse(BaseModel):
    items: list[NotificationResponse]
    total: int
    unread_count: int
    limit: int
    offset: int


class NotificationUnreadCountResponse(BaseModel):
    unread_count: int


class NotificationPreferenceResponse(BaseModel):
    id: str
    user_id: str
    in_app_enabled: bool
    system_notifications: bool
    submission_updates: bool
    ai_verification_updates: bool
    impact_updates: bool
    reward_updates: bool
    campaign_updates: bool
    community_updates: bool
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }


class NotificationPreferenceUpdateRequest(BaseModel):
    in_app_enabled: bool | None = None
    system_notifications: bool | None = None
    submission_updates: bool | None = None
    ai_verification_updates: bool | None = None
    impact_updates: bool | None = None
    reward_updates: bool | None = None
    campaign_updates: bool | None = None
    community_updates: bool | None = None


class AdminSendNotificationRequest(BaseModel):
    user_id: str
    title: str = Field(..., min_length=2, max_length=255)
    message: str = Field(..., min_length=2)
    notification_type: NotificationType = NotificationType.GENERAL
    priority: NotificationPriority = NotificationPriority.NORMAL
    reference_type: NotificationReferenceType | None = None
    reference_id: str | None = None
    action_url: str | None = None
    metadata: dict[str, Any] | None = None


class CampaignBroadcastRequest(BaseModel):
    title: str = Field(..., min_length=2, max_length=255)
    message: str = Field(..., min_length=2)
    priority: NotificationPriority = NotificationPriority.NORMAL
    action_url: str | None = None
    metadata: dict[str, Any] | None = None


class CampaignBroadcastResponse(BaseModel):
    campaign_id: str
    total_members: int
    notifications_created: int
    message: str