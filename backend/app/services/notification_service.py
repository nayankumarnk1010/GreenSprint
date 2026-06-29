import json
from datetime import datetime
from typing import Any

from sqlalchemy.orm import Session

from app.core.enums import CampaignMemberStatus
from app.core.enums import NotificationPriority
from app.core.enums import NotificationReferenceType
from app.core.enums import NotificationStatus
from app.core.enums import NotificationType
from app.models.campaign import Campaign
from app.models.campaign_member import CampaignMember
from app.models.notification import Notification
from app.models.notification_preference import NotificationPreference
from app.models.submission import Submission
from app.models.user import User


class NotificationService:
    @staticmethod
    def _serialize_metadata(
        metadata: dict[str, Any] | None,
    ) -> str | None:
        if metadata is None:
            return None

        return json.dumps(metadata)

    @staticmethod
    def _deserialize_metadata(
        metadata_json: str | None,
    ) -> dict[str, Any] | None:
        if not metadata_json:
            return None

        try:
            return json.loads(metadata_json)

        except json.JSONDecodeError:
            return None

    @staticmethod
    def _notification_payload(
        notification: Notification,
    ) -> dict:
        return {
            "id": notification.id,
            "user_id": notification.user_id,
            "actor_user_id": notification.actor_user_id,
            "title": notification.title,
            "message": notification.message,
            "notification_type": notification.notification_type,
            "status": notification.status,
            "priority": notification.priority,
            "reference_type": notification.reference_type,
            "reference_id": notification.reference_id,
            "action_url": notification.action_url,
            "metadata": NotificationService._deserialize_metadata(
                notification.metadata_json
            ),
            "created_at": notification.created_at,
            "read_at": notification.read_at,
        }

    @staticmethod
    def get_or_create_preferences(
        db: Session,
        user_id: str,
    ) -> NotificationPreference:
        preference = (
            db.query(NotificationPreference)
            .filter(NotificationPreference.user_id == user_id)
            .first()
        )

        if preference:
            return preference

        preference = NotificationPreference(
            user_id=user_id,
            in_app_enabled=True,
            system_notifications=True,
            submission_updates=True,
            ai_verification_updates=True,
            impact_updates=True,
            reward_updates=True,
            campaign_updates=True,
            community_updates=True,
        )

        db.add(preference)
        db.commit()
        db.refresh(preference)

        return preference

    @staticmethod
    def update_preferences(
        db: Session,
        current_user: User,
        payload,
    ) -> NotificationPreference:
        preference = NotificationService.get_or_create_preferences(
            db=db,
            user_id=current_user.id,
        )

        update_data = payload.model_dump(exclude_unset=True)

        for key, value in update_data.items():
            setattr(preference, key, value)

        db.commit()
        db.refresh(preference)

        return preference

    @staticmethod
    def _is_allowed_by_preferences(
        db: Session,
        user_id: str,
        notification_type: NotificationType,
    ) -> bool:
        preference = NotificationService.get_or_create_preferences(
            db=db,
            user_id=user_id,
        )

        if not preference.in_app_enabled:
            return False

        if notification_type == NotificationType.SYSTEM:
            return preference.system_notifications

        if notification_type == NotificationType.SUBMISSION_STATUS:
            return preference.submission_updates

        if notification_type == NotificationType.AI_VERIFICATION:
            return preference.ai_verification_updates

        if notification_type == NotificationType.IMPACT_CALCULATED:
            return preference.impact_updates

        if notification_type in {
            NotificationType.POINTS_AWARDED,
            NotificationType.BADGE_EARNED,
        }:
            return preference.reward_updates

        if notification_type == NotificationType.CAMPAIGN_UPDATE:
            return preference.campaign_updates

        if notification_type == NotificationType.COMMUNITY_INTERACTION:
            return preference.community_updates

        return True

    @staticmethod
    def create_notification(
        db: Session,
        user_id: str,
        title: str,
        message: str,
        notification_type: NotificationType = NotificationType.GENERAL,
        priority: NotificationPriority = NotificationPriority.NORMAL,
        actor_user_id: str | None = None,
        reference_type: NotificationReferenceType | None = None,
        reference_id: str | None = None,
        action_url: str | None = None,
        metadata: dict[str, Any] | None = None,
        respect_preferences: bool = True,
    ) -> Notification | None:
        user = (
            db.query(User)
            .filter(User.id == user_id)
            .first()
        )

        if not user:
            raise ValueError("User not found")

        if respect_preferences:
            allowed = NotificationService._is_allowed_by_preferences(
                db=db,
                user_id=user_id,
                notification_type=notification_type,
            )

            if not allowed:
                return None

        notification = Notification(
            user_id=user_id,
            actor_user_id=actor_user_id,
            title=title,
            message=message,
            notification_type=notification_type,
            status=NotificationStatus.UNREAD,
            priority=priority,
            reference_type=reference_type,
            reference_id=reference_id,
            action_url=action_url,
            metadata_json=NotificationService._serialize_metadata(metadata),
        )

        db.add(notification)
        db.commit()
        db.refresh(notification)

        return notification

    @staticmethod
    def list_my_notifications(
        db: Session,
        current_user: User,
        status_filter: NotificationStatus | None = None,
        type_filter: NotificationType | None = None,
        include_archived: bool = False,
        limit: int = 20,
        offset: int = 0,
    ) -> dict:
        limit = max(1, min(limit, 100))
        offset = max(0, offset)

        query = (
            db.query(Notification)
            .filter(Notification.user_id == current_user.id)
        )

        if status_filter:
            query = query.filter(Notification.status == status_filter)

        elif not include_archived:
            query = query.filter(Notification.status != NotificationStatus.ARCHIVED)

        if type_filter:
            query = query.filter(Notification.notification_type == type_filter)

        total = query.count()

        notifications = (
            query.order_by(Notification.created_at.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )

        unread_count = NotificationService.get_unread_count(
            db=db,
            current_user=current_user,
        )

        return {
            "items": [
                NotificationService._notification_payload(notification)
                for notification in notifications
            ],
            "total": total,
            "unread_count": unread_count,
            "limit": limit,
            "offset": offset,
        }

    @staticmethod
    def get_unread_count(
        db: Session,
        current_user: User,
    ) -> int:
        return (
            db.query(Notification)
            .filter(Notification.user_id == current_user.id)
            .filter(Notification.status == NotificationStatus.UNREAD)
            .count()
        )

    @staticmethod
    def mark_as_read(
        db: Session,
        current_user: User,
        notification_id: str,
    ) -> dict:
        notification = (
            db.query(Notification)
            .filter(Notification.id == notification_id)
            .filter(Notification.user_id == current_user.id)
            .first()
        )

        if not notification:
            raise ValueError("Notification not found")

        notification.status = NotificationStatus.READ
        notification.read_at = datetime.utcnow()

        db.commit()
        db.refresh(notification)

        return NotificationService._notification_payload(notification)

    @staticmethod
    def mark_all_as_read(
        db: Session,
        current_user: User,
    ) -> dict:
        notifications = (
            db.query(Notification)
            .filter(Notification.user_id == current_user.id)
            .filter(Notification.status == NotificationStatus.UNREAD)
            .all()
        )

        now = datetime.utcnow()

        for notification in notifications:
            notification.status = NotificationStatus.READ
            notification.read_at = now

        db.commit()

        return {
            "updated_count": len(notifications),
            "message": "All unread notifications marked as read.",
        }

    @staticmethod
    def archive_notification(
        db: Session,
        current_user: User,
        notification_id: str,
    ) -> dict:
        notification = (
            db.query(Notification)
            .filter(Notification.id == notification_id)
            .filter(Notification.user_id == current_user.id)
            .first()
        )

        if not notification:
            raise ValueError("Notification not found")

        notification.status = NotificationStatus.ARCHIVED

        db.commit()
        db.refresh(notification)

        return NotificationService._notification_payload(notification)

    @staticmethod
    def admin_send_to_user(
        db: Session,
        current_user: User,
        payload,
    ) -> dict:
        notification = NotificationService.create_notification(
            db=db,
            user_id=payload.user_id,
            actor_user_id=current_user.id,
            title=payload.title,
            message=payload.message,
            notification_type=payload.notification_type,
            priority=payload.priority,
            reference_type=payload.reference_type,
            reference_id=payload.reference_id,
            action_url=payload.action_url,
            metadata=payload.metadata,
            respect_preferences=False,
        )

        if not notification:
            raise ValueError("Notification could not be created")

        return NotificationService._notification_payload(notification)

    @staticmethod
    def broadcast_to_campaign(
        db: Session,
        current_user: User,
        campaign_id: str,
        payload,
    ) -> dict:
        campaign = (
            db.query(Campaign)
            .filter(Campaign.id == campaign_id)
            .first()
        )

        if not campaign:
            raise ValueError("Campaign not found")

        members = (
            db.query(CampaignMember)
            .filter(CampaignMember.campaign_id == campaign_id)
            .filter(CampaignMember.status == CampaignMemberStatus.ACTIVE)
            .all()
        )

        created_count = 0

        unique_user_ids = list(
            {
                member.user_id
                for member in members
            }
        )

        for user_id in unique_user_ids:
            notification = NotificationService.create_notification(
                db=db,
                user_id=user_id,
                actor_user_id=current_user.id,
                title=payload.title,
                message=payload.message,
                notification_type=NotificationType.CAMPAIGN_UPDATE,
                priority=payload.priority,
                reference_type=NotificationReferenceType.CAMPAIGN,
                reference_id=campaign_id,
                action_url=payload.action_url,
                metadata=payload.metadata,
                respect_preferences=True,
            )

            if notification:
                created_count += 1

        return {
            "campaign_id": campaign_id,
            "total_members": len(unique_user_ids),
            "notifications_created": created_count,
            "message": "Campaign notification broadcast completed.",
        }

    @staticmethod
    def notify_submission_status(
        db: Session,
        current_user: User,
        submission_id: str,
    ) -> dict:
        submission = (
            db.query(Submission)
            .filter(Submission.id == submission_id)
            .first()
        )

        if not submission:
            raise ValueError("Submission not found")

        title = "Submission status updated"

        message = (
            f"Your submission '{submission.title}' is currently "
            f"{submission.status.value if hasattr(submission.status, 'value') else submission.status}."
        )

        notification = NotificationService.create_notification(
            db=db,
            user_id=submission.user_id,
            actor_user_id=current_user.id,
            title=title,
            message=message,
            notification_type=NotificationType.SUBMISSION_STATUS,
            priority=NotificationPriority.NORMAL,
            reference_type=NotificationReferenceType.SUBMISSION,
            reference_id=submission.id,
            action_url=f"/submissions/{submission.id}",
            metadata={
                "submission_id": submission.id,
                "submission_status": submission.status.value
                if hasattr(submission.status, "value")
                else str(submission.status),
            },
            respect_preferences=True,
        )

        if not notification:
            return {
                "skipped": True,
                "message": "Notification skipped due to user preferences.",
            }

        return NotificationService._notification_payload(notification)