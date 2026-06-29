from datetime import datetime

from pydantic import BaseModel
from pydantic import Field

from app.core.enums import SubmissionStatus
from app.core.enums import SubmissionType


class MapImpactSummary(BaseModel):
    co2e_saved_kg: float = 0.0
    waste_diverted_kg: float = 0.0
    water_saved_liters: float = 0.0
    energy_saved_kwh: float = 0.0
    trees_planted: float = 0.0
    biodiversity_score: float = 0.0


class MapMarkerResponse(BaseModel):
    submission_id: str
    challenge_id: str | None
    user_id: str
    user_full_name: str | None

    title: str
    description: str | None
    submission_type: SubmissionType
    status: SubmissionStatus

    latitude: float
    longitude: float
    location_name: str | None

    impact: MapImpactSummary
    created_at: datetime


class GeoJSONFeatureCollectionResponse(BaseModel):
    type: str = "FeatureCollection"
    features: list[dict] = Field(default_factory=list)


class NearbyMapMarkerResponse(MapMarkerResponse):
    distance_km: float


class RegionImpactSummaryResponse(BaseModel):
    region_key: str
    center_latitude: float
    center_longitude: float

    total_submissions: int
    total_users: int
    total_challenges: int

    total_co2e_saved_kg: float
    total_waste_diverted_kg: float
    total_water_saved_liters: float
    total_energy_saved_kwh: float
    total_trees_planted: float
    total_biodiversity_score: float


class HeatmapClusterResponse(BaseModel):
    cluster_key: str
    center_latitude: float
    center_longitude: float
    intensity: float

    submission_count: int
    impact_action_count: int
    total_co2e_saved_kg: float
    total_trees_planted: float
    total_biodiversity_score: float


class MapBoundsResponse(BaseModel):
    min_latitude: float | None
    max_latitude: float | None
    min_longitude: float | None
    max_longitude: float | None
    marker_count: int