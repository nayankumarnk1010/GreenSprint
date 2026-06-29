from datetime import date
from datetime import datetime
from pathlib import Path
from typing import Any

from sqlalchemy.orm import Session

from app.core.enums import MediaType
from app.core.enums import PlantDiagnosisStatus
from app.core.enums import PlantDiseaseSeverity
from app.core.enums import PlantRecommendationType
from app.models.plant_care_recommendation import PlantCareRecommendation
from app.models.plant_diagnosis import PlantDiagnosis
from app.models.submission import Submission
from app.models.submission_media import SubmissionMedia
from app.services.ai.plant_disease_ai_service import PlantDiseaseAIService

try:
    from PIL import Image
except ImportError:
    Image = None


class PlantHealthService:
    """
    Plant health diagnosis service.

    This upgraded version uses:
    1. Pretrained MobileNetV2 plant disease model
    2. Treatment recommendation dataset
    3. Plant guide answer generation
    4. Safe fallback to local color heuristics if model prediction fails

    No paid API is required.
    """

    MODEL_NAME = "pretrained_mobilenetv2_plant_disease_plus_guide"
    FALLBACK_MODEL_NAME = "local_plant_health_rules_fallback_v1"

    @staticmethod
    def _get_latest_image_media(
        db: Session,
        submission_id: str,
    ) -> SubmissionMedia | None:
        return (
            db.query(SubmissionMedia)
            .filter(SubmissionMedia.submission_id == submission_id)
            .filter(SubmissionMedia.file_type == MediaType.IMAGE)
            .order_by(SubmissionMedia.uploaded_at.desc())
            .first()
        )

    @staticmethod
    def _enum_value(
        value: Any,
    ) -> Any:
        return getattr(
            value,
            "value",
            value,
        )

    @staticmethod
    def _json_safe(
        value: Any,
    ) -> Any:
        if isinstance(
            value,
            (
                datetime,
                date,
            ),
        ):
            return value.isoformat()

        if isinstance(
            value,
            dict,
        ):
            return {
                str(key): PlantHealthService._json_safe(
                    item_value
                )
                for key, item_value in value.items()
            }

        if isinstance(
            value,
            (
                list,
                tuple,
                set,
            ),
        ):
            return [
                PlantHealthService._json_safe(
                    item
                )
                for item in value
            ]

        if hasattr(
            value,
            "value",
        ):
            return value.value

        return value

    @staticmethod
    def _severity_from_text(
        severity: str | None,
        confidence_score: float,
    ) -> PlantDiseaseSeverity:
        severity_text = (
            severity
            or ""
        ).upper()

        if severity_text == "NONE":
            return PlantDiseaseSeverity.HEALTHY

        if severity_text == "HEALTHY":
            return PlantDiseaseSeverity.HEALTHY

        if severity_text == "LOW":
            return PlantDiseaseSeverity.LOW

        if severity_text == "MODERATE":
            return PlantDiseaseSeverity.MODERATE

        if severity_text == "HIGH":
            return PlantDiseaseSeverity.HIGH

        if confidence_score < 0.50:
            return PlantDiseaseSeverity.MODERATE

        return PlantDiseaseSeverity.MODERATE

    @staticmethod
    def _status_from_confidence(
        confidence_score: float,
        disease_name: str,
    ) -> PlantDiagnosisStatus:
        if confidence_score < 0.50:
            return PlantDiagnosisStatus.MANUAL_REVIEW

        if disease_name.lower() == "healthy":
            return PlantDiagnosisStatus.COMPLETED

        return PlantDiagnosisStatus.COMPLETED

    @staticmethod
    def _recommendation_type_from_section(
        section_name: str,
    ) -> PlantRecommendationType:
        if section_name == "organic_treatment":
            return PlantRecommendationType.CURE

        if section_name == "chemical_treatment":
            return PlantRecommendationType.CURE

        if section_name == "prevention":
            return PlantRecommendationType.PREVENTION

        return PlantRecommendationType.CARE

    @staticmethod
    def _build_recommendation_payloads_from_treatment(
        treatment: dict,
    ) -> list[dict]:
        common_safety_note = (
            "This is an AI-assisted plant health suggestion, not a final "
            "professional agricultural diagnosis. For severe disease spread "
            "or crop loss, consult a local agriculture expert."
        )

        payloads = []
        priority_order = 1

        section_config = [
            (
                "organic_treatment",
                "Organic / safe care steps",
            ),
            (
                "chemical_treatment",
                "Chemical treatment guidance",
            ),
            (
                "prevention",
                "Prevention tips",
            ),
        ]

        for section_name, title in section_config:
            items = treatment.get(
                section_name,
                [],
            )

            if not items:
                continue

            description = " ".join(
                f"{index + 1}. {item}"
                for index, item in enumerate(items)
            )

            payloads.append(
                {
                    "recommendation_type": PlantHealthService._recommendation_type_from_section(
                        section_name
                    ),
                    "title": title,
                    "description": description,
                    "priority_order": priority_order,
                    "safety_note": common_safety_note,
                }
            )

            priority_order += 1

        if not payloads:
            payloads.append(
                {
                    "recommendation_type": PlantRecommendationType.FOLLOW_UP,
                    "title": "Upload clearer image",
                    "description": (
                        "Upload a clear close-up image of the affected leaf "
                        "in natural light for better diagnosis."
                    ),
                    "priority_order": 1,
                    "safety_note": common_safety_note,
                }
            )

        return payloads

    @staticmethod
    def _create_recommendations(
        db: Session,
        diagnosis_id: str,
        recommendation_payloads: list[dict],
    ) -> None:
        for payload in recommendation_payloads:
            recommendation = PlantCareRecommendation(
                diagnosis_id=diagnosis_id,
                recommendation_type=payload["recommendation_type"],
                title=payload["title"],
                description=payload["description"],
                priority_order=payload["priority_order"],
                safety_note=payload["safety_note"],
            )

            db.add(recommendation)

    @staticmethod
    def _diagnose_with_pretrained_model(
        db: Session,
        submission_id: str,
        user_id: str,
        media: SubmissionMedia,
        plant_name: str | None = None,
        user_question: str | None = None,
    ) -> dict:
        prediction = PlantDiseaseAIService.predict_from_image_path(
            image_path=media.file_path,
            user_question=user_question,
        )

        treatment = prediction.get(
            "treatment",
            {},
        )

        disease_name = prediction.get(
            "disease_name",
            "Possible plant disease",
        )

        crop_name = prediction.get(
            "crop_name",
        )

        confidence_score = float(
            prediction.get(
                "confidence_score",
                0.0,
            )
        )

        confidence_level = prediction.get(
            "confidence_level",
            "LOW",
        )

        severity = PlantHealthService._severity_from_text(
            severity=treatment.get(
                "severity",
            ),
            confidence_score=confidence_score,
        )

        status = PlantHealthService._status_from_confidence(
            confidence_score=confidence_score,
            disease_name=disease_name,
        )

        display_plant_name = (
            plant_name
            or crop_name
        )

        if crop_name and disease_name.lower() != "healthy":
            display_disease_name = f"{crop_name} - {disease_name}"
        else:
            display_disease_name = disease_name

        guide_answer = prediction.get(
            "guide_answer",
            "",
        )

        cure_summary = treatment.get(
            "description",
            guide_answer,
        )

        prevention_items = treatment.get(
            "prevention",
            [],
        )

        prevention_tips = " ".join(
            f"{index + 1}. {item}"
            for index, item in enumerate(prevention_items)
        )

        if not prevention_tips:
            prevention_tips = prediction.get(
                "warning",
                "",
            )

        symptoms_payload = PlantHealthService._json_safe(
            {
                "predicted_class": prediction.get(
                    "predicted_class",
                ),
                "crop_name": crop_name,
                "disease_name": disease_name,
                "confidence_level": confidence_level,
                "top_predictions": prediction.get(
                    "top_predictions",
                    [],
                ),
                "image_width": prediction.get(
                    "image_width",
                ),
                "image_height": prediction.get(
                    "image_height",
                ),
                "warning": prediction.get(
                    "warning",
                ),
                "query_answered": prediction.get(
                    "query_answered",
                    False,
                ),
                "user_question": user_question,
            }
        )

        raw_result_payload = PlantHealthService._json_safe(
            {
                "engine": "pretrained_mobilenetv2_plant_disease",
                "paid_api_used": False,
                "model_source": prediction.get(
                    "model_source",
                ),
                "model_name": prediction.get(
                    "model_name",
                ),
                "confidence_level": confidence_level,
                "guide_answer": guide_answer,
                "treatment": treatment,
                "full_prediction": prediction,
                "note": (
                    "This is an AI-based plant health suggestion. "
                    "Low-confidence predictions should be manually reviewed."
                ),
            }
        )

        diagnosis = PlantDiagnosis(
            user_id=user_id,
            submission_id=submission_id,
            media_id=media.id,
            plant_name=display_plant_name,
            disease_name=display_disease_name,
            severity=severity,
            status=status,
            confidence_score=confidence_score,
            model_name=PlantHealthService.MODEL_NAME,
            symptoms_json=symptoms_payload,
            cure_summary=cure_summary,
            prevention_tips=prevention_tips,
            raw_result_json=raw_result_payload,
        )

        db.add(diagnosis)
        db.flush()

        recommendation_payloads = (
            PlantHealthService._build_recommendation_payloads_from_treatment(
                treatment=treatment,
            )
        )

        if guide_answer:
            recommendation_payloads.insert(
                0,
                {
                    "recommendation_type": PlantRecommendationType.CARE,
                    "title": "Plant guide answer",
                    "description": guide_answer,
                    "priority_order": 0,
                    "safety_note": prediction.get(
                        "warning",
                        (
                            "This is AI-assisted guidance. For severe disease "
                            "spread, consult a local agriculture expert."
                        ),
                    ),
                },
            )

        PlantHealthService._create_recommendations(
            db=db,
            diagnosis_id=diagnosis.id,
            recommendation_payloads=recommendation_payloads,
        )

        db.commit()
        db.refresh(diagnosis)

        return PlantHealthService.get_diagnosis_detail(
            db=db,
            diagnosis_id=diagnosis.id,
        )

    @staticmethod
    def _analyze_image_colors(
        file_path: str,
    ) -> dict:
        if Image is None:
            raise RuntimeError(
                "Pillow is not installed. Install it using: pip install Pillow"
            )

        path = Path(
            file_path
        )

        if not path.exists():
            raise FileNotFoundError(
                "Plant image file not found in storage"
            )

        with Image.open(path) as image:
            image = image.convert(
                "RGB"
            )
            image = image.resize(
                (256, 256)
            )

            pixels = list(
                image.getdata()
            )
            total_pixels = len(
                pixels
            )

            green_pixels = 0
            yellow_pixels = 0
            brown_pixels = 0
            dark_spot_pixels = 0
            pale_pixels = 0

            brightness_sum = 0

            for red, green, blue in pixels:
                brightness = (
                    red
                    + green
                    + blue
                ) / 3

                brightness_sum += brightness

                is_green = (
                    green > red * 1.10
                    and green > blue * 1.10
                    and green > 70
                )

                is_yellow = (
                    red > 130
                    and green > 120
                    and blue < 120
                    and abs(red - green) < 80
                )

                is_brown = (
                    red > 70
                    and green > 35
                    and blue < 100
                    and red > green
                    and green >= blue
                )

                is_dark_spot = (
                    red < 75
                    and green < 75
                    and blue < 75
                )

                is_pale = (
                    red > 170
                    and green > 170
                    and blue > 130
                )

                if is_green:
                    green_pixels += 1

                if is_yellow:
                    yellow_pixels += 1

                if is_brown:
                    brown_pixels += 1

                if is_dark_spot:
                    dark_spot_pixels += 1

                if is_pale:
                    pale_pixels += 1

            return {
                "green_ratio": round(
                    green_pixels / total_pixels,
                    4,
                ),
                "yellow_ratio": round(
                    yellow_pixels / total_pixels,
                    4,
                ),
                "brown_ratio": round(
                    brown_pixels / total_pixels,
                    4,
                ),
                "dark_spot_ratio": round(
                    dark_spot_pixels / total_pixels,
                    4,
                ),
                "pale_ratio": round(
                    pale_pixels / total_pixels,
                    4,
                ),
                "average_brightness": round(
                    brightness_sum / total_pixels,
                    2,
                ),
                "analyzed_resolution": "256x256",
            }

    @staticmethod
    def _severity_from_score(
        score: float,
    ) -> PlantDiseaseSeverity:
        if score >= 0.55:
            return PlantDiseaseSeverity.HIGH

        if score >= 0.30:
            return PlantDiseaseSeverity.MODERATE

        if score >= 0.15:
            return PlantDiseaseSeverity.LOW

        return PlantDiseaseSeverity.HEALTHY

    @staticmethod
    def _confidence_from_score(
        score: float,
    ) -> float:
        confidence = 0.55 + min(
            score,
            0.45,
        )

        return round(
            min(
                confidence,
                0.92,
            ),
            2,
        )

    @staticmethod
    def _predict_condition_fallback(
        metrics: dict,
    ) -> dict:
        green_ratio = metrics["green_ratio"]
        yellow_ratio = metrics["yellow_ratio"]
        brown_ratio = metrics["brown_ratio"]
        dark_spot_ratio = metrics["dark_spot_ratio"]
        pale_ratio = metrics["pale_ratio"]

        disease_score = (
            yellow_ratio * 0.8
            + brown_ratio * 1.1
            + dark_spot_ratio * 1.4
            + pale_ratio * 0.4
        )

        if green_ratio < 0.05:
            return {
                "disease_name": "Plant/leaf not clearly visible",
                "severity": PlantDiseaseSeverity.MODERATE,
                "confidence_score": 0.45,
                "status": PlantDiagnosisStatus.MANUAL_REVIEW,
                "main_reason": "Low visible green leaf area detected",
            }

        if dark_spot_ratio >= 0.12 or brown_ratio >= 0.22:
            severity = PlantHealthService._severity_from_score(
                disease_score
            )

            return {
                "disease_name": "Possible Leaf Blight or Fungal Leaf Spot",
                "severity": severity,
                "confidence_score": PlantHealthService._confidence_from_score(
                    disease_score
                ),
                "status": PlantDiagnosisStatus.COMPLETED,
                "main_reason": "Brown/dark patch patterns detected",
            }

        if yellow_ratio >= 0.22:
            severity = PlantHealthService._severity_from_score(
                disease_score
            )

            return {
                "disease_name": "Possible Leaf Yellowing or Nutrient Stress",
                "severity": severity,
                "confidence_score": PlantHealthService._confidence_from_score(
                    disease_score
                ),
                "status": PlantDiagnosisStatus.COMPLETED,
                "main_reason": "Yellowing pattern detected",
            }

        if pale_ratio >= 0.35:
            return {
                "disease_name": "Possible Sun Stress or Chlorosis",
                "severity": PlantDiseaseSeverity.LOW,
                "confidence_score": 0.62,
                "status": PlantDiagnosisStatus.COMPLETED,
                "main_reason": "Pale leaf color pattern detected",
            }

        return {
            "disease_name": "Healthy Plant / No Visible Disease",
            "severity": PlantDiseaseSeverity.HEALTHY,
            "confidence_score": 0.78,
            "status": PlantDiagnosisStatus.COMPLETED,
            "main_reason": "Healthy green leaf pattern detected",
        }

    @staticmethod
    def _summary_from_disease_fallback(
        disease_name: str,
    ) -> tuple[str, str]:
        if disease_name == "Healthy Plant / No Visible Disease":
            return (
                "The plant appears healthy based on the uploaded image.",
                "Continue regular care, avoid overwatering, and monitor leaves weekly.",
            )

        if "Yellowing" in disease_name:
            return (
                "The plant may be experiencing yellowing or nutrient stress.",
                "Use compost, avoid overwatering, and check whether new leaves improve.",
            )

        if "Blight" in disease_name or "Fungal" in disease_name:
            return (
                "The image shows possible fungal or blight-like symptoms.",
                "Remove infected leaves, avoid wetting leaves, and improve airflow.",
            )

        if "Sun Stress" in disease_name:
            return (
                "The plant may be under sunlight or chlorosis-related stress.",
                "Provide partial shade, balanced watering, and observe leaf color changes.",
            )

        return (
            "The image needs manual review for reliable plant health diagnosis.",
            "Upload a clearer close-up image of the affected leaf or plant part.",
        )

    @staticmethod
    def _build_fallback_recommendation_payloads(
        disease_name: str,
    ) -> list[dict]:
        common_safety_note = (
            "This is an AI-assisted suggestion, not a professional agricultural "
            "diagnosis. For severe disease spread, consult a local agriculture expert."
        )

        if disease_name == "Healthy Plant / No Visible Disease":
            return [
                {
                    "recommendation_type": PlantRecommendationType.CARE,
                    "title": "Continue regular care",
                    "description": (
                        "Maintain balanced watering, sunlight, and soil drainage. "
                        "Keep observing leaves for early color changes or spots."
                    ),
                    "priority_order": 1,
                    "safety_note": common_safety_note,
                },
                {
                    "recommendation_type": PlantRecommendationType.PREVENTION,
                    "title": "Prevent future infection",
                    "description": (
                        "Avoid water stagnation near roots and remove dead leaves "
                        "around the plant to reduce fungal growth."
                    ),
                    "priority_order": 2,
                    "safety_note": common_safety_note,
                },
            ]

        if "Yellowing" in disease_name or "Nutrient" in disease_name:
            return [
                {
                    "recommendation_type": PlantRecommendationType.CARE,
                    "title": "Check watering pattern",
                    "description": (
                        "Avoid overwatering. Let the top layer of soil dry slightly "
                        "before the next watering."
                    ),
                    "priority_order": 1,
                    "safety_note": common_safety_note,
                },
                {
                    "recommendation_type": PlantRecommendationType.CURE,
                    "title": "Improve soil nutrition",
                    "description": (
                        "Add compost or organic manure in small quantity. Yellowing "
                        "can happen due to nitrogen or iron deficiency."
                    ),
                    "priority_order": 2,
                    "safety_note": common_safety_note,
                },
                {
                    "recommendation_type": PlantRecommendationType.FOLLOW_UP,
                    "title": "Upload follow-up image",
                    "description": (
                        "Upload another image after 5 to 7 days to compare whether "
                        "yellowing is reducing."
                    ),
                    "priority_order": 3,
                    "safety_note": common_safety_note,
                },
            ]

        if "Blight" in disease_name or "Fungal" in disease_name:
            return [
                {
                    "recommendation_type": PlantRecommendationType.CURE,
                    "title": "Remove infected leaves",
                    "description": (
                        "Carefully remove highly infected leaves and dispose of them "
                        "away from healthy plants."
                    ),
                    "priority_order": 1,
                    "safety_note": common_safety_note,
                },
                {
                    "recommendation_type": PlantRecommendationType.CURE,
                    "title": "Use neem-based spray",
                    "description": (
                        "Use a mild neem oil spray in the evening. Avoid spraying "
                        "during harsh sunlight."
                    ),
                    "priority_order": 2,
                    "safety_note": common_safety_note,
                },
                {
                    "recommendation_type": PlantRecommendationType.PREVENTION,
                    "title": "Avoid wet leaves",
                    "description": (
                        "Water near the soil instead of spraying water on leaves. "
                        "Improve air circulation around the plant."
                    ),
                    "priority_order": 3,
                    "safety_note": common_safety_note,
                },
            ]

        return [
            {
                "recommendation_type": PlantRecommendationType.FOLLOW_UP,
                "title": "Manual review recommended",
                "description": (
                    "Upload a clear close-up image of affected leaves in natural light."
                ),
                "priority_order": 1,
                "safety_note": common_safety_note,
            }
        ]

    @staticmethod
    def _diagnose_with_fallback_rules(
        db: Session,
        submission_id: str,
        user_id: str,
        media: SubmissionMedia,
        plant_name: str | None = None,
        error_message: str | None = None,
    ) -> dict:
        metrics = PlantHealthService._analyze_image_colors(
            file_path=media.file_path
        )

        prediction = PlantHealthService._predict_condition_fallback(
            metrics
        )

        cure_summary, prevention_tips = (
            PlantHealthService._summary_from_disease_fallback(
                disease_name=prediction["disease_name"],
            )
        )

        diagnosis = PlantDiagnosis(
            user_id=user_id,
            submission_id=submission_id,
            media_id=media.id,
            plant_name=plant_name,
            disease_name=prediction["disease_name"],
            severity=prediction["severity"],
            status=prediction["status"],
            confidence_score=prediction["confidence_score"],
            model_name=PlantHealthService.FALLBACK_MODEL_NAME,
            symptoms_json=PlantHealthService._json_safe(
                {
                    "main_reason": prediction["main_reason"],
                    "color_metrics": metrics,
                    "fallback_used": True,
                }
            ),
            cure_summary=cure_summary,
            prevention_tips=prevention_tips,
            raw_result_json=PlantHealthService._json_safe(
                {
                    "engine": "free_local_plant_rules_fallback",
                    "paid_api_used": False,
                    "fallback_reason": error_message,
                    "note": (
                        "Pretrained plant model could not be used, so local "
                        "color-heuristic fallback diagnosis was applied."
                    ),
                }
            ),
        )

        db.add(diagnosis)
        db.flush()

        recommendation_payloads = (
            PlantHealthService._build_fallback_recommendation_payloads(
                disease_name=diagnosis.disease_name,
            )
        )

        PlantHealthService._create_recommendations(
            db=db,
            diagnosis_id=diagnosis.id,
            recommendation_payloads=recommendation_payloads,
        )

        db.commit()
        db.refresh(diagnosis)

        return PlantHealthService.get_diagnosis_detail(
            db=db,
            diagnosis_id=diagnosis.id,
        )

    @staticmethod
    def diagnose_submission(
        db: Session,
        submission_id: str,
        user_id: str,
        plant_name: str | None = None,
        user_question: str | None = None,
    ) -> dict:
        submission = (
            db.query(Submission)
            .filter(Submission.id == submission_id)
            .first()
        )

        if not submission:
            raise ValueError(
                "Submission not found"
            )

        media = PlantHealthService._get_latest_image_media(
            db=db,
            submission_id=submission_id,
        )

        if not media:
            raise ValueError(
                "No image media found for this submission"
            )

        try:
            return PlantHealthService._diagnose_with_pretrained_model(
                db=db,
                submission_id=submission_id,
                user_id=user_id,
                media=media,
                plant_name=plant_name,
                user_question=user_question,
            )

        except Exception as exc:
            db.rollback()

            try:
                return PlantHealthService._diagnose_with_fallback_rules(
                    db=db,
                    submission_id=submission_id,
                    user_id=user_id,
                    media=media,
                    plant_name=plant_name,
                    error_message=str(exc),
                )

            except Exception as fallback_exc:
                db.rollback()

                diagnosis = PlantDiagnosis(
                    user_id=user_id,
                    submission_id=submission_id,
                    media_id=media.id,
                    plant_name=plant_name,
                    disease_name="Diagnosis failed",
                    severity=PlantDiseaseSeverity.MODERATE,
                    status=PlantDiagnosisStatus.FAILED,
                    confidence_score=0.0,
                    model_name=PlantHealthService.MODEL_NAME,
                    symptoms_json={},
                    cure_summary=None,
                    prevention_tips=None,
                    raw_result_json=PlantHealthService._json_safe(
                        {
                            "engine": "pretrained_mobilenetv2_plant_disease",
                            "paid_api_used": False,
                            "fallback_attempted": True,
                            "primary_error": str(exc),
                            "fallback_error": str(fallback_exc),
                        }
                    ),
                    error_message=str(fallback_exc),
                )

                db.add(diagnosis)
                db.commit()
                db.refresh(diagnosis)

                return PlantHealthService.get_diagnosis_detail(
                    db=db,
                    diagnosis_id=diagnosis.id,
                )

    @staticmethod
    def get_diagnosis_detail(
        db: Session,
        diagnosis_id: str,
    ) -> dict | None:
        diagnosis = (
            db.query(PlantDiagnosis)
            .filter(PlantDiagnosis.id == diagnosis_id)
            .first()
        )

        if not diagnosis:
            return None

        recommendations = (
            db.query(PlantCareRecommendation)
            .filter(PlantCareRecommendation.diagnosis_id == diagnosis_id)
            .order_by(PlantCareRecommendation.priority_order.asc())
            .all()
        )

        return {
            "id": diagnosis.id,
            "user_id": diagnosis.user_id,
            "submission_id": diagnosis.submission_id,
            "media_id": diagnosis.media_id,
            "plant_name": diagnosis.plant_name,
            "disease_name": diagnosis.disease_name,
            "severity": diagnosis.severity,
            "status": diagnosis.status,
            "confidence_score": diagnosis.confidence_score,
            "model_name": diagnosis.model_name,
            "symptoms_json": diagnosis.symptoms_json,
            "cure_summary": diagnosis.cure_summary,
            "prevention_tips": diagnosis.prevention_tips,
            "raw_result_json": diagnosis.raw_result_json,
            "error_message": diagnosis.error_message,
            "created_at": diagnosis.created_at,
            "recommendations": recommendations,
        }

    @staticmethod
    def get_my_diagnoses(
        db: Session,
        user_id: str,
    ) -> list[PlantDiagnosis]:
        return (
            db.query(PlantDiagnosis)
            .filter(PlantDiagnosis.user_id == user_id)
            .order_by(PlantDiagnosis.created_at.desc())
            .all()
        )

    @staticmethod
    def get_manual_review_diagnoses(
        db: Session,
    ) -> list[dict]:
        diagnoses = (
            db.query(PlantDiagnosis)
            .filter(
                PlantDiagnosis.status == PlantDiagnosisStatus.MANUAL_REVIEW
            )
            .order_by(PlantDiagnosis.created_at.desc())
            .all()
        )

        return [
            PlantHealthService.get_diagnosis_detail(
                db=db,
                diagnosis_id=diagnosis.id,
            )
            for diagnosis in diagnoses
        ]