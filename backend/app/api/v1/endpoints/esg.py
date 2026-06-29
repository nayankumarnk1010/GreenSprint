from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import Query
from fastapi import status

from sqlalchemy.orm import Session

from app.api.dependencies.auth import get_current_user
from app.api.dependencies.rbac import require_role
from app.core.enums import ESGReportStatus
from app.core.enums import UserRole
from app.db.dependencies import get_db
from app.models.user import User
from app.schemas.esg import ESGReportDetailResponse
from app.schemas.esg import ESGReportGenerateRequest
from app.schemas.esg import ESGReportListResponse
from app.schemas.esg import ESGSummaryResponse
from app.services.esg_service import ESGService


router = APIRouter()


@router.post(
    "/reports/generate",
    response_model=ESGReportDetailResponse,
    status_code=status.HTTP_201_CREATED,
)
def generate_esg_report(
    payload: ESGReportGenerateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role(
            UserRole.ADMIN,
            UserRole.ORGANIZATION,
        )
    ),
):
    try:
        return ESGService.generate_report(
            db=db,
            current_user=current_user,
            payload=payload,
        )

    except PermissionError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        ) from exc

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


@router.get(
    "/reports",
    response_model=ESGReportListResponse,
)
def list_esg_reports(
    organization_id: str | None = Query(default=None),
    campaign_id: str | None = Query(default=None),
    status_filter: ESGReportStatus | None = Query(
        default=None,
        alias="status",
    ),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role(
            UserRole.ADMIN,
            UserRole.ORGANIZATION,
        )
    ),
):
    try:
        return ESGService.list_reports(
            db=db,
            current_user=current_user,
            organization_id=organization_id,
            campaign_id=campaign_id,
            status_filter=status_filter,
            limit=limit,
            offset=offset,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


@router.get(
    "/reports/{report_id}",
    response_model=ESGReportDetailResponse,
)
def get_esg_report_detail(
    report_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role(
            UserRole.ADMIN,
            UserRole.ORGANIZATION,
        )
    ),
):
    try:
        return ESGService.get_report_detail(
            db=db,
            current_user=current_user,
            report_id=report_id,
        )

    except PermissionError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        ) from exc

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.patch(
    "/reports/{report_id}/publish",
    response_model=ESGReportDetailResponse,
)
def publish_esg_report(
    report_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role(
            UserRole.ADMIN,
            UserRole.ORGANIZATION,
        )
    ),
):
    try:
        return ESGService.publish_report(
            db=db,
            current_user=current_user,
            report_id=report_id,
        )

    except PermissionError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        ) from exc

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.patch(
    "/reports/{report_id}/archive",
    response_model=ESGReportDetailResponse,
)
def archive_esg_report(
    report_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role(
            UserRole.ADMIN,
            UserRole.ORGANIZATION,
        )
    ),
):
    try:
        return ESGService.archive_report(
            db=db,
            current_user=current_user,
            report_id=report_id,
        )

    except PermissionError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        ) from exc

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.get(
    "/organizations/me/summary",
    response_model=ESGSummaryResponse,
)
def get_my_organization_esg_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role(
            UserRole.ORGANIZATION,
            UserRole.ADMIN,
        )
    ),
):
    try:
        return ESGService.organization_summary(
            db=db,
            current_user=current_user,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.get(
    "/campaigns/{campaign_id}/summary",
    response_model=ESGSummaryResponse,
)
def get_campaign_esg_summary(
    campaign_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role(
            UserRole.ORGANIZATION,
            UserRole.ADMIN,
        )
    ),
):
    try:
        return ESGService.campaign_summary(
            db=db,
            current_user=current_user,
            campaign_id=campaign_id,
        )

    except PermissionError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        ) from exc

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.get(
    "/admin/platform-summary",
    response_model=ESGSummaryResponse,
)
def get_platform_esg_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role(
            UserRole.ADMIN,
        )
    ),
):
    return ESGService.admin_platform_summary(
        db=db,
    )