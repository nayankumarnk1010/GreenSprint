from sqlalchemy.orm import Session

from app.core.enums import BadgeCategory
from app.core.enums import ImpactCalculationStatus
from app.core.enums import PointsSourceType
from app.core.enums import PointsTransactionType
from app.core.enums import SubmissionStatus
from app.core.enums import SubmissionType
from app.models.badge import Badge
from app.models.impact_metric import ImpactMetric
from app.models.points_ledger import PointsLedger
from app.models.submission import Submission
from app.models.user import User
from app.models.user_badge import UserBadge
from app.models.user_gamification_profile import UserGamificationProfile


class GamificationService:
    """
    Free/local gamification engine.

    No paid API is used.
    Current logic is deterministic and fraud-aware.
    Later AI upgrades:
    - personalized reward optimization
    - motivation-based badge recommendations
    - fraud-aware dynamic point adjustment
    - engagement prediction
    """

    BASE_POINTS_BY_SUBMISSION_TYPE = {
        SubmissionType.TREE_PLANTATION: 100,
        SubmissionType.RECYCLING: 40,
        SubmissionType.WASTE_CLEANUP: 60,
        SubmissionType.WATER_CONSERVATION: 30,
        SubmissionType.ENERGY_SAVING: 35,
        SubmissionType.SUSTAINABLE_TRANSPORT: 50,
        SubmissionType.PLANT_HEALTH_CHECK: 25,
        SubmissionType.COMMUNITY_SERVICE: 45,
        SubmissionType.OTHER: 20,
    }

    DEFAULT_BADGES = [
        {
            "code": "ECO_STARTER",
            "name": "Eco Starter",
            "description": "Awarded for completing the first rewarded sustainability action.",
            "category": BadgeCategory.STARTER,
            "points_threshold": 1,
            "badge_points_bonus": 10,
            "requirements_json": {
                "impact_actions_rewarded_min": 1,
            },
        },
        {
            "code": "TREE_STARTER",
            "name": "Tree Starter",
            "description": "Awarded for completing the first tree plantation impact action.",
            "category": BadgeCategory.TREE_PLANTATION,
            "points_threshold": 100,
            "badge_points_bonus": 20,
            "requirements_json": {
                "trees_planted_min": 1,
            },
        },
        {
            "code": "CARBON_SAVER",
            "name": "Carbon Saver",
            "description": "Awarded after saving at least 20 kg of estimated CO2e.",
            "category": BadgeCategory.IMPACT,
            "points_threshold": 100,
            "badge_points_bonus": 20,
            "requirements_json": {
                "co2e_saved_kg_min": 20,
            },
        },
        {
            "code": "RISING_CHAMPION",
            "name": "Rising Green Champion",
            "description": "Awarded after earning at least 250 total points.",
            "category": BadgeCategory.IMPACT,
            "points_threshold": 250,
            "badge_points_bonus": 30,
            "requirements_json": {
                "total_points_min": 250,
            },
        },
        {
            "code": "GREEN_HERO",
            "name": "Green Hero",
            "description": "Awarded after earning at least 1000 total points.",
            "category": BadgeCategory.IMPACT,
            "points_threshold": 1000,
            "badge_points_bonus": 100,
            "requirements_json": {
                "total_points_min": 1000,
            },
        },
        {
            "code": "PLANT_HEALER",
            "name": "Plant Healer",
            "description": "Awarded for completing a plant health check.",
            "category": BadgeCategory.PLANT_HEALTH,
            "points_threshold": 25,
            "badge_points_bonus": 10,
            "requirements_json": {
                "plant_health_checks_min": 1,
            },
        },
    ]

    @staticmethod
    def _get_or_create_profile(
        db: Session,
        user_id: str,
    ) -> UserGamificationProfile:
        profile = (
            db.query(UserGamificationProfile)
            .filter(UserGamificationProfile.user_id == user_id)
            .first()
        )

        if profile:
            return profile

        profile = UserGamificationProfile(
            user_id=user_id,
            total_points=0,
            current_level=1,
            green_reputation_score=0.0,
            total_badges=0,
            impact_actions_rewarded=0,
            ai_verified_actions=0,
            approved_actions=0,
            rejected_actions=0,
        )

        db.add(profile)
        db.flush()

        return profile

    @staticmethod
    def _calculate_level(total_points: int) -> int:
        if total_points < 100:
            return 1

        return min(50, int(total_points // 100) + 1)

    @staticmethod
    def _calculate_green_reputation_score(
        total_points: int,
        impact_actions: int,
        approved_actions: int,
        rejected_actions: int,
        total_badges: int,
    ) -> float:
        score = 0.0

        score += min(total_points / 10, 50)
        score += min(impact_actions * 5, 25)
        score += min(approved_actions * 3, 15)
        score += min(total_badges * 2, 10)

        if rejected_actions > 0:
            score -= min(rejected_actions * 10, 30)

        return round(max(0.0, min(100.0, score)), 2)

    @staticmethod
    def _ensure_default_badges(db: Session) -> None:
        existing_codes = {
            badge.code
            for badge in db.query(Badge).all()
        }

        for payload in GamificationService.DEFAULT_BADGES:
            if payload["code"] in existing_codes:
                continue

            badge = Badge(
                code=payload["code"],
                name=payload["name"],
                description=payload["description"],
                category=payload["category"],
                points_threshold=payload["points_threshold"],
                badge_points_bonus=payload["badge_points_bonus"],
                requirements_json=payload["requirements_json"],
                is_active=True,
            )

            db.add(badge)

        db.flush()

    @staticmethod
    def _get_submission(
        db: Session,
        submission_id: str,
    ) -> Submission | None:
        return (
            db.query(Submission)
            .filter(Submission.id == submission_id)
            .first()
        )

    @staticmethod
    def _get_submission_impact(
        db: Session,
        submission_id: str,
    ) -> ImpactMetric | None:
        return (
            db.query(ImpactMetric)
            .filter(ImpactMetric.submission_id == submission_id)
            .first()
        )

    @staticmethod
    def _calculate_submission_points(
        submission: Submission,
        impact: ImpactMetric,
    ) -> tuple[int, dict]:
        base_points = GamificationService.BASE_POINTS_BY_SUBMISSION_TYPE.get(
            submission.submission_type,
            20,
        )

        impact_bonus = 0

        if impact.co2e_saved_kg >= 20:
            impact_bonus += 10

        if impact.trees_planted >= 1:
            impact_bonus += 10

        if impact.waste_diverted_kg >= 2:
            impact_bonus += 5

        if impact.biodiversity_score >= 10:
            impact_bonus += 10

        verification_bonus = 0

        if submission.status == SubmissionStatus.AI_VERIFIED:
            verification_bonus += 20

        if submission.status == SubmissionStatus.APPROVED:
            verification_bonus += 30

        if impact.calculation_status == ImpactCalculationStatus.CONFIRMED:
            verification_bonus += 10

        total_points = base_points + impact_bonus + verification_bonus

        details = {
            "base_points": base_points,
            "impact_bonus": impact_bonus,
            "verification_bonus": verification_bonus,
            "submission_status": submission.status.value,
            "impact_status": impact.calculation_status.value,
            "fraud_aware_note": (
                "Rejected submissions receive no points. "
                "Manual-review submissions can receive base estimated rewards, "
                "but approval/AI bonuses are added only after verification or approval."
            ),
        }

        return total_points, details

    @staticmethod
    def _count_user_badges(
        db: Session,
        user_id: str,
    ) -> int:
        return (
            db.query(UserBadge)
            .filter(UserBadge.user_id == user_id)
            .count()
        )

    @staticmethod
    def _user_total_tree_count(
        db: Session,
        user_id: str,
    ) -> float:
        metrics = (
            db.query(ImpactMetric)
            .filter(ImpactMetric.user_id == user_id)
            .all()
        )

        return sum(metric.trees_planted for metric in metrics)

    @staticmethod
    def _user_total_co2e_saved(
        db: Session,
        user_id: str,
    ) -> float:
        metrics = (
            db.query(ImpactMetric)
            .filter(ImpactMetric.user_id == user_id)
            .all()
        )

        return sum(metric.co2e_saved_kg for metric in metrics)

    @staticmethod
    def _user_plant_health_checks(
        db: Session,
        user_id: str,
    ) -> int:
        return (
            db.query(Submission)
            .filter(Submission.user_id == user_id)
            .filter(Submission.submission_type == SubmissionType.PLANT_HEALTH_CHECK)
            .count()
        )

    @staticmethod
    def _award_eligible_badges(
        db: Session,
        user_id: str,
        submission_id: str | None,
        profile: UserGamificationProfile,
    ) -> list[Badge]:
        GamificationService._ensure_default_badges(db=db)

        active_badges = (
            db.query(Badge)
            .filter(Badge.is_active == True)
            .all()
        )

        existing_badge_ids = {
            user_badge.badge_id
            for user_badge in (
                db.query(UserBadge)
                .filter(UserBadge.user_id == user_id)
                .all()
            )
        }

        total_trees = GamificationService._user_total_tree_count(
            db=db,
            user_id=user_id,
        )

        total_co2e = GamificationService._user_total_co2e_saved(
            db=db,
            user_id=user_id,
        )

        plant_health_checks = GamificationService._user_plant_health_checks(
            db=db,
            user_id=user_id,
        )

        awarded_badges: list[Badge] = []

        for badge in active_badges:
            if badge.id in existing_badge_ids:
                continue

            requirements = badge.requirements_json or {}

            eligible = True

            if (
                requirements.get("impact_actions_rewarded_min") is not None
                and profile.impact_actions_rewarded
                < int(requirements["impact_actions_rewarded_min"])
            ):
                eligible = False

            if (
                requirements.get("trees_planted_min") is not None
                and total_trees < float(requirements["trees_planted_min"])
            ):
                eligible = False

            if (
                requirements.get("co2e_saved_kg_min") is not None
                and total_co2e < float(requirements["co2e_saved_kg_min"])
            ):
                eligible = False

            if (
                requirements.get("total_points_min") is not None
                and profile.total_points < int(requirements["total_points_min"])
            ):
                eligible = False

            if (
                requirements.get("plant_health_checks_min") is not None
                and plant_health_checks < int(requirements["plant_health_checks_min"])
            ):
                eligible = False

            if not eligible:
                continue

            user_badge = UserBadge(
                user_id=user_id,
                badge_id=badge.id,
                awarded_from_submission_id=submission_id,
            )

            db.add(user_badge)
            awarded_badges.append(badge)

            if badge.badge_points_bonus > 0:
                bonus_entry = PointsLedger(
                    user_id=user_id,
                    submission_id=None,
                    points=badge.badge_points_bonus,
                    transaction_type=PointsTransactionType.BONUS,
                    source_type=PointsSourceType.BADGE_BONUS,
                    description=f"Badge bonus awarded for {badge.name}",
                    metadata_json={
                        "badge_code": badge.code,
                        "badge_name": badge.name,
                    },
                )

                db.add(bonus_entry)
                profile.total_points += badge.badge_points_bonus

        profile.total_badges = GamificationService._count_user_badges(
            db=db,
            user_id=user_id,
        ) + len(awarded_badges)

        profile.current_level = GamificationService._calculate_level(
            profile.total_points
        )

        profile.green_reputation_score = (
            GamificationService._calculate_green_reputation_score(
                total_points=profile.total_points,
                impact_actions=profile.impact_actions_rewarded,
                approved_actions=profile.approved_actions,
                rejected_actions=profile.rejected_actions,
                total_badges=profile.total_badges,
            )
        )

        db.flush()

        return awarded_badges

    @staticmethod
    def award_submission_points(
        db: Session,
        submission_id: str,
    ) -> dict:
        submission = GamificationService._get_submission(
            db=db,
            submission_id=submission_id,
        )

        if not submission:
            raise ValueError("Submission not found")

        existing_entry = (
            db.query(PointsLedger)
            .filter(PointsLedger.submission_id == submission_id)
            .first()
        )

        if existing_entry:
            profile = GamificationService._get_or_create_profile(
                db=db,
                user_id=submission.user_id,
            )

            return {
                "profile": profile,
                "ledger_entry": existing_entry,
                "badges_awarded": [],
                "message": "Points already awarded for this submission.",
            }

        if submission.status in {
            SubmissionStatus.REJECTED,
            SubmissionStatus.AI_REJECTED,
        }:
            profile = GamificationService._get_or_create_profile(
                db=db,
                user_id=submission.user_id,
            )
            profile.rejected_actions += 1
            db.commit()
            db.refresh(profile)

            raise ValueError(
                "Rejected submissions cannot receive gamification points."
            )

        impact = GamificationService._get_submission_impact(
            db=db,
            submission_id=submission_id,
        )

        if not impact:
            raise ValueError(
                "Impact metric not found. Calculate environmental impact first."
            )

        profile = GamificationService._get_or_create_profile(
            db=db,
            user_id=submission.user_id,
        )

        points, details = GamificationService._calculate_submission_points(
            submission=submission,
            impact=impact,
        )

        ledger_entry = PointsLedger(
            user_id=submission.user_id,
            submission_id=submission.id,
            points=points,
            transaction_type=PointsTransactionType.EARNED,
            source_type=PointsSourceType.SUBMISSION,
            description=f"Points awarded for {submission.submission_type.value} submission.",
            metadata_json={
                "submission_type": submission.submission_type.value,
                "impact_metric_id": impact.id,
                "points_breakdown": details,
            },
        )

        db.add(ledger_entry)

        profile.total_points += points
        profile.impact_actions_rewarded += 1

        if submission.status == SubmissionStatus.AI_VERIFIED:
            profile.ai_verified_actions += 1

        if submission.status == SubmissionStatus.APPROVED:
            profile.approved_actions += 1

        profile.current_level = GamificationService._calculate_level(
            profile.total_points
        )

        profile.green_reputation_score = (
            GamificationService._calculate_green_reputation_score(
                total_points=profile.total_points,
                impact_actions=profile.impact_actions_rewarded,
                approved_actions=profile.approved_actions,
                rejected_actions=profile.rejected_actions,
                total_badges=profile.total_badges,
            )
        )

        db.flush()

        badges_awarded = GamificationService._award_eligible_badges(
            db=db,
            user_id=submission.user_id,
            submission_id=submission.id,
            profile=profile,
        )

        profile.current_level = GamificationService._calculate_level(
            profile.total_points
        )

        profile.green_reputation_score = (
            GamificationService._calculate_green_reputation_score(
                total_points=profile.total_points,
                impact_actions=profile.impact_actions_rewarded,
                approved_actions=profile.approved_actions,
                rejected_actions=profile.rejected_actions,
                total_badges=profile.total_badges,
            )
        )

        db.commit()
        db.refresh(profile)
        db.refresh(ledger_entry)

        return {
            "profile": profile,
            "ledger_entry": ledger_entry,
            "badges_awarded": badges_awarded,
            "message": "Points awarded successfully.",
        }

    @staticmethod
    def get_all_badges(
        db: Session,
    ) -> list[Badge]:
        GamificationService._ensure_default_badges(db=db)
        db.commit()

        return (
            db.query(Badge)
            .filter(Badge.is_active == True)
            .order_by(Badge.points_threshold.asc())
            .all()
        )

    @staticmethod
    def get_user_badges(
        db: Session,
        user_id: str,
    ) -> list[dict]:
        user_badges = (
            db.query(UserBadge)
            .filter(UserBadge.user_id == user_id)
            .order_by(UserBadge.awarded_at.desc())
            .all()
        )

        results = []

        for user_badge in user_badges:
            badge = (
                db.query(Badge)
                .filter(Badge.id == user_badge.badge_id)
                .first()
            )

            results.append(
                {
                    "id": user_badge.id,
                    "user_id": user_badge.user_id,
                    "badge_id": user_badge.badge_id,
                    "awarded_from_submission_id": (
                        user_badge.awarded_from_submission_id
                    ),
                    "awarded_at": user_badge.awarded_at,
                    "badge": badge,
                }
            )

        return results

    @staticmethod
    def get_user_detail(
        db: Session,
        user_id: str,
    ) -> dict:
        profile = GamificationService._get_or_create_profile(
            db=db,
            user_id=user_id,
        )

        badges = [
            item["badge"]
            for item in GamificationService.get_user_badges(
                db=db,
                user_id=user_id,
            )
            if item["badge"] is not None
        ]

        recent_points = (
            db.query(PointsLedger)
            .filter(PointsLedger.user_id == user_id)
            .order_by(PointsLedger.created_at.desc())
            .limit(10)
            .all()
        )

        db.commit()
        db.refresh(profile)

        return {
            "profile": profile,
            "badges": badges,
            "recent_points": recent_points,
        }

    @staticmethod
    def get_leaderboard(
        db: Session,
        limit: int = 10,
    ) -> list[dict]:
        limit = max(1, min(limit, 100))

        rows = (
            db.query(UserGamificationProfile, User)
            .join(User, User.id == UserGamificationProfile.user_id)
            .order_by(
                UserGamificationProfile.total_points.desc(),
                UserGamificationProfile.green_reputation_score.desc(),
                UserGamificationProfile.updated_at.asc(),
            )
            .limit(limit)
            .all()
        )

        leaderboard = []

        for index, row in enumerate(rows, start=1):
            profile, user = row

            leaderboard.append(
                {
                    "rank": index,
                    "user_id": profile.user_id,
                    "full_name": user.full_name,
                    "total_points": profile.total_points,
                    "current_level": profile.current_level,
                    "green_reputation_score": profile.green_reputation_score,
                    "total_badges": profile.total_badges,
                    "impact_actions_rewarded": profile.impact_actions_rewarded,
                }
            )

        return leaderboard