from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import Query
from fastapi import status

from sqlalchemy.orm import Session

from app.api.dependencies.auth import get_current_user
from app.core.enums import SubmissionStatus
from app.core.enums import SubmissionType
from app.db.dependencies import get_db
from app.models.user import User
from app.schemas.geospatial import GeoJSONFeatureCollectionResponse
from app.schemas.geospatial import HeatmapClusterResponse
from app.schemas.geospatial import MapBoundsResponse
from app.schemas.geospatial import MapMarkerResponse
from app.schemas.geospatial import NearbyMapMarkerResponse
from app.schemas.geospatial import RegionImpactSummaryResponse
from app.services.geospatial_service import GeospatialService


router = APIRouter()


@router.get(
    "/markers",
    response_model=list[MapMarkerResponse],
)
def get_map_markers(
    challenge_id: str | None = None,
    status_filter: SubmissionStatus | None = Query(
        default=None,
        alias="status",
    ),
    submission_type: SubmissionType | None = None,
    min_latitude: float | None = None,
    max_latitude: float | None = None,
    min_longitude: float | None = None,
    max_longitude: float | None = None,
    limit: int = Query(default=500, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return GeospatialService.get_map_markers(
        db=db,
        challenge_id=challenge_id,
        status_filter=status_filter,
        submission_type=submission_type,
        min_latitude=min_latitude,
        max_latitude=max_latitude,
        min_longitude=min_longitude,
        max_longitude=max_longitude,
        limit=limit,
    )


@router.get(
    "/geojson",
    response_model=GeoJSONFeatureCollectionResponse,
)
def get_geojson_map_data(
    challenge_id: str | None = None,
    status_filter: SubmissionStatus | None = Query(
        default=None,
        alias="status",
    ),
    submission_type: SubmissionType | None = None,
    min_latitude: float | None = None,
    max_latitude: float | None = None,
    min_longitude: float | None = None,
    max_longitude: float | None = None,
    limit: int = Query(default=500, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return GeospatialService.get_geojson(
        db=db,
        challenge_id=challenge_id,
        status_filter=status_filter,
        submission_type=submission_type,
        min_latitude=min_latitude,
        max_latitude=max_latitude,
        min_longitude=min_longitude,
        max_longitude=max_longitude,
        limit=limit,
    )


@router.get(
    "/nearby",
    response_model=list[NearbyMapMarkerResponse],
)
def get_nearby_map_markers(
    latitude: float = Query(..., ge=-90, le=90),
    longitude: float = Query(..., ge=-180, le=180),
    radius_km: float = Query(default=10.0, ge=0.1, le=500),
    challenge_id: str | None = None,
    status_filter: SubmissionStatus | None = Query(
        default=None,
        alias="status",
    ),
    submission_type: SubmissionType | None = None,
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return GeospatialService.get_nearby_markers(
        db=db,
        latitude=latitude,
        longitude=longitude,
        radius_km=radius_km,
        challenge_id=challenge_id,
        status_filter=status_filter,
        submission_type=submission_type,
        limit=limit,
    )


@router.get(
    "/bounds",
    response_model=MapBoundsResponse,
)
def get_map_bounds(
    challenge_id: str | None = None,
    status_filter: SubmissionStatus | None = Query(
        default=None,
        alias="status",
    ),
    submission_type: SubmissionType | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return GeospatialService.get_bounds(
        db=db,
        challenge_id=challenge_id,
        status_filter=status_filter,
        submission_type=submission_type,
    )


@router.get(
    "/regions/summary",
    response_model=list[RegionImpactSummaryResponse],
)
def get_region_impact_summary(
    precision: int = Query(default=2, ge=1, le=4),
    challenge_id: str | None = None,
    status_filter: SubmissionStatus | None = Query(
        default=None,
        alias="status",
    ),
    submission_type: SubmissionType | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return GeospatialService.get_region_summary(
        db=db,
        precision=precision,
        challenge_id=challenge_id,
        status_filter=status_filter,
        submission_type=submission_type,
    )


@router.get(
    "/challenges/{challenge_id}/heatmap",
    response_model=list[HeatmapClusterResponse],
)
def get_challenge_heatmap(
    challenge_id: str,
    precision: int = Query(default=2, ge=1, le=4),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return GeospatialService.get_challenge_heatmap(
            db=db,
            challenge_id=challenge_id,
            precision=precision,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc