from datetime import datetime

from pydantic import BaseModel

from app.core.enums import ImpactCalculationStatus
from app.core.enums import ImpactMetricType


class ImpactMetricResponse(BaseModel):
    id: str
    user_id: str
    challenge_id: str | None
    submission_id: str
    metric_type: ImpactMetricType
    calculation_status: ImpactCalculationStatus

    co2e_saved_kg: float
    waste_diverted_kg: float
    water_saved_liters: float
    energy_saved_kwh: float
    trees_planted: float
    transport_distance_km: float
    biodiversity_score: float

    confidence_score: float
    calculation_method: str
    assumptions_json: dict | None
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }


class UserImpactSummaryResponse(BaseModel):
    id: str
    user_id: str

    total_co2e_saved_kg: float
    total_waste_diverted_kg: float
    total_water_saved_liters: float
    total_energy_saved_kwh: float
    total_trees_planted: float
    total_transport_distance_km: float
    total_biodiversity_score: float

    impact_actions_count: int
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }


class ChallengeImpactSummaryResponse(BaseModel):
    id: str
    challenge_id: str

    total_co2e_saved_kg: float
    total_waste_diverted_kg: float
    total_water_saved_liters: float
    total_energy_saved_kwh: float
    total_trees_planted: float
    total_transport_distance_km: float
    total_biodiversity_score: float

    impact_actions_count: int
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }


class PlatformImpactSummaryResponse(BaseModel):
    total_co2e_saved_kg: float
    total_waste_diverted_kg: float
    total_water_saved_liters: float
    total_energy_saved_kwh: float
    total_trees_planted: float
    total_transport_distance_km: float
    total_biodiversity_score: float
    impact_actions_count: int
    calculation_method: str