from pydantic import BaseModel
from pydantic import Field


class AnalyticsCountItem(BaseModel):
    label: str
    count: int


class AnalyticsMetricItem(BaseModel):
    label: str
    value: float


class AnalyticsTrendItem(BaseModel):
    date: str
    submissions: int = 0
    impact_actions: int = 0
    points_awarded: int = 0


class UserAnalyticsResponse(BaseModel):
    user_id: str

    total_submissions: int
    submission_status_breakdown: list[AnalyticsCountItem]
    submission_type_breakdown: list[AnalyticsCountItem]

    total_ai_verifications: int
    ai_decision_breakdown: list[AnalyticsCountItem]
    average_fraud_risk_score: float

    total_plant_diagnoses: int
    plant_disease_breakdown: list[AnalyticsCountItem]
    plant_severity_breakdown: list[AnalyticsCountItem]

    total_co2e_saved_kg: float
    total_waste_diverted_kg: float
    total_water_saved_liters: float
    total_energy_saved_kwh: float
    total_trees_planted: float
    total_biodiversity_score: float

    total_points: int
    current_level: int
    green_reputation_score: float
    total_badges: int
    impact_actions_rewarded: int

    activity_trend: list[AnalyticsTrendItem] = Field(default_factory=list)


class ChallengeAnalyticsResponse(BaseModel):
    challenge_id: str

    total_submissions: int
    submission_status_breakdown: list[AnalyticsCountItem]
    submission_type_breakdown: list[AnalyticsCountItem]

    total_participants: int
    completed_participants: int

    total_ai_verifications: int
    ai_decision_breakdown: list[AnalyticsCountItem]
    average_fraud_risk_score: float

    total_co2e_saved_kg: float
    total_waste_diverted_kg: float
    total_water_saved_liters: float
    total_energy_saved_kwh: float
    total_trees_planted: float
    total_biodiversity_score: float

    activity_trend: list[AnalyticsTrendItem] = Field(default_factory=list)


class AdminDashboardAnalyticsResponse(BaseModel):
    total_users: int
    total_challenges: int
    total_submissions: int
    total_impact_actions: int
    total_ai_verifications: int
    total_plant_diagnoses: int

    submission_status_breakdown: list[AnalyticsCountItem]
    submission_type_breakdown: list[AnalyticsCountItem]
    ai_decision_breakdown: list[AnalyticsCountItem]
    plant_severity_breakdown: list[AnalyticsCountItem]

    total_co2e_saved_kg: float
    total_waste_diverted_kg: float
    total_water_saved_liters: float
    total_energy_saved_kwh: float
    total_trees_planted: float
    total_biodiversity_score: float

    total_points_awarded: int
    average_green_reputation_score: float

    top_impact_metrics: list[AnalyticsMetricItem]
    activity_trend: list[AnalyticsTrendItem] = Field(default_factory=list)


class AIAnalyticsResponse(BaseModel):
    total_ai_verifications: int
    ai_status_breakdown: list[AnalyticsCountItem]
    ai_decision_breakdown: list[AnalyticsCountItem]
    average_confidence_score: float
    average_fraud_risk_score: float
    high_risk_verifications: int
    manual_review_count: int


class PlantHealthAnalyticsResponse(BaseModel):
    total_plant_diagnoses: int
    diagnosis_status_breakdown: list[AnalyticsCountItem]
    disease_breakdown: list[AnalyticsCountItem]
    severity_breakdown: list[AnalyticsCountItem]
    average_confidence_score: float
    manual_review_count: int


class GamificationAnalyticsResponse(BaseModel):
    total_profiles: int
    total_points_awarded: int
    average_points_per_user: float
    average_green_reputation_score: float
    total_badges_awarded: int
    top_users: list[dict]