import json
from datetime import datetime
from enum import Enum
from typing import Any

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.enums import AIVerificationDecision
from app.core.enums import AIVerificationStatus
from app.core.enums import CommunityPostStatus
from app.core.enums import CommunityReportStatus
from app.core.enums import ESGReportStatus
from app.core.enums import OrganizationProfileStatus
from app.core.enums import SubmissionStatus
from app.models.ai_verification import AIVerification
from app.models.admin_audit_log import AdminAuditLog
from app.models.campaign import Campaign
from app.models.community_post import CommunityPost
from app.models.community_report import CommunityReport
from app.models.esg_report import ESGReport
from app.models.organization_profile import OrganizationProfile
from app.models.platform_setting import PlatformSetting
from app.models.submission import Submission
from app.models.user import User


class AdminService:
    DEFAULT_SETTINGS = [
        {
            "setting_key": "submissions_enabled",
            "setting_value": "true",
            "value_type": "boolean",
            "description": "Allows users to create eco-action submissions.",
        },
        {
            "setting_key": "ai_verification_enabled",
            "setting_value": "true",
            "value_type": "boolean",
            "description": "Allows AI verification checks to run.",
        },
        {
            "setting_key": "community_posting_enabled",
            "setting_value": "true",
            "value_type": "boolean",
            "description": "Allows users to create community posts.",
        },
        {
            "setting_key": "campaign_creation_enabled",
            "setting_value": "true",
            "value_type": "boolean",
            "description": "Allows organizations to create campaigns.",
        },
        {
            "setting_key": "maintenance_mode",
            "setting_value": "false",
            "value_type": "boolean",
            "description": "Indicates whether the platform is in maintenance mode.",
        },
        {
            "setting_key": "max_daily_submissions_per_user",
            "setting_value": "10",
            "value_type": "integer",
            "description": "Maximum number of submissions a user can create in one day.",
        },
    ]

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
    def _audit_payload(
        audit: AdminAuditLog,
    ) -> dict:
        return {
            "id": audit.id,
            "actor_user_id": audit.actor_user_id,
            "action": audit.action,
            "target_type": audit.target_type,
            "target_id": audit.target_id,
            "description": audit.description,
            "metadata": AdminService._deserialize_metadata(audit.metadata_json),
            "created_at": audit.created_at,
        }

    @staticmethod
    def _enum_member(
        enum_class,
        value: str,
    ):
        normalized_value = value.upper().strip()

        for member in enum_class:
            if member.name == normalized_value:
                return member

            if str(member.value).upper() == normalized_value:
                return member

        raise ValueError(
            f"Invalid value '{value}'. Allowed values: "
            f"{', '.join([member.value for member in enum_class])}"
        )

    @staticmethod
    def _enum_member_or_none(
        enum_class,
        value: str | None,
    ):
        if not value:
            return None

        return AdminService._enum_member(
            enum_class=enum_class,
            value=value,
        )

    @staticmethod
    def create_audit_log(
        db: Session,
        actor_user_id: str,
        action: str,
        target_type: str,
        target_id: str | None,
        description: str,
        metadata: dict[str, Any] | None = None,
    ) -> AdminAuditLog:
        audit = AdminAuditLog(
            actor_user_id=actor_user_id,
            action=action,
            target_type=target_type,
            target_id=target_id,
            description=description,
            metadata_json=AdminService._serialize_metadata(metadata),
        )

        db.add(audit)
        db.commit()
        db.refresh(audit)

        return audit

    @staticmethod
    def seed_default_settings(
        db: Session,
    ) -> None:
        for setting_data in AdminService.DEFAULT_SETTINGS:
            existing = (
                db.query(PlatformSetting)
                .filter(
                    PlatformSetting.setting_key
                    == setting_data["setting_key"]
                )
                .first()
            )

            if existing:
                continue

            db.add(
                PlatformSetting(
                    setting_key=setting_data["setting_key"],
                    setting_value=setting_data["setting_value"],
                    value_type=setting_data["value_type"],
                    description=setting_data["description"],
                )
            )

        db.commit()

    @staticmethod
    def get_dashboard(
        db: Session,
    ) -> dict:
        AdminService.seed_default_settings(db=db)

        total_users = db.query(User).count()
        active_users = (
            db.query(User)
            .filter(User.is_active == True)
            .count()
        )
        verified_users = (
            db.query(User)
            .filter(User.is_verified == True)
            .count()
        )

        total_orgs = db.query(OrganizationProfile).count()
        active_orgs = (
            db.query(OrganizationProfile)
            .filter(OrganizationProfile.status == OrganizationProfileStatus.ACTIVE)
            .count()
        )
        suspended_orgs = (
            db.query(OrganizationProfile)
            .filter(OrganizationProfile.status == OrganizationProfileStatus.SUSPENDED)
            .count()
        )

        total_campaigns = db.query(Campaign).count()

        total_submissions = db.query(Submission).count()
        manual_review_submissions = (
            db.query(Submission)
            .filter(Submission.status == SubmissionStatus.MANUAL_REVIEW)
            .count()
        )
        pending_submissions = (
            db.query(Submission)
            .filter(Submission.status == SubmissionStatus.PENDING)
            .count()
        )

        total_ai_verifications = db.query(AIVerification).count()
        manual_review_ai = (
            db.query(AIVerification)
            .filter(AIVerification.decision == AIVerificationDecision.MANUAL_REVIEW)
            .count()
        )

        average_confidence = (
            db.query(func.avg(AIVerification.confidence_score))
            .scalar()
        )
        average_fraud_risk = (
            db.query(func.avg(AIVerification.fraud_risk_score))
            .scalar()
        )

        total_community_posts = db.query(CommunityPost).count()
        hidden_community_posts = (
            db.query(CommunityPost)
            .filter(CommunityPost.status == CommunityPostStatus.HIDDEN)
            .count()
        )

        pending_reports = (
            db.query(CommunityReport)
            .filter(CommunityReport.status == CommunityReportStatus.PENDING)
            .count()
        )

        total_esg_reports = db.query(ESGReport).count()
        published_esg_reports = (
            db.query(ESGReport)
            .filter(ESGReport.status == ESGReportStatus.PUBLISHED)
            .count()
        )

        platform_settings_count = db.query(PlatformSetting).count()

        return {
            "users": {
                "total_users": total_users,
                "active_users": active_users,
                "inactive_users": total_users - active_users,
                "verified_users": verified_users,
            },
            "organizations": {
                "total_organizations": total_orgs,
                "active_organizations": active_orgs,
                "suspended_organizations": suspended_orgs,
            },
            "campaigns": {
                "total_campaigns": total_campaigns,
            },
            "submissions": {
                "total_submissions": total_submissions,
                "pending_submissions": pending_submissions,
                "manual_review_submissions": manual_review_submissions,
            },
            "ai_verification": {
                "total_ai_verifications": total_ai_verifications,
                "manual_review_ai": manual_review_ai,
                "average_confidence": round(float(average_confidence or 0), 2),
                "average_fraud_risk": round(float(average_fraud_risk or 0), 2),
            },
            "community": {
                "total_posts": total_community_posts,
                "hidden_posts": hidden_community_posts,
                "pending_reports": pending_reports,
            },
            "esg_reports": {
                "total_reports": total_esg_reports,
                "published_reports": published_esg_reports,
            },
            "platform_settings": {
                "settings_count": platform_settings_count,
            },
        }

    @staticmethod
    def list_users(
        db: Session,
        role: str | None = None,
        is_active: bool | None = None,
        search: str | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> dict:
        limit = max(1, min(limit, 100))
        offset = max(0, offset)

        query = db.query(User)

        if role:
            from app.core.enums import UserRole

            query = query.filter(
                User.role == AdminService._enum_member(
                    enum_class=UserRole,
                    value=role,
                )
            )

        if is_active is not None:
            query = query.filter(User.is_active == is_active)

        if search:
            like_text = f"%{search}%"
            query = query.filter(
                (User.email.ilike(like_text))
                | (User.full_name.ilike(like_text))
            )

        total = query.count()

        users = (
            query.order_by(User.created_at.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )

        return {
            "items": users,
            "total": total,
            "limit": limit,
            "offset": offset,
        }

    @staticmethod
    def update_user(
        db: Session,
        current_user: User,
        user_id: str,
        payload,
    ) -> User:
        user = (
            db.query(User)
            .filter(User.id == user_id)
            .first()
        )

        if not user:
            raise ValueError("User not found")

        update_data = payload.model_dump(exclude_unset=True)

        for key, value in update_data.items():
            setattr(user, key, value)

        db.commit()
        db.refresh(user)

        AdminService.create_audit_log(
            db=db,
            actor_user_id=current_user.id,
            action="USER_UPDATED",
            target_type="USER",
            target_id=user.id,
            description=f"Admin updated user {user.email}.",
            metadata=update_data,
        )

        return user

    @staticmethod
    def list_organizations(
        db: Session,
        status: str | None = None,
        search: str | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> dict:
        limit = max(1, min(limit, 100))
        offset = max(0, offset)

        query = db.query(OrganizationProfile)

        if status:
            query = query.filter(
                OrganizationProfile.status
                == AdminService._enum_member(
                    enum_class=OrganizationProfileStatus,
                    value=status,
                )
            )

        if search:
            like_text = f"%{search}%"
            query = query.filter(
                OrganizationProfile.organization_name.ilike(like_text)
            )

        total = query.count()

        orgs = (
            query.order_by(OrganizationProfile.created_at.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )

        return {
            "items": [
                {
                    "id": org.id,
                    "user_id": org.user_id,
                    "organization_name": org.organization_name,
                    "organization_type": org.organization_type,
                    "description": org.description,
                    "city": org.city,
                    "state": org.state,
                    "country": org.country,
                    "status": org.status,
                    "created_at": org.created_at,
                    "updated_at": org.updated_at,
                }
                for org in orgs
            ],
            "total": total,
            "limit": limit,
            "offset": offset,
        }

    @staticmethod
    def update_organization_status(
        db: Session,
        current_user: User,
        organization_id: str,
        payload,
    ) -> dict:
        organization = (
            db.query(OrganizationProfile)
            .filter(OrganizationProfile.id == organization_id)
            .first()
        )

        if not organization:
            raise ValueError("Organization not found")

        old_status = organization.status

        organization.status = AdminService._enum_member(
            enum_class=OrganizationProfileStatus,
            value=payload.status,
        )

        db.commit()
        db.refresh(organization)

        AdminService.create_audit_log(
            db=db,
            actor_user_id=current_user.id,
            action="ORGANIZATION_STATUS_UPDATED",
            target_type="ORGANIZATION",
            target_id=organization.id,
            description=(
                f"Organization status changed from {old_status} "
                f"to {organization.status}."
            ),
            metadata={
                "old_status": old_status.value
                if hasattr(old_status, "value")
                else str(old_status),
                "new_status": organization.status.value
                if hasattr(organization.status, "value")
                else str(organization.status),
                "notes": payload.notes,
            },
        )

        return {
            "id": organization.id,
            "organization_name": organization.organization_name,
            "status": organization.status,
            "updated_at": organization.updated_at,
        }

    @staticmethod
    def list_submission_moderation_queue(
        db: Session,
        status: str | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> dict:
        limit = max(1, min(limit, 100))
        offset = max(0, offset)

        query = db.query(Submission)

        if status:
            query = query.filter(
                Submission.status
                == AdminService._enum_member(
                    enum_class=SubmissionStatus,
                    value=status,
                )
            )

        else:
            query = query.filter(
                Submission.status.in_(
                    [
                        SubmissionStatus.PENDING,
                        SubmissionStatus.MANUAL_REVIEW,
                    ]
                )
            )

        total = query.count()

        submissions = (
            query.order_by(Submission.created_at.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )

        return {
            "items": [
                {
                    "id": submission.id,
                    "user_id": submission.user_id,
                    "challenge_id": submission.challenge_id,
                    "title": submission.title,
                    "description": submission.description,
                    "submission_type": submission.submission_type,
                    "status": submission.status,
                    "latitude": submission.latitude,
                    "longitude": submission.longitude,
                    "created_at": submission.created_at,
                    "updated_at": submission.updated_at,
                }
                for submission in submissions
            ],
            "total": total,
            "limit": limit,
            "offset": offset,
        }

    @staticmethod
    def decide_submission(
        db: Session,
        current_user: User,
        submission_id: str,
        payload,
    ) -> dict:
        submission = (
            db.query(Submission)
            .filter(Submission.id == submission_id)
            .first()
        )

        if not submission:
            raise ValueError("Submission not found")

        decision = payload.decision.upper().strip()

        if decision == "APPROVE":
            new_status = SubmissionStatus.APPROVED

        elif decision == "REJECT":
            new_status = SubmissionStatus.REJECTED

        else:
            raise ValueError("Decision must be APPROVE or REJECT")

        old_status = submission.status
        submission.status = new_status

        db.commit()
        db.refresh(submission)

        AdminService.create_audit_log(
            db=db,
            actor_user_id=current_user.id,
            action="SUBMISSION_MODERATED",
            target_type="SUBMISSION",
            target_id=submission.id,
            description=f"Submission moderation decision: {decision}.",
            metadata={
                "old_status": old_status.value
                if hasattr(old_status, "value")
                else str(old_status),
                "new_status": new_status.value
                if hasattr(new_status, "value")
                else str(new_status),
                "notes": payload.notes,
            },
        )

        return {
            "id": submission.id,
            "status": submission.status,
            "decision": decision,
            "notes": payload.notes,
        }

    @staticmethod
    def list_community_reports(
        db: Session,
        status: str | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> dict:
        limit = max(1, min(limit, 100))
        offset = max(0, offset)

        query = db.query(CommunityReport)

        if status:
            query = query.filter(
                CommunityReport.status
                == AdminService._enum_member(
                    enum_class=CommunityReportStatus,
                    value=status,
                )
            )

        total = query.count()

        reports = (
            query.order_by(CommunityReport.created_at.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )

        items = []

        for report in reports:
            post_id = getattr(report, "post_id", None)

            post = None

            if post_id:
                post = (
                    db.query(CommunityPost)
                    .filter(CommunityPost.id == post_id)
                    .first()
                )

            items.append(
                {
                    "id": report.id,
                    "post_id": post_id,
                    "reporter_user_id": getattr(report, "reporter_user_id", None),
                    "reason": getattr(report, "reason", None),
                    "description": getattr(report, "description", None),
                    "status": getattr(report, "status", None),
                    "created_at": getattr(report, "created_at", None),
                    "post_status": post.status if post else None,
                    "post_content": post.content if post else None,
                }
            )

        return {
            "items": items,
            "total": total,
            "limit": limit,
            "offset": offset,
        }

    @staticmethod
    def decide_community_report(
        db: Session,
        current_user: User,
        report_id: str,
        payload,
    ) -> dict:
        report = (
            db.query(CommunityReport)
            .filter(CommunityReport.id == report_id)
            .first()
        )

        if not report:
            raise ValueError("Community report not found")

        post_id = getattr(report, "post_id", None)

        post = None

        if post_id:
            post = (
                db.query(CommunityPost)
                .filter(CommunityPost.id == post_id)
                .first()
            )

        decision = payload.decision.upper().strip()

        if decision == "HIDE":
            if not post:
                raise ValueError("Community post not found")

            post.status = CommunityPostStatus.HIDDEN

            if hasattr(report, "status"):
                report.status = AdminService._enum_member_or_none(
                    enum_class=CommunityReportStatus,
                    value="RESOLVED",
                ) or report.status

        elif decision == "RESTORE":
            if not post:
                raise ValueError("Community post not found")

            post.status = CommunityPostStatus.ACTIVE

        elif decision in {"DISMISS", "RESOLVE"}:
            if hasattr(report, "status"):
                try:
                    report.status = AdminService._enum_member(
                        enum_class=CommunityReportStatus,
                        value="RESOLVED",
                    )

                except ValueError:
                    report.status = AdminService._enum_member(
                        enum_class=CommunityReportStatus,
                        value="REVIEWED",
                    )

        else:
            raise ValueError("Decision must be HIDE, RESTORE, DISMISS, or RESOLVE")

        if hasattr(report, "reviewed_by"):
            report.reviewed_by = current_user.id

        if hasattr(report, "reviewed_at"):
            report.reviewed_at = datetime.utcnow()

        db.commit()
        db.refresh(report)

        if post:
            db.refresh(post)

        AdminService.create_audit_log(
            db=db,
            actor_user_id=current_user.id,
            action="COMMUNITY_REPORT_MODERATED",
            target_type="COMMUNITY_REPORT",
            target_id=report.id,
            description=f"Community report moderation decision: {decision}.",
            metadata={
                "decision": decision,
                "post_id": post_id,
                "notes": payload.notes,
            },
        )

        return {
            "report_id": report.id,
            "report_status": getattr(report, "status", None),
            "post_id": post_id,
            "post_status": post.status if post else None,
            "decision": decision,
            "notes": payload.notes,
        }

    @staticmethod
    def list_settings(
        db: Session,
    ) -> list[PlatformSetting]:
        AdminService.seed_default_settings(db=db)

        return (
            db.query(PlatformSetting)
            .order_by(PlatformSetting.setting_key.asc())
            .all()
        )

    @staticmethod
    def update_setting(
        db: Session,
        current_user: User,
        setting_key: str,
        payload,
    ) -> PlatformSetting:
        AdminService.seed_default_settings(db=db)

        setting = (
            db.query(PlatformSetting)
            .filter(PlatformSetting.setting_key == setting_key)
            .first()
        )

        if not setting:
            setting = PlatformSetting(
                setting_key=setting_key,
                setting_value=payload.setting_value,
                value_type=payload.value_type,
                description=payload.description,
                updated_by=current_user.id,
            )
            db.add(setting)

        else:
            setting.setting_value = payload.setting_value
            setting.value_type = payload.value_type
            setting.description = payload.description
            setting.updated_by = current_user.id

        db.commit()
        db.refresh(setting)

        AdminService.create_audit_log(
            db=db,
            actor_user_id=current_user.id,
            action="PLATFORM_SETTING_UPDATED",
            target_type="PLATFORM_SETTING",
            target_id=setting.id,
            description=f"Platform setting updated: {setting.setting_key}.",
            metadata={
                "setting_key": setting.setting_key,
                "setting_value": setting.setting_value,
                "value_type": setting.value_type,
            },
        )

        return setting

    @staticmethod
    def list_audit_logs(
        db: Session,
        action: str | None = None,
        target_type: str | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> dict:
        limit = max(1, min(limit, 100))
        offset = max(0, offset)

        query = db.query(AdminAuditLog)

        if action:
            query = query.filter(AdminAuditLog.action == action)

        if target_type:
            query = query.filter(AdminAuditLog.target_type == target_type)

        total = query.count()

        logs = (
            query.order_by(AdminAuditLog.created_at.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )

        return {
            "items": [
                AdminService._audit_payload(log)
                for log in logs
            ],
            "total": total,
            "limit": limit,
            "offset": offset,
        }