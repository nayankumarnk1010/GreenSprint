from sqlalchemy.orm import Session

from app.core.enums import ImpactCalculationStatus
from app.core.enums import ImpactMetricType
from app.core.enums import SubmissionStatus
from app.core.enums import SubmissionType
from app.models.challenge import Challenge
from app.models.challenge_impact_summary import ChallengeImpactSummary
from app.models.impact_metric import ImpactMetric
from app.models.submission import Submission
from app.models.user_impact_summary import UserImpactSummary


class ImpactService:
    """
    Free/local environmental impact calculation engine.
    """

    CALCULATION_METHOD = "local_impact_estimator_v1"

    @staticmethod
    def _round(value: float) -> float:
        return round(float(value or 0.0), 3)

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
    def _get_challenge(
        db: Session,
        challenge_id: str | None,
    ) -> Challenge | None:
        if not challenge_id:
            return None

        return (
            db.query(Challenge)
            .filter(Challenge.id == challenge_id)
            .first()
        )

    @staticmethod
    def _status_from_submission(
        submission: Submission,
    ) -> ImpactCalculationStatus:
        if submission.status in {
            SubmissionStatus.APPROVED,
            SubmissionStatus.AI_VERIFIED,
        }:
            return ImpactCalculationStatus.CONFIRMED

        if submission.status in {
            SubmissionStatus.MANUAL_REVIEW,
            SubmissionStatus.PENDING,
            SubmissionStatus.AI_REVIEWING,
        }:
            return ImpactCalculationStatus.ESTIMATED

        if submission.status in {
            SubmissionStatus.AI_REJECTED,
            SubmissionStatus.REJECTED,
        }:
            return ImpactCalculationStatus.NEEDS_REVIEW

        return ImpactCalculationStatus.ESTIMATED

    @staticmethod
    def _estimate_impact(
        submission: Submission,
        challenge: Challenge | None,
    ) -> dict:
        submission_type = submission.submission_type

        base = {
            "metric_type": ImpactMetricType.MIXED,
            "co2e_saved_kg": 0.0,
            "waste_diverted_kg": 0.0,
            "water_saved_liters": 0.0,
            "energy_saved_kwh": 0.0,
            "trees_planted": 0.0,
            "transport_distance_km": 0.0,
            "biodiversity_score": 0.0,
            "confidence_score": 0.72,
            "assumptions_json": {
                "engine": ImpactService.CALCULATION_METHOD,
                "paid_api_used": False,
                "note": (
                    "These are transparent MVP estimates. "
                    "They can be improved later with regional emission factors "
                    "and AI-based prediction."
                ),
                "challenge_target_value": (
                    challenge.target_value if challenge else None
                ),
            },
        }

        if submission_type == SubmissionType.TREE_PLANTATION:
            base.update(
                {
                    "metric_type": ImpactMetricType.TREE_PLANTATION,
                    "co2e_saved_kg": 21.77,
                    "trees_planted": 1.0,
                    "biodiversity_score": 10.0,
                    "confidence_score": 0.82,
                }
            )
            base["assumptions_json"].update(
                {
                    "assumption": "One submitted tree plantation action equals one tree.",
                    "co2_basis": "Approximate annual CO2 absorption estimate per young tree.",
                    "unit": "per tree per year",
                }
            )

        elif submission_type == SubmissionType.RECYCLING:
            base.update(
                {
                    "metric_type": ImpactMetricType.WASTE_DIVERSION,
                    "co2e_saved_kg": 1.5,
                    "waste_diverted_kg": 1.0,
                    "confidence_score": 0.74,
                }
            )
            base["assumptions_json"].update(
                {
                    "assumption": "One recycling submission equals around 1 kg diverted waste.",
                    "co2_basis": "Approximate avoided emissions from recycling mixed household waste.",
                    "unit": "per submission",
                }
            )

        elif submission_type == SubmissionType.WASTE_CLEANUP:
            base.update(
                {
                    "metric_type": ImpactMetricType.WASTE_DIVERSION,
                    "co2e_saved_kg": 1.2,
                    "waste_diverted_kg": 2.0,
                    "biodiversity_score": 3.0,
                    "confidence_score": 0.72,
                }
            )
            base["assumptions_json"].update(
                {
                    "assumption": "One cleanup submission equals around 2 kg collected waste.",
                    "co2_basis": "Approximate environmental benefit from waste diversion.",
                    "unit": "per cleanup proof",
                }
            )

        elif submission_type == SubmissionType.WATER_CONSERVATION:
            base.update(
                {
                    "metric_type": ImpactMetricType.WATER_SAVED,
                    "water_saved_liters": 10.0,
                    "confidence_score": 0.68,
                }
            )
            base["assumptions_json"].update(
                {
                    "assumption": "One water conservation action saves around 10 liters.",
                    "unit": "per submission",
                }
            )

        elif submission_type == SubmissionType.ENERGY_SAVING:
            base.update(
                {
                    "metric_type": ImpactMetricType.ENERGY_SAVED,
                    "co2e_saved_kg": 0.82,
                    "energy_saved_kwh": 1.0,
                    "confidence_score": 0.68,
                }
            )
            base["assumptions_json"].update(
                {
                    "assumption": "One energy saving action saves around 1 kWh.",
                    "co2_basis": "Approximate grid emission saving.",
                    "unit": "per submission",
                }
            )

        elif submission_type == SubmissionType.SUSTAINABLE_TRANSPORT:
            base.update(
                {
                    "metric_type": ImpactMetricType.TRANSPORT_EMISSION_SAVED,
                    "co2e_saved_kg": 0.75,
                    "transport_distance_km": 5.0,
                    "confidence_score": 0.70,
                }
            )
            base["assumptions_json"].update(
                {
                    "assumption": "One sustainable transport action replaces around 5 km of car travel.",
                    "co2_basis": "Approximate avoided passenger transport emission.",
                    "unit": "per submission",
                }
            )

        elif submission_type == SubmissionType.PLANT_HEALTH_CHECK:
            base.update(
                {
                    "metric_type": ImpactMetricType.PLANT_HEALTH,
                    "biodiversity_score": 2.0,
                    "confidence_score": 0.70,
                }
            )
            base["assumptions_json"].update(
                {
                    "assumption": "Plant health diagnosis contributes to plant survival monitoring.",
                    "unit": "per plant health check",
                }
            )

        else:
            base["assumptions_json"].update(
                {
                    "assumption": "Generic sustainability action. Impact requires manual or future AI classification.",
                    "unit": "per submission",
                }
            )

        return base

    @staticmethod
    def _refresh_user_summary(
        db: Session,
        user_id: str,
    ) -> UserImpactSummary:
        metrics = (
            db.query(ImpactMetric)
            .filter(ImpactMetric.user_id == user_id)
            .filter(
                ImpactMetric.calculation_status
                != ImpactCalculationStatus.FAILED
            )
            .all()
        )

        summary = (
            db.query(UserImpactSummary)
            .filter(UserImpactSummary.user_id == user_id)
            .first()
        )

        if not summary:
            summary = UserImpactSummary(user_id=user_id)
            db.add(summary)
            db.flush()

        summary.total_co2e_saved_kg = ImpactService._round(
            sum(metric.co2e_saved_kg for metric in metrics)
        )
        summary.total_waste_diverted_kg = ImpactService._round(
            sum(metric.waste_diverted_kg for metric in metrics)
        )
        summary.total_water_saved_liters = ImpactService._round(
            sum(metric.water_saved_liters for metric in metrics)
        )
        summary.total_energy_saved_kwh = ImpactService._round(
            sum(metric.energy_saved_kwh for metric in metrics)
        )
        summary.total_trees_planted = ImpactService._round(
            sum(metric.trees_planted for metric in metrics)
        )
        summary.total_transport_distance_km = ImpactService._round(
            sum(metric.transport_distance_km for metric in metrics)
        )
        summary.total_biodiversity_score = ImpactService._round(
            sum(metric.biodiversity_score for metric in metrics)
        )
        summary.impact_actions_count = len(metrics)

        db.flush()
        return summary

    @staticmethod
    def _refresh_challenge_summary(
        db: Session,
        challenge_id: str,
    ) -> ChallengeImpactSummary:
        metrics = (
            db.query(ImpactMetric)
            .filter(ImpactMetric.challenge_id == challenge_id)
            .filter(
                ImpactMetric.calculation_status
                != ImpactCalculationStatus.FAILED
            )
            .all()
        )

        summary = (
            db.query(ChallengeImpactSummary)
            .filter(ChallengeImpactSummary.challenge_id == challenge_id)
            .first()
        )

        if not summary:
            summary = ChallengeImpactSummary(challenge_id=challenge_id)
            db.add(summary)
            db.flush()

        summary.total_co2e_saved_kg = ImpactService._round(
            sum(metric.co2e_saved_kg for metric in metrics)
        )
        summary.total_waste_diverted_kg = ImpactService._round(
            sum(metric.waste_diverted_kg for metric in metrics)
        )
        summary.total_water_saved_liters = ImpactService._round(
            sum(metric.water_saved_liters for metric in metrics)
        )
        summary.total_energy_saved_kwh = ImpactService._round(
            sum(metric.energy_saved_kwh for metric in metrics)
        )
        summary.total_trees_planted = ImpactService._round(
            sum(metric.trees_planted for metric in metrics)
        )
        summary.total_transport_distance_km = ImpactService._round(
            sum(metric.transport_distance_km for metric in metrics)
        )
        summary.total_biodiversity_score = ImpactService._round(
            sum(metric.biodiversity_score for metric in metrics)
        )
        summary.impact_actions_count = len(metrics)

        db.flush()
        return summary

    @staticmethod
    def calculate_submission_impact(
        db: Session,
        submission_id: str,
    ) -> ImpactMetric:
        submission = ImpactService._get_submission(
            db=db,
            submission_id=submission_id,
        )

        if not submission:
            raise ValueError("Submission not found")

        challenge = ImpactService._get_challenge(
            db=db,
            challenge_id=submission.challenge_id,
        )

        estimated = ImpactService._estimate_impact(
            submission=submission,
            challenge=challenge,
        )

        calculation_status = ImpactService._status_from_submission(submission)

        metric = (
            db.query(ImpactMetric)
            .filter(ImpactMetric.submission_id == submission_id)
            .first()
        )

        if not metric:
            metric = ImpactMetric(
                user_id=submission.user_id,
                challenge_id=submission.challenge_id,
                submission_id=submission.id,
                metric_type=estimated["metric_type"],
                calculation_status=calculation_status,
                co2e_saved_kg=ImpactService._round(estimated["co2e_saved_kg"]),
                waste_diverted_kg=ImpactService._round(
                    estimated["waste_diverted_kg"]
                ),
                water_saved_liters=ImpactService._round(
                    estimated["water_saved_liters"]
                ),
                energy_saved_kwh=ImpactService._round(
                    estimated["energy_saved_kwh"]
                ),
                trees_planted=ImpactService._round(estimated["trees_planted"]),
                transport_distance_km=ImpactService._round(
                    estimated["transport_distance_km"]
                ),
                biodiversity_score=ImpactService._round(
                    estimated["biodiversity_score"]
                ),
                confidence_score=ImpactService._round(
                    estimated["confidence_score"]
                ),
                calculation_method=ImpactService.CALCULATION_METHOD,
                assumptions_json=estimated["assumptions_json"],
            )
            db.add(metric)

        else:
            metric.metric_type = estimated["metric_type"]
            metric.calculation_status = calculation_status
            metric.co2e_saved_kg = ImpactService._round(
                estimated["co2e_saved_kg"]
            )
            metric.waste_diverted_kg = ImpactService._round(
                estimated["waste_diverted_kg"]
            )
            metric.water_saved_liters = ImpactService._round(
                estimated["water_saved_liters"]
            )
            metric.energy_saved_kwh = ImpactService._round(
                estimated["energy_saved_kwh"]
            )
            metric.trees_planted = ImpactService._round(
                estimated["trees_planted"]
            )
            metric.transport_distance_km = ImpactService._round(
                estimated["transport_distance_km"]
            )
            metric.biodiversity_score = ImpactService._round(
                estimated["biodiversity_score"]
            )
            metric.confidence_score = ImpactService._round(
                estimated["confidence_score"]
            )
            metric.calculation_method = ImpactService.CALCULATION_METHOD
            metric.assumptions_json = estimated["assumptions_json"]

        db.flush()

        ImpactService._refresh_user_summary(
            db=db,
            user_id=submission.user_id,
        )

        if submission.challenge_id:
            ImpactService._refresh_challenge_summary(
                db=db,
                challenge_id=submission.challenge_id,
            )

        db.commit()
        db.refresh(metric)

        return metric

    @staticmethod
    def get_submission_impact(
        db: Session,
        submission_id: str,
    ) -> ImpactMetric | None:
        return (
            db.query(ImpactMetric)
            .filter(ImpactMetric.submission_id == submission_id)
            .first()
        )

    @staticmethod
    def get_user_summary(
        db: Session,
        user_id: str,
    ) -> UserImpactSummary:
        summary = (
            db.query(UserImpactSummary)
            .filter(UserImpactSummary.user_id == user_id)
            .first()
        )

        if not summary:
            summary = ImpactService._refresh_user_summary(
                db=db,
                user_id=user_id,
            )
            db.commit()
            db.refresh(summary)

        return summary

    @staticmethod
    def get_challenge_summary(
        db: Session,
        challenge_id: str,
    ) -> ChallengeImpactSummary:
        challenge = (
            db.query(Challenge)
            .filter(Challenge.id == challenge_id)
            .first()
        )

        if not challenge:
            raise ValueError("Challenge not found")

        summary = (
            db.query(ChallengeImpactSummary)
            .filter(ChallengeImpactSummary.challenge_id == challenge_id)
            .first()
        )

        if not summary:
            summary = ImpactService._refresh_challenge_summary(
                db=db,
                challenge_id=challenge_id,
            )
            db.commit()
            db.refresh(summary)

        return summary

    @staticmethod
    def get_platform_summary(
        db: Session,
    ) -> dict:
        metrics = (
            db.query(ImpactMetric)
            .filter(
                ImpactMetric.calculation_status
                != ImpactCalculationStatus.FAILED
            )
            .all()
        )

        return {
            "total_co2e_saved_kg": ImpactService._round(
                sum(metric.co2e_saved_kg for metric in metrics)
            ),
            "total_waste_diverted_kg": ImpactService._round(
                sum(metric.waste_diverted_kg for metric in metrics)
            ),
            "total_water_saved_liters": ImpactService._round(
                sum(metric.water_saved_liters for metric in metrics)
            ),
            "total_energy_saved_kwh": ImpactService._round(
                sum(metric.energy_saved_kwh for metric in metrics)
            ),
            "total_trees_planted": ImpactService._round(
                sum(metric.trees_planted for metric in metrics)
            ),
            "total_transport_distance_km": ImpactService._round(
                sum(metric.transport_distance_km for metric in metrics)
            ),
            "total_biodiversity_score": ImpactService._round(
                sum(metric.biodiversity_score for metric in metrics)
            ),
            "impact_actions_count": len(metrics),
            "calculation_method": ImpactService.CALCULATION_METHOD,
        }