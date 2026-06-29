import math
from collections import defaultdict

from sqlalchemy.orm import Session

from app.core.enums import SubmissionStatus
from app.core.enums import SubmissionType
from app.models.challenge import Challenge
from app.models.impact_metric import ImpactMetric
from app.models.submission import Submission
from app.models.user import User


class GeospatialService:
    """
    Free/local geospatial aggregation service.

    No paid map API is used.
    This service prepares data for OpenStreetMap/Leaflet frontend maps.
    """

    EARTH_RADIUS_KM = 6371.0

    @staticmethod
    def _round(value: float) -> float:
        return round(float(value or 0.0), 6)

    @staticmethod
    def _round_metric(value: float) -> float:
        return round(float(value or 0.0), 3)

    @staticmethod
    def _distance_km(
        lat1: float,
        lon1: float,
        lat2: float,
        lon2: float,
    ) -> float:
        """
        Haversine distance calculation.
        Returns approximate distance between two latitude/longitude points in km.
        """

        lat1_rad = math.radians(float(lat1))
        lon1_rad = math.radians(float(lon1))
        lat2_rad = math.radians(float(lat2))
        lon2_rad = math.radians(float(lon2))

        delta_lat = lat2_rad - lat1_rad
        delta_lon = lon2_rad - lon1_rad

        a = (
            math.sin(delta_lat / 2) ** 2
            + math.cos(lat1_rad)
            * math.cos(lat2_rad)
            * math.sin(delta_lon / 2) ** 2
        )

        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        return round(GeospatialService.EARTH_RADIUS_KM * c, 3)

    @staticmethod
    def _base_location_query(db: Session):
        return (
            db.query(Submission)
            .filter(Submission.latitude.isnot(None))
            .filter(Submission.longitude.isnot(None))
        )

    @staticmethod
    def _apply_filters(
        query,
        challenge_id: str | None = None,
        status_filter: SubmissionStatus | None = None,
        submission_type: SubmissionType | None = None,
        min_latitude: float | None = None,
        max_latitude: float | None = None,
        min_longitude: float | None = None,
        max_longitude: float | None = None,
    ):
        if challenge_id:
            query = query.filter(Submission.challenge_id == challenge_id)

        if status_filter:
            query = query.filter(Submission.status == status_filter)

        if submission_type:
            query = query.filter(Submission.submission_type == submission_type)

        if min_latitude is not None:
            query = query.filter(Submission.latitude >= min_latitude)

        if max_latitude is not None:
            query = query.filter(Submission.latitude <= max_latitude)

        if min_longitude is not None:
            query = query.filter(Submission.longitude >= min_longitude)

        if max_longitude is not None:
            query = query.filter(Submission.longitude <= max_longitude)

        return query

    @staticmethod
    def _impact_map_for_submissions(
        db: Session,
        submission_ids: list[str],
    ) -> dict[str, ImpactMetric]:
        if not submission_ids:
            return {}

        metrics = (
            db.query(ImpactMetric)
            .filter(ImpactMetric.submission_id.in_(submission_ids))
            .all()
        )

        return {
            metric.submission_id: metric
            for metric in metrics
        }

    @staticmethod
    def _user_name_map(
        db: Session,
        user_ids: list[str],
    ) -> dict[str, str | None]:
        if not user_ids:
            return {}

        users = (
            db.query(User)
            .filter(User.id.in_(user_ids))
            .all()
        )

        return {
            user.id: user.full_name
            for user in users
        }

    @staticmethod
    def _impact_payload(
        impact_metric: ImpactMetric | None,
    ) -> dict:
        if not impact_metric:
            return {
                "co2e_saved_kg": 0.0,
                "waste_diverted_kg": 0.0,
                "water_saved_liters": 0.0,
                "energy_saved_kwh": 0.0,
                "trees_planted": 0.0,
                "biodiversity_score": 0.0,
            }

        return {
            "co2e_saved_kg": GeospatialService._round_metric(
                impact_metric.co2e_saved_kg
            ),
            "waste_diverted_kg": GeospatialService._round_metric(
                impact_metric.waste_diverted_kg
            ),
            "water_saved_liters": GeospatialService._round_metric(
                impact_metric.water_saved_liters
            ),
            "energy_saved_kwh": GeospatialService._round_metric(
                impact_metric.energy_saved_kwh
            ),
            "trees_planted": GeospatialService._round_metric(
                impact_metric.trees_planted
            ),
            "biodiversity_score": GeospatialService._round_metric(
                impact_metric.biodiversity_score
            ),
        }

    @staticmethod
    def _marker_payload(
        submission: Submission,
        impact_metric: ImpactMetric | None,
        user_name: str | None,
    ) -> dict:
        return {
            "submission_id": submission.id,
            "challenge_id": submission.challenge_id,
            "user_id": submission.user_id,
            "user_full_name": user_name,
            "title": submission.title,
            "description": submission.description,
            "submission_type": submission.submission_type,
            "status": submission.status,
            "latitude": GeospatialService._round(submission.latitude),
            "longitude": GeospatialService._round(submission.longitude),
            "location_name": submission.location_name,
            "impact": GeospatialService._impact_payload(impact_metric),
            "created_at": submission.created_at,
        }

    @staticmethod
    def get_map_markers(
        db: Session,
        challenge_id: str | None = None,
        status_filter: SubmissionStatus | None = None,
        submission_type: SubmissionType | None = None,
        min_latitude: float | None = None,
        max_latitude: float | None = None,
        min_longitude: float | None = None,
        max_longitude: float | None = None,
        limit: int = 500,
    ) -> list[dict]:
        limit = max(1, min(limit, 1000))

        query = GeospatialService._base_location_query(db=db)

        query = GeospatialService._apply_filters(
            query=query,
            challenge_id=challenge_id,
            status_filter=status_filter,
            submission_type=submission_type,
            min_latitude=min_latitude,
            max_latitude=max_latitude,
            min_longitude=min_longitude,
            max_longitude=max_longitude,
        )

        submissions = (
            query.order_by(Submission.created_at.desc())
            .limit(limit)
            .all()
        )

        submission_ids = [
            submission.id
            for submission in submissions
        ]

        user_ids = list(
            {
                submission.user_id
                for submission in submissions
            }
        )

        impact_map = GeospatialService._impact_map_for_submissions(
            db=db,
            submission_ids=submission_ids,
        )

        user_names = GeospatialService._user_name_map(
            db=db,
            user_ids=user_ids,
        )

        return [
            GeospatialService._marker_payload(
                submission=submission,
                impact_metric=impact_map.get(submission.id),
                user_name=user_names.get(submission.user_id),
            )
            for submission in submissions
        ]

    @staticmethod
    def get_geojson(
        db: Session,
        challenge_id: str | None = None,
        status_filter: SubmissionStatus | None = None,
        submission_type: SubmissionType | None = None,
        min_latitude: float | None = None,
        max_latitude: float | None = None,
        min_longitude: float | None = None,
        max_longitude: float | None = None,
        limit: int = 500,
    ) -> dict:
        markers = GeospatialService.get_map_markers(
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

        features = []

        for marker in markers:
            features.append(
                {
                    "type": "Feature",
                    "geometry": {
                        "type": "Point",
                        "coordinates": [
                            marker["longitude"],
                            marker["latitude"],
                        ],
                    },
                    "properties": {
                        "submission_id": marker["submission_id"],
                        "challenge_id": marker["challenge_id"],
                        "user_id": marker["user_id"],
                        "user_full_name": marker["user_full_name"],
                        "title": marker["title"],
                        "description": marker["description"],
                        "submission_type": marker["submission_type"].value,
                        "status": marker["status"].value,
                        "location_name": marker["location_name"],
                        "impact": marker["impact"],
                        "created_at": marker["created_at"].isoformat()
                        if marker["created_at"]
                        else None,
                    },
                }
            )

        return {
            "type": "FeatureCollection",
            "features": features,
        }

    @staticmethod
    def get_nearby_markers(
        db: Session,
        latitude: float,
        longitude: float,
        radius_km: float = 10.0,
        challenge_id: str | None = None,
        status_filter: SubmissionStatus | None = None,
        submission_type: SubmissionType | None = None,
        limit: int = 100,
    ) -> list[dict]:
        radius_km = max(0.1, min(float(radius_km), 500.0))
        limit = max(1, min(limit, 500))

        # Small bounding box optimization before exact Haversine distance.
        lat_delta = radius_km / 111.0
        lon_delta = radius_km / (
            111.0 * max(math.cos(math.radians(latitude)), 0.01)
        )

        markers = GeospatialService.get_map_markers(
            db=db,
            challenge_id=challenge_id,
            status_filter=status_filter,
            submission_type=submission_type,
            min_latitude=latitude - lat_delta,
            max_latitude=latitude + lat_delta,
            min_longitude=longitude - lon_delta,
            max_longitude=longitude + lon_delta,
            limit=500,
        )

        nearby = []

        for marker in markers:
            distance = GeospatialService._distance_km(
                lat1=latitude,
                lon1=longitude,
                lat2=marker["latitude"],
                lon2=marker["longitude"],
            )

            if distance > radius_km:
                continue

            marker_with_distance = {
                **marker,
                "distance_km": distance,
            }

            nearby.append(marker_with_distance)

        nearby.sort(key=lambda item: item["distance_km"])

        return nearby[:limit]

    @staticmethod
    def get_bounds(
        db: Session,
        challenge_id: str | None = None,
        status_filter: SubmissionStatus | None = None,
        submission_type: SubmissionType | None = None,
    ) -> dict:
        markers = GeospatialService.get_map_markers(
            db=db,
            challenge_id=challenge_id,
            status_filter=status_filter,
            submission_type=submission_type,
            limit=1000,
        )

        if not markers:
            return {
                "min_latitude": None,
                "max_latitude": None,
                "min_longitude": None,
                "max_longitude": None,
                "marker_count": 0,
            }

        latitudes = [
            marker["latitude"]
            for marker in markers
        ]

        longitudes = [
            marker["longitude"]
            for marker in markers
        ]

        return {
            "min_latitude": min(latitudes),
            "max_latitude": max(latitudes),
            "min_longitude": min(longitudes),
            "max_longitude": max(longitudes),
            "marker_count": len(markers),
        }

    @staticmethod
    def get_region_summary(
        db: Session,
        precision: int = 2,
        challenge_id: str | None = None,
        status_filter: SubmissionStatus | None = None,
        submission_type: SubmissionType | None = None,
    ) -> list[dict]:
        """
        Groups map points into approximate regions using rounded lat/lng.

        precision=2 roughly groups by city/neighborhood area.
        precision=1 gives wider regional grouping.
        precision=3 gives tighter grouping.
        """

        precision = max(1, min(precision, 4))

        markers = GeospatialService.get_map_markers(
            db=db,
            challenge_id=challenge_id,
            status_filter=status_filter,
            submission_type=submission_type,
            limit=1000,
        )

        groups = defaultdict(
            lambda: {
                "submissions": [],
                "user_ids": set(),
                "challenge_ids": set(),
                "co2e_saved_kg": 0.0,
                "waste_diverted_kg": 0.0,
                "water_saved_liters": 0.0,
                "energy_saved_kwh": 0.0,
                "trees_planted": 0.0,
                "biodiversity_score": 0.0,
            }
        )

        for marker in markers:
            center_lat = round(marker["latitude"], precision)
            center_lng = round(marker["longitude"], precision)
            region_key = f"{center_lat},{center_lng}"

            group = groups[region_key]
            group["submissions"].append(marker)
            group["user_ids"].add(marker["user_id"])

            if marker["challenge_id"]:
                group["challenge_ids"].add(marker["challenge_id"])

            impact = marker["impact"]

            group["co2e_saved_kg"] += impact["co2e_saved_kg"]
            group["waste_diverted_kg"] += impact["waste_diverted_kg"]
            group["water_saved_liters"] += impact["water_saved_liters"]
            group["energy_saved_kwh"] += impact["energy_saved_kwh"]
            group["trees_planted"] += impact["trees_planted"]
            group["biodiversity_score"] += impact["biodiversity_score"]

        response = []

        for region_key, group in groups.items():
            lat_text, lng_text = region_key.split(",")

            response.append(
                {
                    "region_key": region_key,
                    "center_latitude": float(lat_text),
                    "center_longitude": float(lng_text),
                    "total_submissions": len(group["submissions"]),
                    "total_users": len(group["user_ids"]),
                    "total_challenges": len(group["challenge_ids"]),
                    "total_co2e_saved_kg": GeospatialService._round_metric(
                        group["co2e_saved_kg"]
                    ),
                    "total_waste_diverted_kg": GeospatialService._round_metric(
                        group["waste_diverted_kg"]
                    ),
                    "total_water_saved_liters": GeospatialService._round_metric(
                        group["water_saved_liters"]
                    ),
                    "total_energy_saved_kwh": GeospatialService._round_metric(
                        group["energy_saved_kwh"]
                    ),
                    "total_trees_planted": GeospatialService._round_metric(
                        group["trees_planted"]
                    ),
                    "total_biodiversity_score": GeospatialService._round_metric(
                        group["biodiversity_score"]
                    ),
                }
            )

        response.sort(
            key=lambda item: item["total_submissions"],
            reverse=True,
        )

        return response

    @staticmethod
    def get_challenge_heatmap(
        db: Session,
        challenge_id: str,
        precision: int = 2,
    ) -> list[dict]:
        challenge = (
            db.query(Challenge)
            .filter(Challenge.id == challenge_id)
            .first()
        )

        if not challenge:
            raise ValueError("Challenge not found")

        regions = GeospatialService.get_region_summary(
            db=db,
            precision=precision,
            challenge_id=challenge_id,
        )

        heatmap = []

        for region in regions:
            impact_action_count = region["total_submissions"]

            intensity = (
                region["total_submissions"] * 1.0
                + region["total_co2e_saved_kg"] * 0.05
                + region["total_trees_planted"] * 2.0
                + region["total_biodiversity_score"] * 0.1
            )

            heatmap.append(
                {
                    "cluster_key": region["region_key"],
                    "center_latitude": region["center_latitude"],
                    "center_longitude": region["center_longitude"],
                    "intensity": GeospatialService._round_metric(intensity),
                    "submission_count": region["total_submissions"],
                    "impact_action_count": impact_action_count,
                    "total_co2e_saved_kg": region["total_co2e_saved_kg"],
                    "total_trees_planted": region["total_trees_planted"],
                    "total_biodiversity_score": region[
                        "total_biodiversity_score"
                    ],
                }
            )

        heatmap.sort(
            key=lambda item: item["intensity"],
            reverse=True,
        )

        return heatmap