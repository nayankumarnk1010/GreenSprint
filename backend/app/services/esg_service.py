import json
from datetime import datetime
from typing import Any

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.enums import CampaignChallengeStatus
from app.core.enums import CampaignStatus
from app.core.enums import ESGMetricCategory
from app.core.enums import ESGReportStatus
from app.core.enums import ESGReportType
from app.core.enums import UserRole
from app.models.ai_verification import AIVerification
from app.models.campaign import Campaign
from app.models.campaign_challenge import CampaignChallenge
from app.models.campaign_member import CampaignMember
from app.models.community_post import CommunityPost
from app.models.esg_report import ESGReport
from app.models.esg_report_metric import ESGReportMetric
from app.models.impact_metric import ImpactMetric
from app.models.organization_profile import OrganizationProfile
from app.models.points_ledger import PointsLedger
from app.models.submission import Submission
from app.models.user import User


class ESGService:
    @staticmethod
    def _serialize_summary(summary: dict[str, Any]) -> str:
        return json.dumps(summary)

    @staticmethod
    def _deserialize_summary(summary_json: str | None) -> dict[str, Any] | None:
        if not summary_json:
            return None

        try:
            return json.loads(summary_json)

        except json.JSONDecodeError:
            return None

    @staticmethod
    def _report_payload(
        report: ESGReport,
    ) -> dict:
        return {
            "id": report.id,
            "organization_id": report.organization_id,
            "campaign_id": report.campaign_id,
            "created_by": report.created_by,
            "title": report.title,
            "description": report.description,
            "report_type": report.report_type,
            "status": report.status,
            "period_start": report.period_start,
            "period_end": report.period_end,
            "summary": ESGService._deserialize_summary(report.summary_json),
            "published_at": report.published_at,
            "created_at": report.created_at,
            "updated_at": report.updated_at,
        }

    @staticmethod
    def _get_current_user_organization(
        db: Session,
        current_user: User,
    ) -> OrganizationProfile:
        organization = (
            db.query(OrganizationProfile)
            .filter(OrganizationProfile.user_id == current_user.id)
            .first()
        )

        if not organization:
            raise ValueError("Organization profile not found")

        return organization

    @staticmethod
    def _resolve_organization(
        db: Session,
        current_user: User,
        organization_id: str | None = None,
    ) -> OrganizationProfile:
        if current_user.role == UserRole.ADMIN:
            if organization_id:
                organization = (
                    db.query(OrganizationProfile)
                    .filter(OrganizationProfile.id == organization_id)
                    .first()
                )

                if not organization:
                    raise ValueError("Organization profile not found")

                return organization

            organization = (
                db.query(OrganizationProfile)
                .first()
            )

            if not organization:
                raise ValueError("Organization profile not found")

            return organization

        return ESGService._get_current_user_organization(
            db=db,
            current_user=current_user,
        )

    @staticmethod
    def _verify_campaign_access(
        db: Session,
        current_user: User,
        organization: OrganizationProfile,
        campaign_id: str,
    ) -> Campaign:
        campaign = (
            db.query(Campaign)
            .filter(Campaign.id == campaign_id)
            .first()
        )

        if not campaign:
            raise ValueError("Campaign not found")

        if (
            current_user.role != UserRole.ADMIN
            and campaign.organization_id != organization.id
        ):
            raise PermissionError("You do not have access to this campaign")

        return campaign

    @staticmethod
    def _apply_submission_period_filter(
        query,
        period_start: datetime | None,
        period_end: datetime | None,
    ):
        if period_start:
            query = query.filter(Submission.created_at >= period_start)

        if period_end:
            query = query.filter(Submission.created_at <= period_end)

        return query

    @staticmethod
    def _get_campaign_challenge_ids(
        db: Session,
        campaign_id: str,
    ) -> list[str]:
        rows = (
            db.query(CampaignChallenge.challenge_id)
            .filter(CampaignChallenge.campaign_id == campaign_id)
            .filter(CampaignChallenge.status == CampaignChallengeStatus.ACTIVE)
            .all()
        )

        return list(
            {
                row[0]
                for row in rows
            }
        )

    @staticmethod
    def _get_organization_challenge_ids(
        db: Session,
        organization_id: str,
    ) -> list[str]:
        campaign_ids = [
            row[0]
            for row in (
                db.query(Campaign.id)
                .filter(Campaign.organization_id == organization_id)
                .all()
            )
        ]

        if not campaign_ids:
            return []

        rows = (
            db.query(CampaignChallenge.challenge_id)
            .filter(CampaignChallenge.campaign_id.in_(campaign_ids))
            .filter(CampaignChallenge.status == CampaignChallengeStatus.ACTIVE)
            .all()
        )

        return list(
            {
                row[0]
                for row in rows
            }
        )

    @staticmethod
    def _safe_sum(value) -> float:
        if value is None:
            return 0.0

        return round(float(value), 2)

    @staticmethod
    def _build_summary(
        db: Session,
        organization: OrganizationProfile,
        report_type: ESGReportType,
        period_start: datetime | None = None,
        period_end: datetime | None = None,
        campaign: Campaign | None = None,
    ) -> dict[str, Any]:
        if report_type == ESGReportType.CAMPAIGN:
            if not campaign:
                raise ValueError("Campaign is required for campaign report")

            challenge_ids = ESGService._get_campaign_challenge_ids(
                db=db,
                campaign_id=campaign.id,
            )

            campaigns_count = 1
            active_campaigns_count = 1 if campaign.status == CampaignStatus.ACTIVE else 0

            members_count = (
                db.query(CampaignMember)
                .filter(CampaignMember.campaign_id == campaign.id)
                .count()
            )

            scope = "CAMPAIGN"

        else:
            challenge_ids = ESGService._get_organization_challenge_ids(
                db=db,
                organization_id=organization.id,
            )

            campaigns_count = (
                db.query(Campaign)
                .filter(Campaign.organization_id == organization.id)
                .count()
            )

            active_campaigns_count = (
                db.query(Campaign)
                .filter(Campaign.organization_id == organization.id)
                .filter(Campaign.status == CampaignStatus.ACTIVE)
                .count()
            )

            campaign_ids = [
                row[0]
                for row in (
                    db.query(Campaign.id)
                    .filter(Campaign.organization_id == organization.id)
                    .all()
                )
            ]

            if campaign_ids:
                members_count = (
                    db.query(CampaignMember)
                    .filter(CampaignMember.campaign_id.in_(campaign_ids))
                    .count()
                )

            else:
                members_count = 0

            scope = "ORGANIZATION"

        linked_challenges_count = len(challenge_ids)

        if not challenge_ids:
            return {
                "organization": {
                    "id": organization.id,
                    "name": organization.organization_name,
                    "type": organization.organization_type.value
                    if hasattr(organization.organization_type, "value")
                    else str(organization.organization_type),
                },
                "campaign": {
                    "id": campaign.id,
                    "title": campaign.title,
                } if campaign else None,
                "scope": scope,
                "period": {
                    "start": period_start.isoformat() if period_start else None,
                    "end": period_end.isoformat() if period_end else None,
                },
                "environmental": {
                    "total_co2e_saved_kg": 0,
                    "total_trees_planted": 0,
                    "total_biodiversity_score": 0,
                    "impact_actions_count": 0,
                },
                "social": {
                    "campaigns_count": campaigns_count,
                    "active_campaigns_count": active_campaigns_count,
                    "campaign_members_count": members_count,
                    "unique_participants_count": 0,
                },
                "governance": {
                    "linked_challenges_count": 0,
                    "submissions_count": 0,
                    "published_reports_count": 0,
                    "data_sources": [
                        "campaigns",
                        "challenge_links",
                        "submissions",
                        "impact_metrics",
                        "ai_verifications",
                        "community_posts",
                        "points_ledger",
                    ],
                },
                "engagement": {
                    "community_posts_count": 0,
                    "points_awarded": 0,
                },
                "verification": {
                    "ai_verifications_count": 0,
                    "verification_coverage_percent": 0,
                    "average_ai_confidence": 0,
                    "average_fraud_risk": 0,
                },
            }

        submission_query = (
            db.query(Submission)
            .filter(Submission.challenge_id.in_(challenge_ids))
        )

        submission_query = ESGService._apply_submission_period_filter(
            query=submission_query,
            period_start=period_start,
            period_end=period_end,
        )

        submissions = submission_query.all()
        submission_ids = [submission.id for submission in submissions]
        user_ids = list({submission.user_id for submission in submissions})

        submissions_count = len(submissions)
        unique_participants_count = len(user_ids)

        if submission_ids:
            impact_query = (
                db.query(
                    func.sum(ImpactMetric.co2e_saved_kg),
                    func.sum(ImpactMetric.trees_planted),
                    func.sum(ImpactMetric.biodiversity_score),
                    func.count(ImpactMetric.id),
                )
                .filter(ImpactMetric.submission_id.in_(submission_ids))
            )

            impact_row = impact_query.first()

            total_co2e_saved_kg = ESGService._safe_sum(impact_row[0])
            total_trees_planted = ESGService._safe_sum(impact_row[1])
            total_biodiversity_score = ESGService._safe_sum(impact_row[2])
            impact_actions_count = int(impact_row[3] or 0)

            ai_row = (
                db.query(
                    func.count(AIVerification.id),
                    func.avg(AIVerification.confidence_score),
                    func.avg(AIVerification.fraud_risk_score),
                )
                .filter(AIVerification.submission_id.in_(submission_ids))
                .first()
            )

            ai_verifications_count = int(ai_row[0] or 0)
            average_ai_confidence = round(float(ai_row[1] or 0), 2)
            average_fraud_risk = round(float(ai_row[2] or 0), 2)

            points_awarded = (
                db.query(func.sum(PointsLedger.points))
                .filter(PointsLedger.submission_id.in_(submission_ids))
                .scalar()
            )

            points_awarded = int(points_awarded or 0)

        else:
            total_co2e_saved_kg = 0
            total_trees_planted = 0
            total_biodiversity_score = 0
            impact_actions_count = 0
            ai_verifications_count = 0
            average_ai_confidence = 0
            average_fraud_risk = 0
            points_awarded = 0

        community_posts_count = (
            db.query(CommunityPost)
            .filter(CommunityPost.challenge_id.in_(challenge_ids))
            .count()
        )

        published_reports_count = (
            db.query(ESGReport)
            .filter(ESGReport.organization_id == organization.id)
            .filter(ESGReport.status == ESGReportStatus.PUBLISHED)
            .count()
        )

        verification_coverage_percent = 0

        if submissions_count > 0:
            verification_coverage_percent = round(
                (ai_verifications_count / submissions_count) * 100,
                2,
            )

        return {
            "organization": {
                "id": organization.id,
                "name": organization.organization_name,
                "type": organization.organization_type.value
                if hasattr(organization.organization_type, "value")
                else str(organization.organization_type),
            },
            "campaign": {
                "id": campaign.id,
                "title": campaign.title,
            } if campaign else None,
            "scope": scope,
            "period": {
                "start": period_start.isoformat() if period_start else None,
                "end": period_end.isoformat() if period_end else None,
            },
            "environmental": {
                "total_co2e_saved_kg": total_co2e_saved_kg,
                "total_trees_planted": total_trees_planted,
                "total_biodiversity_score": total_biodiversity_score,
                "impact_actions_count": impact_actions_count,
            },
            "social": {
                "campaigns_count": campaigns_count,
                "active_campaigns_count": active_campaigns_count,
                "campaign_members_count": members_count,
                "unique_participants_count": unique_participants_count,
            },
            "governance": {
                "linked_challenges_count": linked_challenges_count,
                "submissions_count": submissions_count,
                "published_reports_count": published_reports_count,
                "data_sources": [
                    "campaigns",
                    "challenge_links",
                    "submissions",
                    "impact_metrics",
                    "ai_verifications",
                    "community_posts",
                    "points_ledger",
                ],
            },
            "engagement": {
                "community_posts_count": community_posts_count,
                "points_awarded": points_awarded,
            },
            "verification": {
                "ai_verifications_count": ai_verifications_count,
                "verification_coverage_percent": verification_coverage_percent,
                "average_ai_confidence": average_ai_confidence,
                "average_fraud_risk": average_fraud_risk,
            },
        }

    @staticmethod
    def _metric_rows_from_summary(
        report_id: str,
        summary: dict[str, Any],
    ) -> list[ESGReportMetric]:
        rows: list[ESGReportMetric] = []

        metric_specs = [
            (
                ESGMetricCategory.ENVIRONMENTAL,
                "total_co2e_saved_kg",
                "Total CO2e Saved",
                summary["environmental"]["total_co2e_saved_kg"],
                "kg",
            ),
            (
                ESGMetricCategory.ENVIRONMENTAL,
                "total_trees_planted",
                "Total Trees Planted",
                summary["environmental"]["total_trees_planted"],
                "trees",
            ),
            (
                ESGMetricCategory.ENVIRONMENTAL,
                "total_biodiversity_score",
                "Total Biodiversity Score",
                summary["environmental"]["total_biodiversity_score"],
                "score",
            ),
            (
                ESGMetricCategory.ENVIRONMENTAL,
                "impact_actions_count",
                "Impact Actions Count",
                summary["environmental"]["impact_actions_count"],
                "actions",
            ),
            (
                ESGMetricCategory.SOCIAL,
                "campaigns_count",
                "Campaigns Count",
                summary["social"]["campaigns_count"],
                "campaigns",
            ),
            (
                ESGMetricCategory.SOCIAL,
                "campaign_members_count",
                "Campaign Members Count",
                summary["social"]["campaign_members_count"],
                "members",
            ),
            (
                ESGMetricCategory.SOCIAL,
                "unique_participants_count",
                "Unique Participants Count",
                summary["social"]["unique_participants_count"],
                "users",
            ),
            (
                ESGMetricCategory.GOVERNANCE,
                "linked_challenges_count",
                "Linked Challenges Count",
                summary["governance"]["linked_challenges_count"],
                "challenges",
            ),
            (
                ESGMetricCategory.GOVERNANCE,
                "submissions_count",
                "Submissions Count",
                summary["governance"]["submissions_count"],
                "submissions",
            ),
            (
                ESGMetricCategory.ENGAGEMENT,
                "community_posts_count",
                "Community Posts Count",
                summary["engagement"]["community_posts_count"],
                "posts",
            ),
            (
                ESGMetricCategory.ENGAGEMENT,
                "points_awarded",
                "Points Awarded",
                summary["engagement"]["points_awarded"],
                "points",
            ),
            (
                ESGMetricCategory.VERIFICATION,
                "ai_verifications_count",
                "AI Verifications Count",
                summary["verification"]["ai_verifications_count"],
                "verifications",
            ),
            (
                ESGMetricCategory.VERIFICATION,
                "verification_coverage_percent",
                "Verification Coverage",
                summary["verification"]["verification_coverage_percent"],
                "%",
            ),
            (
                ESGMetricCategory.VERIFICATION,
                "average_ai_confidence",
                "Average AI Confidence",
                summary["verification"]["average_ai_confidence"],
                "score",
            ),
            (
                ESGMetricCategory.VERIFICATION,
                "average_fraud_risk",
                "Average Fraud Risk",
                summary["verification"]["average_fraud_risk"],
                "score",
            ),
        ]

        for category, key, name, value, unit in metric_specs:
            rows.append(
                ESGReportMetric(
                    report_id=report_id,
                    category=category,
                    metric_key=key,
                    metric_name=name,
                    value_number=float(value),
                    value_text=None,
                    unit=unit,
                )
            )

        return rows

    @staticmethod
    def generate_report(
        db: Session,
        current_user: User,
        payload,
    ) -> dict:
        organization = ESGService._resolve_organization(
            db=db,
            current_user=current_user,
            organization_id=payload.organization_id,
        )

        campaign = None

        if payload.report_type == ESGReportType.CAMPAIGN:
            if not payload.campaign_id:
                raise ValueError("campaign_id is required for CAMPAIGN report")

            campaign = ESGService._verify_campaign_access(
                db=db,
                current_user=current_user,
                organization=organization,
                campaign_id=payload.campaign_id,
            )

        summary = ESGService._build_summary(
            db=db,
            organization=organization,
            report_type=payload.report_type,
            period_start=payload.period_start,
            period_end=payload.period_end,
            campaign=campaign,
        )

        report = ESGReport(
            organization_id=organization.id,
            campaign_id=campaign.id if campaign else None,
            created_by=current_user.id,
            title=payload.title,
            description=payload.description,
            report_type=payload.report_type,
            status=ESGReportStatus.GENERATED,
            period_start=payload.period_start,
            period_end=payload.period_end,
            summary_json=ESGService._serialize_summary(summary),
        )

        db.add(report)
        db.commit()
        db.refresh(report)

        metric_rows = ESGService._metric_rows_from_summary(
            report_id=report.id,
            summary=summary,
        )

        for metric in metric_rows:
            db.add(metric)

        db.commit()

        metrics = (
            db.query(ESGReportMetric)
            .filter(ESGReportMetric.report_id == report.id)
            .all()
        )

        data = ESGService._report_payload(report)
        data["metrics"] = metrics

        return data

    @staticmethod
    def list_reports(
        db: Session,
        current_user: User,
        organization_id: str | None = None,
        campaign_id: str | None = None,
        status_filter: ESGReportStatus | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> dict:
        limit = max(1, min(limit, 100))
        offset = max(0, offset)

        query = db.query(ESGReport)

        if current_user.role == UserRole.ADMIN:
            if organization_id:
                query = query.filter(ESGReport.organization_id == organization_id)

        else:
            organization = ESGService._get_current_user_organization(
                db=db,
                current_user=current_user,
            )
            query = query.filter(ESGReport.organization_id == organization.id)

        if campaign_id:
            query = query.filter(ESGReport.campaign_id == campaign_id)

        if status_filter:
            query = query.filter(ESGReport.status == status_filter)

        total = query.count()

        reports = (
            query.order_by(ESGReport.created_at.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )

        return {
            "items": [
                ESGService._report_payload(report)
                for report in reports
            ],
            "total": total,
            "limit": limit,
            "offset": offset,
        }

    @staticmethod
    def get_report_detail(
        db: Session,
        current_user: User,
        report_id: str,
    ) -> dict:
        report = (
            db.query(ESGReport)
            .filter(ESGReport.id == report_id)
            .first()
        )

        if not report:
            raise ValueError("ESG report not found")

        if current_user.role != UserRole.ADMIN:
            organization = ESGService._get_current_user_organization(
                db=db,
                current_user=current_user,
            )

            if report.organization_id != organization.id:
                raise PermissionError("You do not have access to this report")

        metrics = (
            db.query(ESGReportMetric)
            .filter(ESGReportMetric.report_id == report.id)
            .order_by(ESGReportMetric.category.asc())
            .all()
        )

        data = ESGService._report_payload(report)
        data["metrics"] = metrics

        return data

    @staticmethod
    def publish_report(
        db: Session,
        current_user: User,
        report_id: str,
    ) -> dict:
        report = (
            db.query(ESGReport)
            .filter(ESGReport.id == report_id)
            .first()
        )

        if not report:
            raise ValueError("ESG report not found")

        if current_user.role != UserRole.ADMIN:
            organization = ESGService._get_current_user_organization(
                db=db,
                current_user=current_user,
            )

            if report.organization_id != organization.id:
                raise PermissionError("You do not have access to this report")

        report.status = ESGReportStatus.PUBLISHED
        report.published_at = datetime.utcnow()

        db.commit()
        db.refresh(report)

        return ESGService.get_report_detail(
            db=db,
            current_user=current_user,
            report_id=report.id,
        )

    @staticmethod
    def archive_report(
        db: Session,
        current_user: User,
        report_id: str,
    ) -> dict:
        report = (
            db.query(ESGReport)
            .filter(ESGReport.id == report_id)
            .first()
        )

        if not report:
            raise ValueError("ESG report not found")

        if current_user.role != UserRole.ADMIN:
            organization = ESGService._get_current_user_organization(
                db=db,
                current_user=current_user,
            )

            if report.organization_id != organization.id:
                raise PermissionError("You do not have access to this report")

        report.status = ESGReportStatus.ARCHIVED

        db.commit()
        db.refresh(report)

        return ESGService.get_report_detail(
            db=db,
            current_user=current_user,
            report_id=report.id,
        )

    @staticmethod
    def organization_summary(
        db: Session,
        current_user: User,
    ) -> dict:
        organization = ESGService._get_current_user_organization(
            db=db,
            current_user=current_user,
        )

        summary = ESGService._build_summary(
            db=db,
            organization=organization,
            report_type=ESGReportType.ORGANIZATION,
        )

        return {
            "organization_id": organization.id,
            "campaign_id": None,
            "scope": "ORGANIZATION",
            "environmental": summary["environmental"],
            "social": summary["social"],
            "governance": summary["governance"],
            "engagement": summary["engagement"],
            "verification": summary["verification"],
        }

    @staticmethod
    def campaign_summary(
        db: Session,
        current_user: User,
        campaign_id: str,
    ) -> dict:
        organization = ESGService._resolve_organization(
            db=db,
            current_user=current_user,
        )

        campaign = ESGService._verify_campaign_access(
            db=db,
            current_user=current_user,
            organization=organization,
            campaign_id=campaign_id,
        )

        summary = ESGService._build_summary(
            db=db,
            organization=organization,
            report_type=ESGReportType.CAMPAIGN,
            campaign=campaign,
        )

        return {
            "organization_id": organization.id,
            "campaign_id": campaign.id,
            "scope": "CAMPAIGN",
            "environmental": summary["environmental"],
            "social": summary["social"],
            "governance": summary["governance"],
            "engagement": summary["engagement"],
            "verification": summary["verification"],
        }

    @staticmethod
    def admin_platform_summary(
        db: Session,
    ) -> dict:
        organizations_count = db.query(OrganizationProfile).count()
        campaigns_count = db.query(Campaign).count()
        submissions_count = db.query(Submission).count()
        impact_actions_count = db.query(ImpactMetric).count()

        impact_row = (
            db.query(
                func.sum(ImpactMetric.co2e_saved_kg),
                func.sum(ImpactMetric.trees_planted),
                func.sum(ImpactMetric.biodiversity_score),
            )
            .first()
        )

        reports_count = db.query(ESGReport).count()
        published_reports_count = (
            db.query(ESGReport)
            .filter(ESGReport.status == ESGReportStatus.PUBLISHED)
            .count()
        )

        ai_verifications_count = db.query(AIVerification).count()
        community_posts_count = db.query(CommunityPost).count()

        return {
            "organization_id": None,
            "campaign_id": None,
            "scope": "PLATFORM",
            "environmental": {
                "total_co2e_saved_kg": ESGService._safe_sum(impact_row[0]),
                "total_trees_planted": ESGService._safe_sum(impact_row[1]),
                "total_biodiversity_score": ESGService._safe_sum(impact_row[2]),
                "impact_actions_count": impact_actions_count,
            },
            "social": {
                "organizations_count": organizations_count,
                "campaigns_count": campaigns_count,
                "unique_participants_count": 0,
            },
            "governance": {
                "submissions_count": submissions_count,
                "reports_count": reports_count,
                "published_reports_count": published_reports_count,
            },
            "engagement": {
                "community_posts_count": community_posts_count,
            },
            "verification": {
                "ai_verifications_count": ai_verifications_count,
            },
        }