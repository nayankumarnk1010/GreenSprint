from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import Query
from fastapi import status

from sqlalchemy.orm import Session

from app.api.dependencies.auth import get_current_user
from app.api.dependencies.rbac import require_role
from app.core.enums import NotificationStatus
from app.core.enums import NotificationType
from app.core.enums import UserRole
from app.db.dependencies import get_db
from app.models.user import User
from app.schemas.notification import AdminSendNotificationRequest
from app.schemas.notification import CampaignBroadcastRequest
from app.schemas.notification import CampaignBroadcastResponse
from app.schemas.notification import NotificationListResponse
from app.schemas.notification import NotificationPreferenceResponse
from app.schemas.notification import NotificationPreferenceUpdateRequest
from app.schemas.notification import NotificationResponse
from app.schemas.notification import NotificationUnreadCountResponse
from app.services.notification_service import NotificationService


router = APIRouter()


@router.get(
    "",
    response_model=NotificationListResponse,
)
def list_my_notifications(
    status_filter: NotificationStatus | None = Query(
        default=None,
        alias="status",
    ),
    type_filter: NotificationType | None = Query(
        default=None,
        alias="type",
    ),
    include_archived: bool = Query(default=False),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return NotificationService.list_my_notifications(
        db=db,
        current_user=current_user,
        status_filter=status_filter,
        type_filter=type_filter,
        include_archived=include_archived,
        limit=limit,
        offset=offset,
    )


@router.get(
    "/unread-count",
    response_model=NotificationUnreadCountResponse,
)
def get_unread_count(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return {
        "unread_count": NotificationService.get_unread_count(
            db=db,
            current_user=current_user,
        )
    }


@router.patch(
    "/{notification_id}/read",
    response_model=NotificationResponse,
)
def mark_notification_as_read(
    notification_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return NotificationService.mark_as_read(
            db=db,
            current_user=current_user,
            notification_id=notification_id,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.patch(
    "/read-all",
)
def mark_all_notifications_as_read(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return NotificationService.mark_all_as_read(
        db=db,
        current_user=current_user,
    )


@router.patch(
    "/{notification_id}/archive",
    response_model=NotificationResponse,
)
def archive_notification(
    notification_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return NotificationService.archive_notification(
            db=db,
            current_user=current_user,
            notification_id=notification_id,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.get(
    "/preferences",
    response_model=NotificationPreferenceResponse,
)
def get_my_notification_preferences(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return NotificationService.get_or_create_preferences(
        db=db,
        user_id=current_user.id,
    )


@router.patch(
    "/preferences",
    response_model=NotificationPreferenceResponse,
)
def update_my_notification_preferences(
    payload: NotificationPreferenceUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return NotificationService.update_preferences(
        db=db,
        current_user=current_user,
        payload=payload,
    )


@router.post(
    "/admin/send-to-user",
    response_model=NotificationResponse,
    status_code=status.HTTP_201_CREATED,
)
def admin_send_notification_to_user(
    payload: AdminSendNotificationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role(
            UserRole.ADMIN,
            UserRole.ORGANIZATION,
        )
    ),
):
    try:
        return NotificationService.admin_send_to_user(
            db=db,
            current_user=current_user,
            payload=payload,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.post(
    "/admin/campaigns/{campaign_id}/broadcast",
    response_model=CampaignBroadcastResponse,
)
def broadcast_notification_to_campaign(
    campaign_id: str,
    payload: CampaignBroadcastRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role(
            UserRole.ADMIN,
            UserRole.ORGANIZATION,
        )
    ),
):
    try:
        return NotificationService.broadcast_to_campaign(
            db=db,
            current_user=current_user,
            campaign_id=campaign_id,
            payload=payload,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.post(
    "/events/submissions/{submission_id}/status",
)
def notify_submission_status(
    submission_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role(
            UserRole.ADMIN,
            UserRole.ORGANIZATION,
        )
    ),
):
    try:
        return NotificationService.notify_submission_status(
            db=db,
            current_user=current_user,
            submission_id=submission_id,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc