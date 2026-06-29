from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import Query
from fastapi import status

from sqlalchemy.orm import Session

from app.api.dependencies.rbac import require_role
from app.core.enums import UserRole
from app.db.dependencies import get_db
from app.models.user import User
from app.schemas.admin import AdminAuditLogResponse
from app.schemas.admin import AdminDashboardResponse
from app.schemas.admin import AdminModerationDecisionRequest
from app.schemas.admin import AdminModerationListResponse
from app.schemas.admin import AdminOrganizationStatusUpdateRequest
from app.schemas.admin import AdminUserListResponse
from app.schemas.admin import AdminUserResponse
from app.schemas.admin import AdminUserUpdateRequest
from app.schemas.admin import AuditLogListResponse
from app.schemas.admin import PlatformSettingResponse
from app.schemas.admin import PlatformSettingUpdateRequest
from app.services.admin_service import AdminService


router = APIRouter()


@router.get(
    "/dashboard",
    response_model=AdminDashboardResponse,
)
def get_admin_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN)),
):
    return AdminService.get_dashboard(
        db=db,
    )


@router.get(
    "/users",
    response_model=AdminUserListResponse,
)
def list_users(
    role: str | None = Query(default=None),
    is_active: bool | None = Query(default=None),
    search: str | None = Query(default=None),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN)),
):
    try:
        return AdminService.list_users(
            db=db,
            role=role,
            is_active=is_active,
            search=search,
            limit=limit,
            offset=offset,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


@router.patch(
    "/users/{user_id}",
    response_model=AdminUserResponse,
)
def update_user(
    user_id: str,
    payload: AdminUserUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN)),
):
    try:
        return AdminService.update_user(
            db=db,
            current_user=current_user,
            user_id=user_id,
            payload=payload,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.get(
    "/organizations",
)
def list_organizations(
    status_filter: str | None = Query(
        default=None,
        alias="status",
    ),
    search: str | None = Query(default=None),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN)),
):
    try:
        return AdminService.list_organizations(
            db=db,
            status=status_filter,
            search=search,
            limit=limit,
            offset=offset,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


@router.patch(
    "/organizations/{organization_id}/status",
)
def update_organization_status(
    organization_id: str,
    payload: AdminOrganizationStatusUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN)),
):
    try:
        return AdminService.update_organization_status(
            db=db,
            current_user=current_user,
            organization_id=organization_id,
            payload=payload,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


@router.get(
    "/moderation/submissions",
    response_model=AdminModerationListResponse,
)
def list_submission_moderation_queue(
    status_filter: str | None = Query(
        default=None,
        alias="status",
    ),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN)),
):
    try:
        return AdminService.list_submission_moderation_queue(
            db=db,
            status=status_filter,
            limit=limit,
            offset=offset,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


@router.patch(
    "/moderation/submissions/{submission_id}/decision",
)
def decide_submission(
    submission_id: str,
    payload: AdminModerationDecisionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN)),
):
    try:
        return AdminService.decide_submission(
            db=db,
            current_user=current_user,
            submission_id=submission_id,
            payload=payload,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


@router.get(
    "/moderation/community-reports",
    response_model=AdminModerationListResponse,
)
def list_community_reports(
    status_filter: str | None = Query(
        default=None,
        alias="status",
    ),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN)),
):
    try:
        return AdminService.list_community_reports(
            db=db,
            status=status_filter,
            limit=limit,
            offset=offset,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


@router.patch(
    "/moderation/community-reports/{report_id}/decision",
)
def decide_community_report(
    report_id: str,
    payload: AdminModerationDecisionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN)),
):
    try:
        return AdminService.decide_community_report(
            db=db,
            current_user=current_user,
            report_id=report_id,
            payload=payload,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


@router.get(
    "/settings",
    response_model=list[PlatformSettingResponse],
)
def list_platform_settings(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN)),
):
    return AdminService.list_settings(
        db=db,
    )


@router.patch(
    "/settings/{setting_key}",
    response_model=PlatformSettingResponse,
)
def update_platform_setting(
    setting_key: str,
    payload: PlatformSettingUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN)),
):
    return AdminService.update_setting(
        db=db,
        current_user=current_user,
        setting_key=setting_key,
        payload=payload,
    )


@router.get(
    "/audit-logs",
    response_model=AuditLogListResponse,
)
def list_audit_logs(
    action: str | None = Query(default=None),
    target_type: str | None = Query(default=None),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN)),
):
    return AdminService.list_audit_logs(
        db=db,
        action=action,
        target_type=target_type,
        limit=limit,
        offset=offset,
    )