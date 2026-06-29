from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import Query
from fastapi import status
from fastapi import File
from fastapi import Form
from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.api.dependencies.auth import get_current_user
from app.api.dependencies.rbac import require_role
from app.core.enums import CommunityReportStatus
from app.core.enums import UserRole
from app.db.dependencies import get_db
from app.models.user import User
from app.schemas.community import CommunityCommentCreateRequest
from app.schemas.community import CommunityCommentResponse
from app.schemas.community import CommunityFeedResponse
from app.schemas.community import CommunityLikeResponse
from app.schemas.community import CommunityPostCreateRequest
from app.schemas.community import CommunityPostResponse
from app.schemas.community import CommunityPostMediaResponse
from app.schemas.community import CommunityPostUpdateRequest
from app.schemas.community import CommunityReportCreateRequest
from app.schemas.community import CommunityReportResponse
from app.services.community_service import CommunityService

router = APIRouter()


@router.post(
    "/posts",
    response_model=CommunityPostResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_post(
    payload: CommunityPostCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return CommunityService.create_post(
            db=db,
            current_user=current_user,
            content=payload.content,
            submission_id=payload.submission_id,
            challenge_id=payload.challenge_id,
            visibility=payload.visibility,
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
    "/feed",
    response_model=CommunityFeedResponse,
)
def get_community_feed(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return CommunityService.get_feed(
        db=db,
        current_user=current_user,
        limit=limit,
        offset=offset,
    )


@router.get(
    "/posts/{post_id}",
    response_model=CommunityPostResponse,
)
def get_post_detail(
    post_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return CommunityService.get_post_detail(
            db=db,
            post_id=post_id,
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


@router.post(
    "/posts/{post_id}/media",
    response_model=CommunityPostMediaResponse,
    status_code=status.HTTP_201_CREATED,
)
def upload_post_media(
    post_id: str,
    file: UploadFile = File(...),
    alt_text: str | None = Form(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return CommunityService.upload_post_media(
            db=db,
            post_id=post_id,
            current_user=current_user,
            file=file,
            alt_text=alt_text,
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
    "/posts/{post_id}/media",
    response_model=list[CommunityPostMediaResponse],
)
def get_post_media(
    post_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        CommunityService.get_post_detail(
            db=db,
            post_id=post_id,
            current_user=current_user,
        )

        return CommunityService.get_post_media(
            db=db,
            post_id=post_id,
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
    "/posts/{post_id}",
    response_model=CommunityPostResponse,
)
def update_post(
    post_id: str,
    payload: CommunityPostUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return CommunityService.update_post(
            db=db,
            post_id=post_id,
            current_user=current_user,
            content=payload.content,
            visibility=payload.visibility,
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


@router.delete(
    "/posts/{post_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_post(
    post_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        CommunityService.delete_post(
            db=db,
            post_id=post_id,
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
    "/users/me/timeline",
    response_model=CommunityFeedResponse,
)
def get_my_timeline(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return CommunityService.get_user_timeline(
        db=db,
        current_user=current_user,
        target_user_id=current_user.id,
        limit=limit,
        offset=offset,
    )


@router.get(
    "/users/{user_id}/timeline",
    response_model=CommunityFeedResponse,
)
def get_user_timeline(
    user_id: str,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return CommunityService.get_user_timeline(
        db=db,
        current_user=current_user,
        target_user_id=user_id,
        limit=limit,
        offset=offset,
    )


@router.get(
    "/challenges/{challenge_id}/feed",
    response_model=CommunityFeedResponse,
)
def get_challenge_feed(
    challenge_id: str,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return CommunityService.get_challenge_feed(
        db=db,
        current_user=current_user,
        challenge_id=challenge_id,
        limit=limit,
        offset=offset,
    )


@router.post(
    "/posts/{post_id}/like",
    response_model=CommunityLikeResponse,
)
def like_post(
    post_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return CommunityService.like_post(
            db=db,
            post_id=post_id,
            current_user=current_user,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.delete(
    "/posts/{post_id}/like",
    response_model=CommunityLikeResponse,
)
def unlike_post(
    post_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return CommunityService.unlike_post(
            db=db,
            post_id=post_id,
            current_user=current_user,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.post(
    "/posts/{post_id}/comments",
    response_model=CommunityCommentResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_comment(
    post_id: str,
    payload: CommunityCommentCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return CommunityService.add_comment(
            db=db,
            post_id=post_id,
            current_user=current_user,
            content=payload.content,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.get(
    "/posts/{post_id}/comments",
    response_model=list[CommunityCommentResponse],
)
def get_comments(
    post_id: str,
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return CommunityService.get_comments(
        db=db,
        post_id=post_id,
        limit=limit,
        offset=offset,
    )


@router.post(
    "/posts/{post_id}/report",
    response_model=CommunityReportResponse,
    status_code=status.HTTP_201_CREATED,
)
def report_post(
    post_id: str,
    payload: CommunityReportCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return CommunityService.report_post(
            db=db,
            post_id=post_id,
            current_user=current_user,
            reason=payload.reason,
            details=payload.details,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.get(
    "/admin/reports",
    response_model=list[CommunityReportResponse],
)
def get_community_reports(
    status_filter: CommunityReportStatus | None = Query(
        default=None,
        alias="status",
    ),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role(
            UserRole.ADMIN,
            UserRole.ORGANIZATION,
        )
    ),
):
    return CommunityService.get_reports(
        db=db,
        status_filter=status_filter,
        limit=limit,
        offset=offset,
    )


@router.patch(
    "/admin/posts/{post_id}/hide",
    response_model=CommunityPostResponse,
)
def hide_post_admin(
    post_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role(
            UserRole.ADMIN,
            UserRole.ORGANIZATION,
        )
    ),
):
    try:
        post = CommunityService.hide_post(
            db=db,
            post_id=post_id,
        )

        return CommunityService.get_post_detail(
            db=db,
            post_id=post.id,
            current_user=current_user,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.patch(
    "/admin/posts/{post_id}/restore",
    response_model=CommunityPostResponse,
)
def restore_post_admin(
    post_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role(
            UserRole.ADMIN,
            UserRole.ORGANIZATION,
        )
    ),
):
    try:
        post = CommunityService.restore_post(
            db=db,
            post_id=post_id,
        )

        return CommunityService.get_post_detail(
            db=db,
            post_id=post.id,
            current_user=current_user,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
