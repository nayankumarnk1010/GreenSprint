from collections import Counter
from datetime import datetime
from datetime import timedelta

from sqlalchemy.orm import Session

from app.core.enums import AIVerificationDecision
from app.core.enums import PlantDiagnosisStatus
from app.models.ai_verification import AIVerification
from app.models.challenge import Challenge
from app.models.challenge_impact_summary import ChallengeImpactSummary
from app.models.challenge_participant import ChallengeParticipant
from app.models.impact_metric import ImpactMetric
from app.models.plant_diagnosis import PlantDiagnosis
from app.models.points_ledger import PointsLedger
from app.models.submission import Submission
from app.models.user import User
from app.models.user_gamification_profile import UserGamificationProfile
from app.models.user_impact_summary import UserImpactSummary


class AnalyticsService:
    """
    Free/local analytics aggregation service.

    This service does not use paid APIs.
    It prepares dashboard-ready data for the future frontend.
    """

    @staticmethod
    def _enum_value(value) -> str:
        if value is None:
            return "UNKNOWN"

        if hasattr(value, "value"):
            return str(value.value)

        return str(value)

    @staticmethod
    def _round(value: float) -> float:
        return round(float(value or 0.0), 3)

    @staticmethod
    def _count_by_field(items: list, field_name: str) -> list[dict]:
        counter: Counter = Counter()

        for item in items:
            value = getattr(item, field_name, None)
            counter[AnalyticsService._enum_value(value)] += 1

        return [
            {
                "label": label,
                "count": count,
            }
            for label, count in sorted(counter.items())
        ]

    @staticmethod
    def _average(values: list[float | None]) -> float:
        clean_values = [
            float(value)
            for value in values
            if value is not None
        ]

        if not clean_values:
            return 0.0

        return AnalyticsService._round(
            sum(clean_values) / len(clean_values)
        )

    @staticmethod
    def _last_n_days_keys(days: int = 30) -> list[str]:
        today = datetime.utcnow().date()

        return [
            str(today - timedelta(days=offset))
            for offset in reversed(range(days))
        ]

    @staticmethod
    def _trend_from_records(
        submissions: list[Submission],
        impact_metrics: list[ImpactMetric],
        points_entries: list[PointsLedger],
        days: int = 30,
    ) -> list[dict]:
        trend = {
            date_key: {
                "date": date_key,
                "submissions": 0,
                "impact_actions": 0,
                "points_awarded": 0,
            }
            for date_key in AnalyticsService._last_n_days_keys(days)
        }

        for submission in submissions:
            if not submission.created_at:
                continue

            date_key = str(submission.created_at.date())

            if date_key in trend:
                trend[date_key]["submissions"] += 1

        for metric in impact_metrics:
            if not metric.created_at:
                continue

            date_key = str(metric.created_at.date())

            if date_key in trend:
                trend[date_key]["impact_actions"] += 1

        for entry in points_entries:
            if not entry.created_at:
                continue

            date_key = str(entry.created_at.date())

            if date_key in trend:
                trend[date_key]["points_awarded"] += int(entry.points or 0)

        return list(trend.values())

    @staticmethod
    def _get_user_submissions(
        db: Session,
        user_id: str,
    ) -> list[Submission]:
        return (
            db.query(Submission)
            .filter(Submission.user_id == user_id)
            .order_by(Submission.created_at.desc())
            .all()
        )

    @staticmethod
    def _get_submission_ids(
        submissions: list[Submission],
    ) -> list[str]:
        return [
            submission.id
            for submission in submissions
        ]

    @staticmethod
    def _get_ai_verifications_for_submissions(
        db: Session,
        submission_ids: list[str],
    ) -> list[AIVerification]:
        if not submission_ids:
            return []

        return (
            db.query(AIVerification)
            .filter(AIVerification.submission_id.in_(submission_ids))
            .all()
        )

    @staticmethod
    def _get_impact_metrics_for_submissions(
        db: Session,
        submission_ids: list[str],
    ) -> list[ImpactMetric]:
        if not submission_ids:
            return []

        return (
            db.query(ImpactMetric)
            .filter(ImpactMetric.submission_id.in_(submission_ids))
            .all()
        )

    @staticmethod
    def _get_points_for_user(
        db: Session,
        user_id: str,
    ) -> list[PointsLedger]:
        return (
            db.query(PointsLedger)
            .filter(PointsLedger.user_id == user_id)
            .order_by(PointsLedger.created_at.desc())
            .all()
        )

    @staticmethod
    def get_user_analytics(
        db: Session,
        user_id: str,
    ) -> dict:
        submissions = AnalyticsService._get_user_submissions(
            db=db,
            user_id=user_id,
        )

        submission_ids = AnalyticsService._get_submission_ids(submissions)

        ai_verifications = AnalyticsService._get_ai_verifications_for_submissions(
            db=db,
            submission_ids=submission_ids,
        )

        plant_diagnoses = (
            db.query(PlantDiagnosis)
            .filter(PlantDiagnosis.user_id == user_id)
            .all()
        )

        impact_summary = (
            db.query(UserImpactSummary)
            .filter(UserImpactSummary.user_id == user_id)
            .first()
        )

        gamification_profile = (
            db.query(UserGamificationProfile)
            .filter(UserGamificationProfile.user_id == user_id)
            .first()
        )

        impact_metrics = AnalyticsService._get_impact_metrics_for_submissions(
            db=db,
            submission_ids=submission_ids,
        )

        points_entries = AnalyticsService._get_points_for_user(
            db=db,
            user_id=user_id,
        )

        return {
            "user_id": user_id,
            "total_submissions": len(submissions),
            "submission_status_breakdown": AnalyticsService._count_by_field(
                submissions,
                "status",
            ),
            "submission_type_breakdown": AnalyticsService._count_by_field(
                submissions,
                "submission_type",
            ),
            "total_ai_verifications": len(ai_verifications),
            "ai_decision_breakdown": AnalyticsService._count_by_field(
                ai_verifications,
                "decision",
            ),
            "average_fraud_risk_score": AnalyticsService._average(
                [
                    verification.fraud_risk_score
                    for verification in ai_verifications
                ]
            ),
            "total_plant_diagnoses": len(plant_diagnoses),
            "plant_disease_breakdown": AnalyticsService._count_by_field(
                plant_diagnoses,
                "disease_name",
            ),
            "plant_severity_breakdown": AnalyticsService._count_by_field(
                plant_diagnoses,
                "severity",
            ),
            "total_co2e_saved_kg": (
                AnalyticsService._round(impact_summary.total_co2e_saved_kg)
                if impact_summary
                else 0.0
            ),
            "total_waste_diverted_kg": (
                AnalyticsService._round(impact_summary.total_waste_diverted_kg)
                if impact_summary
                else 0.0
            ),
            "total_water_saved_liters": (
                AnalyticsService._round(impact_summary.total_water_saved_liters)
                if impact_summary
                else 0.0
            ),
            "total_energy_saved_kwh": (
                AnalyticsService._round(impact_summary.total_energy_saved_kwh)
                if impact_summary
                else 0.0
            ),
            "total_trees_planted": (
                AnalyticsService._round(impact_summary.total_trees_planted)
                if impact_summary
                else 0.0
            ),
            "total_biodiversity_score": (
                AnalyticsService._round(
                    impact_summary.total_biodiversity_score
                )
                if impact_summary
                else 0.0
            ),
            "total_points": (
                gamification_profile.total_points
                if gamification_profile
                else 0
            ),
            "current_level": (
                gamification_profile.current_level
                if gamification_profile
                else 1
            ),
            "green_reputation_score": (
                AnalyticsService._round(
                    gamification_profile.green_reputation_score
                )
                if gamification_profile
                else 0.0
            ),
            "total_badges": (
                gamification_profile.total_badges
                if gamification_profile
                else 0
            ),
            "impact_actions_rewarded": (
                gamification_profile.impact_actions_rewarded
                if gamification_profile
                else 0
            ),
            "activity_trend": AnalyticsService._trend_from_records(
                submissions=submissions,
                impact_metrics=impact_metrics,
                points_entries=points_entries,
            ),
        }

    @staticmethod
    def get_challenge_analytics(
        db: Session,
        challenge_id: str,
    ) -> dict:
        challenge = (
            db.query(Challenge)
            .filter(Challenge.id == challenge_id)
            .first()
        )

        if not challenge:
            raise ValueError("Challenge not found")

        submissions = (
            db.query(Submission)
            .filter(Submission.challenge_id == challenge_id)
            .order_by(Submission.created_at.desc())
            .all()
        )

        submission_ids = AnalyticsService._get_submission_ids(submissions)

        participants = (
            db.query(ChallengeParticipant)
            .filter(ChallengeParticipant.challenge_id == challenge_id)
            .all()
        )

        ai_verifications = AnalyticsService._get_ai_verifications_for_submissions(
            db=db,
            submission_ids=submission_ids,
        )

        impact_summary = (
            db.query(ChallengeImpactSummary)
            .filter(ChallengeImpactSummary.challenge_id == challenge_id)
            .first()
        )

        impact_metrics = AnalyticsService._get_impact_metrics_for_submissions(
            db=db,
            submission_ids=submission_ids,
        )

        points_entries = []

        if submission_ids:
            points_entries = (
                db.query(PointsLedger)
                .filter(PointsLedger.submission_id.in_(submission_ids))
                .all()
            )

        return {
            "challenge_id": challenge_id,
            "total_submissions": len(submissions),
            "submission_status_breakdown": AnalyticsService._count_by_field(
                submissions,
                "status",
            ),
            "submission_type_breakdown": AnalyticsService._count_by_field(
                submissions,
                "submission_type",
            ),
            "total_participants": len(participants),
            "completed_participants": len(
                [
                    participant
                    for participant in participants
                    if participant.completed
                ]
            ),
            "total_ai_verifications": len(ai_verifications),
            "ai_decision_breakdown": AnalyticsService._count_by_field(
                ai_verifications,
                "decision",
            ),
            "average_fraud_risk_score": AnalyticsService._average(
                [
                    verification.fraud_risk_score
                    for verification in ai_verifications
                ]
            ),
            "total_co2e_saved_kg": (
                AnalyticsService._round(impact_summary.total_co2e_saved_kg)
                if impact_summary
                else 0.0
            ),
            "total_waste_diverted_kg": (
                AnalyticsService._round(impact_summary.total_waste_diverted_kg)
                if impact_summary
                else 0.0
            ),
            "total_water_saved_liters": (
                AnalyticsService._round(impact_summary.total_water_saved_liters)
                if impact_summary
                else 0.0
            ),
            "total_energy_saved_kwh": (
                AnalyticsService._round(impact_summary.total_energy_saved_kwh)
                if impact_summary
                else 0.0
            ),
            "total_trees_planted": (
                AnalyticsService._round(impact_summary.total_trees_planted)
                if impact_summary
                else 0.0
            ),
            "total_biodiversity_score": (
                AnalyticsService._round(
                    impact_summary.total_biodiversity_score
                )
                if impact_summary
                else 0.0
            ),
            "activity_trend": AnalyticsService._trend_from_records(
                submissions=submissions,
                impact_metrics=impact_metrics,
                points_entries=points_entries,
            ),
        }

    @staticmethod
    def get_admin_dashboard_analytics(
        db: Session,
    ) -> dict:
        users = db.query(User).all()
        challenges = db.query(Challenge).all()
        submissions = db.query(Submission).all()
        impact_metrics = db.query(ImpactMetric).all()
        ai_verifications = db.query(AIVerification).all()
        plant_diagnoses = db.query(PlantDiagnosis).all()
        gamification_profiles = db.query(UserGamificationProfile).all()
        points_entries = db.query(PointsLedger).all()

        total_co2e_saved_kg = AnalyticsService._round(
            sum(metric.co2e_saved_kg for metric in impact_metrics)
        )
        total_waste_diverted_kg = AnalyticsService._round(
            sum(metric.waste_diverted_kg for metric in impact_metrics)
        )
        total_water_saved_liters = AnalyticsService._round(
            sum(metric.water_saved_liters for metric in impact_metrics)
        )
        total_energy_saved_kwh = AnalyticsService._round(
            sum(metric.energy_saved_kwh for metric in impact_metrics)
        )
        total_trees_planted = AnalyticsService._round(
            sum(metric.trees_planted for metric in impact_metrics)
        )
        total_biodiversity_score = AnalyticsService._round(
            sum(metric.biodiversity_score for metric in impact_metrics)
        )

        total_points_awarded = sum(
            entry.points
            for entry in points_entries
        )

        average_green_reputation_score = AnalyticsService._average(
            [
                profile.green_reputation_score
                for profile in gamification_profiles
            ]
        )

        return {
            "total_users": len(users),
            "total_challenges": len(challenges),
            "total_submissions": len(submissions),
            "total_impact_actions": len(impact_metrics),
            "total_ai_verifications": len(ai_verifications),
            "total_plant_diagnoses": len(plant_diagnoses),
            "submission_status_breakdown": AnalyticsService._count_by_field(
                submissions,
                "status",
            ),
            "submission_type_breakdown": AnalyticsService._count_by_field(
                submissions,
                "submission_type",
            ),
            "ai_decision_breakdown": AnalyticsService._count_by_field(
                ai_verifications,
                "decision",
            ),
            "plant_severity_breakdown": AnalyticsService._count_by_field(
                plant_diagnoses,
                "severity",
            ),
            "total_co2e_saved_kg": total_co2e_saved_kg,
            "total_waste_diverted_kg": total_waste_diverted_kg,
            "total_water_saved_liters": total_water_saved_liters,
            "total_energy_saved_kwh": total_energy_saved_kwh,
            "total_trees_planted": total_trees_planted,
            "total_biodiversity_score": total_biodiversity_score,
            "total_points_awarded": total_points_awarded,
            "average_green_reputation_score": average_green_reputation_score,
            "top_impact_metrics": [
                {
                    "label": "CO2e Saved kg",
                    "value": total_co2e_saved_kg,
                },
                {
                    "label": "Trees Planted",
                    "value": total_trees_planted,
                },
                {
                    "label": "Biodiversity Score",
                    "value": total_biodiversity_score,
                },
                {
                    "label": "Waste Diverted kg",
                    "value": total_waste_diverted_kg,
                },
                {
                    "label": "Water Saved liters",
                    "value": total_water_saved_liters,
                },
                {
                    "label": "Energy Saved kWh",
                    "value": total_energy_saved_kwh,
                },
            ],
            "activity_trend": AnalyticsService._trend_from_records(
                submissions=submissions,
                impact_metrics=impact_metrics,
                points_entries=points_entries,
            ),
        }

    @staticmethod
    def get_ai_analytics(
        db: Session,
    ) -> dict:
        ai_verifications = db.query(AIVerification).all()

        high_risk_count = len(
            [
                verification
                for verification in ai_verifications
                if verification.fraud_risk_score is not None
                and verification.fraud_risk_score >= 0.55
            ]
        )

        manual_review_count = len(
            [
                verification
                for verification in ai_verifications
                if verification.decision
                == AIVerificationDecision.MANUAL_REVIEW
            ]
        )

        return {
            "total_ai_verifications": len(ai_verifications),
            "ai_status_breakdown": AnalyticsService._count_by_field(
                ai_verifications,
                "status",
            ),
            "ai_decision_breakdown": AnalyticsService._count_by_field(
                ai_verifications,
                "decision",
            ),
            "average_confidence_score": AnalyticsService._average(
                [
                    verification.confidence_score
                    for verification in ai_verifications
                ]
            ),
            "average_fraud_risk_score": AnalyticsService._average(
                [
                    verification.fraud_risk_score
                    for verification in ai_verifications
                ]
            ),
            "high_risk_verifications": high_risk_count,
            "manual_review_count": manual_review_count,
        }

    @staticmethod
    def get_plant_health_analytics(
        db: Session,
    ) -> dict:
        diagnoses = db.query(PlantDiagnosis).all()

        manual_review_count = len(
            [
                diagnosis
                for diagnosis in diagnoses
                if diagnosis.status == PlantDiagnosisStatus.MANUAL_REVIEW
            ]
        )

        return {
            "total_plant_diagnoses": len(diagnoses),
            "diagnosis_status_breakdown": AnalyticsService._count_by_field(
                diagnoses,
                "status",
            ),
            "disease_breakdown": AnalyticsService._count_by_field(
                diagnoses,
                "disease_name",
            ),
            "severity_breakdown": AnalyticsService._count_by_field(
                diagnoses,
                "severity",
            ),
            "average_confidence_score": AnalyticsService._average(
                [
                    diagnosis.confidence_score
                    for diagnosis in diagnoses
                ]
            ),
            "manual_review_count": manual_review_count,
        }

    @staticmethod
    def get_gamification_analytics(
        db: Session,
    ) -> dict:
        profiles = db.query(UserGamificationProfile).all()
        points_entries = db.query(PointsLedger).all()

        total_points_awarded = sum(
            entry.points
            for entry in points_entries
        )

        average_points_per_user = (
            AnalyticsService._round(total_points_awarded / len(profiles))
            if profiles
            else 0.0
        )

        average_green_reputation_score = AnalyticsService._average(
            [
                profile.green_reputation_score
                for profile in profiles
            ]
        )

        top_rows = (
            db.query(UserGamificationProfile, User)
            .join(User, User.id == UserGamificationProfile.user_id)
            .order_by(
                UserGamificationProfile.total_points.desc(),
                UserGamificationProfile.green_reputation_score.desc(),
            )
            .limit(5)
            .all()
        )

        top_users = []

        for rank, row in enumerate(top_rows, start=1):
            profile, user = row

            top_users.append(
                {
                    "rank": rank,
                    "user_id": profile.user_id,
                    "full_name": user.full_name,
                    "total_points": profile.total_points,
                    "current_level": profile.current_level,
                    "green_reputation_score": profile.green_reputation_score,
                    "total_badges": profile.total_badges,
                }
            )

        return {
            "total_profiles": len(profiles),
            "total_points_awarded": total_points_awarded,
            "average_points_per_user": average_points_per_user,
            "average_green_reputation_score": average_green_reputation_score,
            "total_badges_awarded": sum(
                profile.total_badges
                for profile in profiles
            ),
            "top_users": top_users,
        }