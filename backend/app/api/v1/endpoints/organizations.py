from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import Query
from fastapi import status

from sqlalchemy.orm import Session

from app.api.dependencies.auth import get_current_user
from app.api.dependencies.rbac import require_role
from app.core.enums import UserRole
from app.db.dependencies import get_db
from app.models.user import User
from app.schemas.organization import CampaignChallengeResponse
from app.schemas.organization import CampaignCreateRequest
from app.schemas.organization import CampaignDashboardResponse
from app.schemas.organization import CampaignMemberCreateRequest
from app.schemas.organization import CampaignMemberResponse
from app.schemas.organization import CampaignResponse
from app.schemas.organization import CampaignUpdateRequest
from app.schemas.organization import OrganizationDashboardResponse
from app.schemas.organization import OrganizationProfileCreateRequest
from app.schemas.organization import OrganizationProfileResponse
from app.schemas.organization import OrganizationProfileUpdateRequest
from app.services.organization_service import OrganizationService


router = APIRouter()


@router.post(
    "/profile",
    response_model=OrganizationProfileResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_my_organization_profile(
    payload: OrganizationProfileCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role(
            UserRole.ORGANIZATION,
            UserRole.ADMIN,
        )
    ),
):
    try:
        return OrganizationService.create_my_profile(
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
    "/me",
    response_model=OrganizationProfileResponse,
)
def get_my_organization_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role(
            UserRole.ORGANIZATION,
            UserRole.ADMIN,
        )
    ),
):
    try:
        return OrganizationService.get_my_profile(
            db=db,
            current_user=current_user,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.patch(
    "/me",
    response_model=OrganizationProfileResponse,
)
def update_my_organization_profile(
    payload: OrganizationProfileUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role(
            UserRole.ORGANIZATION,
            UserRole.ADMIN,
        )
    ),
):
    try:
        return OrganizationService.update_my_profile(
            db=db,
            current_user=current_user,
            payload=payload,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.get(
    "/directory",
    response_model=list[OrganizationProfileResponse],
)
def list_organization_directory(
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return OrganizationService.list_organizations(
        db=db,
        current_user=current_user,
        limit=limit,
        offset=offset,
    )


@router.get(
    "/profiles/{organization_id}",
    response_model=OrganizationProfileResponse,
)
def get_organization_profile(
    organization_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return OrganizationService.get_organization_public(
            db=db,
            organization_id=organization_id,
            current_user=current_user,
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
    "/me/dashboard",
    response_model=OrganizationDashboardResponse,
)
def get_my_organization_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role(
            UserRole.ORGANIZATION,
            UserRole.ADMIN,
        )
    ),
):
    try:
        return OrganizationService.get_organization_dashboard(
            db=db,
            current_user=current_user,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.post(
    "/campaigns",
    response_model=CampaignResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_campaign(
    payload: CampaignCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role(
            UserRole.ORGANIZATION,
            UserRole.ADMIN,
        )
    ),
):
    try:
        return OrganizationService.create_campaign(
            db=db,
            current_user=current_user,
            payload=payload,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


@router.get(
    "/campaigns/my",
    response_model=list[CampaignResponse],
)
def list_my_campaigns(
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role(
            UserRole.ORGANIZATION,
            UserRole.ADMIN,
        )
    ),
):
    try:
        return OrganizationService.list_my_campaigns(
            db=db,
            current_user=current_user,
            limit=limit,
            offset=offset,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.get(
    "/campaigns/public",
    response_model=list[CampaignResponse],
)
def list_public_campaigns(
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return OrganizationService.list_public_campaigns(
        db=db,
        limit=limit,
        offset=offset,
    )


@router.get(
    "/campaigns/{campaign_id}",
    response_model=CampaignResponse,
)
def get_campaign_detail(
    campaign_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return OrganizationService.get_campaign_detail(
            db=db,
            campaign_id=campaign_id,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.patch(
    "/campaigns/{campaign_id}",
    response_model=CampaignResponse,
)
def update_campaign(
    campaign_id: str,
    payload: CampaignUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role(
            UserRole.ORGANIZATION,
            UserRole.ADMIN,
        )
    ),
):
    try:
        return OrganizationService.update_campaign(
            db=db,
            current_user=current_user,
            campaign_id=campaign_id,
            payload=payload,
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


@router.post(
    "/campaigns/{campaign_id}/join",
    response_model=CampaignMemberResponse,
    status_code=status.HTTP_201_CREATED,
)
def join_campaign(
    campaign_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        member = OrganizationService.join_campaign(
            db=db,
            current_user=current_user,
            campaign_id=campaign_id,
        )

        return OrganizationService._member_payload(
            db=db,
            member=member,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


@router.post(
    "/campaigns/{campaign_id}/members",
    response_model=CampaignMemberResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_campaign_member(
    campaign_id: str,
    payload: CampaignMemberCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role(
            UserRole.ORGANIZATION,
            UserRole.ADMIN,
        )
    ),
):
    try:
        member = OrganizationService.add_campaign_member(
            db=db,
            current_user=current_user,
            campaign_id=campaign_id,
            payload=payload,
        )

        return OrganizationService._member_payload(
            db=db,
            member=member,
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
    "/campaigns/{campaign_id}/members",
    response_model=list[CampaignMemberResponse],
)
def list_campaign_members(
    campaign_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return OrganizationService.list_campaign_members(
        db=db,
        campaign_id=campaign_id,
    )


@router.delete(
    "/campaigns/{campaign_id}/members/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def remove_campaign_member(
    campaign_id: str,
    user_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role(
            UserRole.ORGANIZATION,
            UserRole.ADMIN,
        )
    ),
):
    try:
        OrganizationService.remove_campaign_member(
            db=db,
            current_user=current_user,
            campaign_id=campaign_id,
            user_id=user_id,
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


@router.post(
    "/campaigns/{campaign_id}/challenges/{challenge_id}",
    response_model=CampaignChallengeResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_challenge_to_campaign(
    campaign_id: str,
    challenge_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role(
            UserRole.ORGANIZATION,
            UserRole.ADMIN,
        )
    ),
):
    try:
        link = OrganizationService.add_challenge_to_campaign(
            db=db,
            current_user=current_user,
            campaign_id=campaign_id,
            challenge_id=challenge_id,
        )

        return OrganizationService._campaign_challenge_payload(
            db=db,
            link=link,
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
    "/campaigns/{campaign_id}/challenges",
    response_model=list[CampaignChallengeResponse],
)
def list_campaign_challenges(
    campaign_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return OrganizationService.list_campaign_challenges(
        db=db,
        campaign_id=campaign_id,
    )


@router.delete(
    "/campaigns/{campaign_id}/challenges/{challenge_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def remove_challenge_from_campaign(
    campaign_id: str,
    challenge_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role(
            UserRole.ORGANIZATION,
            UserRole.ADMIN,
        )
    ),
):
    try:
        OrganizationService.remove_challenge_from_campaign(
            db=db,
            current_user=current_user,
            campaign_id=campaign_id,
            challenge_id=challenge_id,
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
    "/campaigns/{campaign_id}/dashboard",
    response_model=CampaignDashboardResponse,
)
def get_campaign_dashboard(
    campaign_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return OrganizationService.get_campaign_dashboard(
            db=db,
            campaign_id=campaign_id,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc