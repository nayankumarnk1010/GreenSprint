from datetime import datetime

from sqlalchemy.orm import Session

from app.core.enums import CommunityCommentStatus
from app.core.enums import CommunityPostStatus
from app.core.enums import CommunityPostType
from app.core.enums import CommunityPostVisibility
from app.core.enums import CommunityReportStatus
from app.core.enums import UserRole
from app.models.community_comment import CommunityComment
from app.models.community_like import CommunityLike
from app.models.community_post import CommunityPost
from app.models.community_report import CommunityReport
from app.models.impact_metric import ImpactMetric
from app.models.submission import Submission
from app.models.user import User
import hashlib
import os
import uuid

from fastapi import UploadFile

from app.core.config import settings
from app.core.enums import MediaType
from app.models.community_post_media import CommunityPostMedia


class CommunityService:
    """
    Free/local community and social feed service.

    This module creates a social layer for GreenSprint:
    - public feed
    - user timeline
    - challenge feed
    - likes
    - comments
    - post reports
    - basic admin moderation
    """

    @staticmethod
    def _safe_file_extension(filename: str) -> str:
        _, extension = os.path.splitext(filename or "")

        extension = extension.lower().strip()

        allowed_extensions = {
            ".jpg",
            ".jpeg",
            ".png",
            ".webp",
        }

        if extension not in allowed_extensions:
            raise ValueError("Only JPG, JPEG, PNG, and WEBP image files are allowed.")

        return extension

    @staticmethod
    def _validate_image_upload(file: UploadFile) -> None:
        allowed_mime_types = {
            "image/jpeg",
            "image/png",
            "image/webp",
        }

        if file.content_type not in allowed_mime_types:
            raise ValueError("Only image uploads are allowed for community posts.")

    @staticmethod
    def _community_post_media_dir(post_id: str) -> str:
        return os.path.join(
            settings.MEDIA_STORAGE_DIR,
            "community",
            "posts",
            post_id,
        )

    @staticmethod
    def _media_payload(media: CommunityPostMedia) -> dict:
        return {
            "id": media.id,
            "post_id": media.post_id,
            "user_id": media.user_id,
            "media_type": (
                media.media_type.value
                if hasattr(media.media_type, "value")
                else str(media.media_type)
            ),
            "original_file_name": media.original_file_name,
            "stored_file_name": media.stored_file_name,
            "file_path": media.file_path,
            "media_url": media.media_url,
            "mime_type": media.mime_type,
            "file_size_bytes": media.file_size_bytes,
            "file_sha256": media.file_sha256,
            "alt_text": media.alt_text,
            "created_at": media.created_at,
        }

    @staticmethod
    def get_post_media(
        db: Session,
        post_id: str,
    ) -> list[dict]:
        media_items = (
            db.query(CommunityPostMedia)
            .filter(CommunityPostMedia.post_id == post_id)
            .order_by(CommunityPostMedia.created_at.asc())
            .all()
        )

        return [CommunityService._media_payload(media) for media in media_items]

    @staticmethod
    def upload_post_media(
        db: Session,
        post_id: str,
        current_user: User,
        file: UploadFile,
        alt_text: str | None = None,
    ) -> dict:
        post = CommunityService._get_post(
            db=db,
            post_id=post_id,
        )

        if not post or post.status == CommunityPostStatus.DELETED:
            raise ValueError("Post not found")

        if not CommunityService._can_modify_post(
            post=post,
            user=current_user,
        ):
            raise PermissionError(
                "You do not have permission to upload media to this post"
            )

        CommunityService._validate_image_upload(file=file)

        extension = CommunityService._safe_file_extension(file.filename or "")

        upload_dir = CommunityService._community_post_media_dir(
            post_id=post_id,
        )

        os.makedirs(upload_dir, exist_ok=True)

        stored_file_name = f"{uuid.uuid4()}{extension}"

        file_path = os.path.join(
            upload_dir,
            stored_file_name,
        )

        max_size_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024

        file_size = 0
        sha256_hash = hashlib.sha256()

        try:
            with open(file_path, "wb") as buffer:
                while True:
                    chunk = file.file.read(1024 * 1024)

                    if not chunk:
                        break

                    file_size += len(chunk)

                    if file_size > max_size_bytes:
                        buffer.close()

                        if os.path.exists(file_path):
                            os.remove(file_path)

                        raise ValueError(
                            f"File size exceeds {settings.MAX_UPLOAD_SIZE_MB} MB."
                        )

                    sha256_hash.update(chunk)
                    buffer.write(chunk)

        finally:
            file.file.close()

        normalized_path = file_path.replace("\\", "/")

        media_url = f"/{normalized_path}"

        media = CommunityPostMedia(
            post_id=post.id,
            user_id=current_user.id,
            media_type=MediaType.IMAGE,
            original_file_name=file.filename or stored_file_name,
            stored_file_name=stored_file_name,
            file_path=normalized_path,
            media_url=media_url,
            mime_type=file.content_type or "application/octet-stream",
            file_size_bytes=file_size,
            file_sha256=sha256_hash.hexdigest(),
            alt_text=alt_text,
        )

        db.add(media)
        db.commit()
        db.refresh(media)

        return CommunityService._media_payload(media)

    @staticmethod
    def _round(value: float) -> float:
        return round(float(value or 0.0), 3)

    @staticmethod
    def _is_admin_or_org(user: User) -> bool:
        return user.role in {
            UserRole.ADMIN,
            UserRole.ORGANIZATION,
        }

    @staticmethod
    def _can_modify_post(
        post: CommunityPost,
        user: User,
    ) -> bool:
        if CommunityService._is_admin_or_org(user):
            return True

        return post.user_id == user.id

    @staticmethod
    def _get_post(
        db: Session,
        post_id: str,
    ) -> CommunityPost | None:
        return db.query(CommunityPost).filter(CommunityPost.id == post_id).first()

    @staticmethod
    def _get_active_post(
        db: Session,
        post_id: str,
    ) -> CommunityPost | None:
        return (
            db.query(CommunityPost)
            .filter(CommunityPost.id == post_id)
            .filter(CommunityPost.status == CommunityPostStatus.ACTIVE)
            .first()
        )

    @staticmethod
    def _get_submission(
        db: Session,
        submission_id: str,
    ) -> Submission | None:
        return db.query(Submission).filter(Submission.id == submission_id).first()

    @staticmethod
    def _get_user_names(
        db: Session,
        user_ids: list[str],
    ) -> dict[str, str | None]:
        if not user_ids:
            return {}

        users = db.query(User).filter(User.id.in_(user_ids)).all()

        return {user.id: user.full_name for user in users}

    @staticmethod
    def _get_liked_post_ids(
        db: Session,
        current_user_id: str,
        post_ids: list[str],
    ) -> set[str]:
        if not post_ids:
            return set()

        likes = (
            db.query(CommunityLike)
            .filter(CommunityLike.user_id == current_user_id)
            .filter(CommunityLike.post_id.in_(post_ids))
            .all()
        )

        return {like.post_id for like in likes}

    @staticmethod
    def _impact_payload(
        impact_metric: ImpactMetric | None,
    ) -> dict:
        if not impact_metric:
            return {
                "co2e_saved_kg": 0.0,
                "waste_diverted_kg": 0.0,
                "water_saved_liters": 0.0,
                "energy_saved_kwh": 0.0,
                "trees_planted": 0.0,
                "biodiversity_score": 0.0,
            }

        return {
            "co2e_saved_kg": CommunityService._round(impact_metric.co2e_saved_kg),
            "waste_diverted_kg": CommunityService._round(
                impact_metric.waste_diverted_kg
            ),
            "water_saved_liters": CommunityService._round(
                impact_metric.water_saved_liters
            ),
            "energy_saved_kwh": CommunityService._round(impact_metric.energy_saved_kwh),
            "trees_planted": CommunityService._round(impact_metric.trees_planted),
            "biodiversity_score": CommunityService._round(
                impact_metric.biodiversity_score
            ),
        }

    @staticmethod
    def _submission_payload(
        db: Session,
        submission_id: str | None,
    ) -> dict | None:
        if not submission_id:
            return None

        submission = CommunityService._get_submission(
            db=db,
            submission_id=submission_id,
        )

        if not submission:
            return None

        impact_metric = (
            db.query(ImpactMetric)
            .filter(ImpactMetric.submission_id == submission.id)
            .first()
        )

        return {
            "id": submission.id,
            "title": submission.title,
            "submission_type": submission.submission_type,
            "status": submission.status,
            "latitude": submission.latitude,
            "longitude": submission.longitude,
            "location_name": submission.location_name,
            "impact": CommunityService._impact_payload(impact_metric),
        }

    @staticmethod
    def _post_payload(
        db: Session,
        post: CommunityPost,
        user_full_name: str | None,
        liked_by_current_user: bool,
    ) -> dict:
        return {
            "id": post.id,
            "user_id": post.user_id,
            "user_full_name": user_full_name,
            "submission_id": post.submission_id,
            "challenge_id": post.challenge_id,
            "content": post.content,
            "post_type": post.post_type,
            "visibility": post.visibility,
            "status": post.status,
            "likes_count": post.likes_count,
            "comments_count": post.comments_count,
            "reports_count": post.reports_count,
            "liked_by_current_user": liked_by_current_user,
            "submission": CommunityService._submission_payload(
                db=db,
                submission_id=post.submission_id,
            ),
            "media": CommunityService.get_post_media(
                db=db,
                post_id=post.id,
            ),
            "created_at": post.created_at,
            "updated_at": post.updated_at,
        }

    @staticmethod
    def _posts_payload(
        db: Session,
        posts: list[CommunityPost],
        current_user_id: str,
    ) -> list[dict]:
        user_ids = list({post.user_id for post in posts})

        post_ids = [post.id for post in posts]

        user_names = CommunityService._get_user_names(
            db=db,
            user_ids=user_ids,
        )

        liked_post_ids = CommunityService._get_liked_post_ids(
            db=db,
            current_user_id=current_user_id,
            post_ids=post_ids,
        )

        return [
            CommunityService._post_payload(
                db=db,
                post=post,
                user_full_name=user_names.get(post.user_id),
                liked_by_current_user=post.id in liked_post_ids,
            )
            for post in posts
        ]

    @staticmethod
    def create_post(
        db: Session,
        current_user: User,
        content: str,
        submission_id: str | None = None,
        challenge_id: str | None = None,
        visibility: CommunityPostVisibility = CommunityPostVisibility.PUBLIC,
    ) -> dict:
        post_type = CommunityPostType.GENERAL

        if submission_id:
            submission = CommunityService._get_submission(
                db=db,
                submission_id=submission_id,
            )

            if not submission:
                raise ValueError("Submission not found")

            if (
                submission.user_id != current_user.id
                and not CommunityService._is_admin_or_org(current_user)
            ):
                raise PermissionError("You can only share your own submission")

            challenge_id = submission.challenge_id
            post_type = CommunityPostType.SUBMISSION_SHARE

        post = CommunityPost(
            user_id=current_user.id,
            submission_id=submission_id,
            challenge_id=challenge_id,
            content=content,
            post_type=post_type,
            visibility=visibility,
            status=CommunityPostStatus.ACTIVE,
            likes_count=0,
            comments_count=0,
            reports_count=0,
        )

        db.add(post)
        db.commit()
        db.refresh(post)

        return CommunityService._post_payload(
            db=db,
            post=post,
            user_full_name=current_user.full_name,
            liked_by_current_user=False,
        )

    @staticmethod
    def get_feed(
        db: Session,
        current_user: User,
        limit: int = 20,
        offset: int = 0,
    ) -> dict:
        limit = max(1, min(limit, 100))
        offset = max(0, offset)

        query = (
            db.query(CommunityPost)
            .filter(CommunityPost.status == CommunityPostStatus.ACTIVE)
            .filter(
                CommunityPost.visibility.in_(
                    [
                        CommunityPostVisibility.PUBLIC,
                        CommunityPostVisibility.CHALLENGE_ONLY,
                    ]
                )
            )
        )

        total = query.count()

        posts = (
            query.order_by(CommunityPost.created_at.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )

        return {
            "items": CommunityService._posts_payload(
                db=db,
                posts=posts,
                current_user_id=current_user.id,
            ),
            "total": total,
            "limit": limit,
            "offset": offset,
        }

    @staticmethod
    def get_post_detail(
        db: Session,
        post_id: str,
        current_user: User,
    ) -> dict:
        post = CommunityService._get_post(
            db=db,
            post_id=post_id,
        )

        if not post or post.status == CommunityPostStatus.DELETED:
            raise ValueError("Post not found")

        if (
            post.status == CommunityPostStatus.HIDDEN
            and not CommunityService._can_modify_post(post, current_user)
        ):
            raise PermissionError("You do not have permission to view this post")

        if (
            post.visibility == CommunityPostVisibility.PRIVATE
            and post.user_id != current_user.id
            and not CommunityService._is_admin_or_org(current_user)
        ):
            raise PermissionError("You do not have permission to view this post")

        user_names = CommunityService._get_user_names(
            db=db,
            user_ids=[post.user_id],
        )

        liked_post_ids = CommunityService._get_liked_post_ids(
            db=db,
            current_user_id=current_user.id,
            post_ids=[post.id],
        )

        return CommunityService._post_payload(
            db=db,
            post=post,
            user_full_name=user_names.get(post.user_id),
            liked_by_current_user=post.id in liked_post_ids,
        )

    @staticmethod
    def get_user_timeline(
        db: Session,
        current_user: User,
        target_user_id: str,
        limit: int = 20,
        offset: int = 0,
    ) -> dict:
        limit = max(1, min(limit, 100))
        offset = max(0, offset)

        query = (
            db.query(CommunityPost)
            .filter(CommunityPost.user_id == target_user_id)
            .filter(CommunityPost.status == CommunityPostStatus.ACTIVE)
        )

        if target_user_id != current_user.id and not CommunityService._is_admin_or_org(
            current_user
        ):
            query = query.filter(
                CommunityPost.visibility.in_(
                    [
                        CommunityPostVisibility.PUBLIC,
                        CommunityPostVisibility.CHALLENGE_ONLY,
                    ]
                )
            )

        total = query.count()

        posts = (
            query.order_by(CommunityPost.created_at.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )

        return {
            "items": CommunityService._posts_payload(
                db=db,
                posts=posts,
                current_user_id=current_user.id,
            ),
            "total": total,
            "limit": limit,
            "offset": offset,
        }

    @staticmethod
    def get_challenge_feed(
        db: Session,
        current_user: User,
        challenge_id: str,
        limit: int = 20,
        offset: int = 0,
    ) -> dict:
        limit = max(1, min(limit, 100))
        offset = max(0, offset)

        query = (
            db.query(CommunityPost)
            .filter(CommunityPost.challenge_id == challenge_id)
            .filter(CommunityPost.status == CommunityPostStatus.ACTIVE)
            .filter(
                CommunityPost.visibility.in_(
                    [
                        CommunityPostVisibility.PUBLIC,
                        CommunityPostVisibility.CHALLENGE_ONLY,
                    ]
                )
            )
        )

        total = query.count()

        posts = (
            query.order_by(CommunityPost.created_at.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )

        return {
            "items": CommunityService._posts_payload(
                db=db,
                posts=posts,
                current_user_id=current_user.id,
            ),
            "total": total,
            "limit": limit,
            "offset": offset,
        }

    @staticmethod
    def update_post(
        db: Session,
        post_id: str,
        current_user: User,
        content: str | None = None,
        visibility: CommunityPostVisibility | None = None,
    ) -> dict:
        post = CommunityService._get_post(
            db=db,
            post_id=post_id,
        )

        if not post or post.status == CommunityPostStatus.DELETED:
            raise ValueError("Post not found")

        if not CommunityService._can_modify_post(post, current_user):
            raise PermissionError("You do not have permission to update this post")

        if content is not None:
            post.content = content

        if visibility is not None:
            post.visibility = visibility

        db.commit()
        db.refresh(post)

        return CommunityService.get_post_detail(
            db=db,
            post_id=post.id,
            current_user=current_user,
        )

    @staticmethod
    def delete_post(
        db: Session,
        post_id: str,
        current_user: User,
    ) -> None:
        post = CommunityService._get_post(
            db=db,
            post_id=post_id,
        )

        if not post or post.status == CommunityPostStatus.DELETED:
            raise ValueError("Post not found")

        if not CommunityService._can_modify_post(post, current_user):
            raise PermissionError("You do not have permission to delete this post")

        post.status = CommunityPostStatus.DELETED
        db.commit()

    @staticmethod
    def like_post(
        db: Session,
        post_id: str,
        current_user: User,
    ) -> dict:
        post = CommunityService._get_active_post(
            db=db,
            post_id=post_id,
        )

        if not post:
            raise ValueError("Post not found")

        existing_like = (
            db.query(CommunityLike)
            .filter(CommunityLike.post_id == post_id)
            .filter(CommunityLike.user_id == current_user.id)
            .first()
        )

        if existing_like:
            return {
                "post_id": post_id,
                "liked": True,
                "likes_count": post.likes_count,
                "message": "Post already liked.",
            }

        like = CommunityLike(
            post_id=post_id,
            user_id=current_user.id,
        )

        db.add(like)
        post.likes_count += 1
        db.commit()
        db.refresh(post)

        return {
            "post_id": post_id,
            "liked": True,
            "likes_count": post.likes_count,
            "message": "Post liked successfully.",
        }

    @staticmethod
    def unlike_post(
        db: Session,
        post_id: str,
        current_user: User,
    ) -> dict:
        post = CommunityService._get_active_post(
            db=db,
            post_id=post_id,
        )

        if not post:
            raise ValueError("Post not found")

        existing_like = (
            db.query(CommunityLike)
            .filter(CommunityLike.post_id == post_id)
            .filter(CommunityLike.user_id == current_user.id)
            .first()
        )

        if not existing_like:
            return {
                "post_id": post_id,
                "liked": False,
                "likes_count": post.likes_count,
                "message": "Post was not liked by current user.",
            }

        db.delete(existing_like)
        post.likes_count = max(0, post.likes_count - 1)
        db.commit()
        db.refresh(post)

        return {
            "post_id": post_id,
            "liked": False,
            "likes_count": post.likes_count,
            "message": "Post unliked successfully.",
        }

    @staticmethod
    def add_comment(
        db: Session,
        post_id: str,
        current_user: User,
        content: str,
    ) -> dict:
        post = CommunityService._get_active_post(
            db=db,
            post_id=post_id,
        )

        if not post:
            raise ValueError("Post not found")

        comment = CommunityComment(
            post_id=post_id,
            user_id=current_user.id,
            content=content,
            status=CommunityCommentStatus.ACTIVE,
        )

        db.add(comment)
        post.comments_count += 1
        db.commit()
        db.refresh(comment)

        return {
            "id": comment.id,
            "post_id": comment.post_id,
            "user_id": comment.user_id,
            "user_full_name": current_user.full_name,
            "content": comment.content,
            "status": comment.status,
            "created_at": comment.created_at,
            "updated_at": comment.updated_at,
        }

    @staticmethod
    def get_comments(
        db: Session,
        post_id: str,
        limit: int = 50,
        offset: int = 0,
    ) -> list[dict]:
        limit = max(1, min(limit, 100))
        offset = max(0, offset)

        comments = (
            db.query(CommunityComment)
            .filter(CommunityComment.post_id == post_id)
            .filter(CommunityComment.status == CommunityCommentStatus.ACTIVE)
            .order_by(CommunityComment.created_at.asc())
            .offset(offset)
            .limit(limit)
            .all()
        )

        user_ids = list({comment.user_id for comment in comments})

        user_names = CommunityService._get_user_names(
            db=db,
            user_ids=user_ids,
        )

        return [
            {
                "id": comment.id,
                "post_id": comment.post_id,
                "user_id": comment.user_id,
                "user_full_name": user_names.get(comment.user_id),
                "content": comment.content,
                "status": comment.status,
                "created_at": comment.created_at,
                "updated_at": comment.updated_at,
            }
            for comment in comments
        ]

    @staticmethod
    def report_post(
        db: Session,
        post_id: str,
        current_user: User,
        reason,
        details: str | None = None,
    ) -> CommunityReport:
        post = CommunityService._get_active_post(
            db=db,
            post_id=post_id,
        )

        if not post:
            raise ValueError("Post not found")

        existing_report = (
            db.query(CommunityReport)
            .filter(CommunityReport.post_id == post_id)
            .filter(CommunityReport.user_id == current_user.id)
            .first()
        )

        if existing_report:
            return existing_report

        report = CommunityReport(
            post_id=post_id,
            user_id=current_user.id,
            reason=reason,
            details=details,
            status=CommunityReportStatus.PENDING,
        )

        db.add(report)
        post.reports_count += 1
        db.commit()
        db.refresh(report)

        return report

    @staticmethod
    def get_reports(
        db: Session,
        status_filter: CommunityReportStatus | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[CommunityReport]:
        limit = max(1, min(limit, 100))
        offset = max(0, offset)

        query = db.query(CommunityReport)

        if status_filter:
            query = query.filter(CommunityReport.status == status_filter)

        return (
            query.order_by(CommunityReport.created_at.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )

    @staticmethod
    def hide_post(
        db: Session,
        post_id: str,
    ) -> CommunityPost:
        post = CommunityService._get_post(
            db=db,
            post_id=post_id,
        )

        if not post or post.status == CommunityPostStatus.DELETED:
            raise ValueError("Post not found")

        post.status = CommunityPostStatus.HIDDEN
        db.commit()
        db.refresh(post)

        return post

    @staticmethod
    def restore_post(
        db: Session,
        post_id: str,
    ) -> CommunityPost:
        post = CommunityService._get_post(
            db=db,
            post_id=post_id,
        )

        if not post or post.status == CommunityPostStatus.DELETED:
            raise ValueError("Post not found")

        post.status = CommunityPostStatus.ACTIVE

        reports = (
            db.query(CommunityReport)
            .filter(CommunityReport.post_id == post_id)
            .filter(CommunityReport.status == CommunityReportStatus.PENDING)
            .all()
        )

        for report in reports:
            report.status = CommunityReportStatus.REVIEWED
            report.reviewed_at = datetime.utcnow()

        db.commit()
        db.refresh(post)

        return post
