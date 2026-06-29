from datetime import datetime
from datetime import timezone
from pathlib import Path
from typing import Any

from sqlalchemy.orm import Session

from app.core.enums import AIVerificationDecision
from app.core.enums import AIVerificationStatus
from app.core.enums import FraudCheckResult
from app.core.enums import FraudCheckType
from app.core.enums import MediaType
from app.core.enums import SubmissionStatus
from app.models.ai_verification import AIVerification
from app.models.fraud_check import FraudCheck
from app.models.submission import Submission
from app.models.submission_media import SubmissionMedia
from app.services.ai.local_vision_service import LocalVisionService

try:
    from PIL import Image
    from PIL import ImageStat
except ImportError:
    Image = None
    ImageStat = None


class AIVerificationService:
    """
    Free/local AI verification engine.

    This service uses:
    1. Local fraud rule checks
    2. Duplicate image detection
    3. Screenshot detection
    4. Image quality analysis
    5. GPS validation
    6. OpenCV-based local vision relevance analysis

    No paid API is used.
    """

    LOCAL_MODEL_NAME = "local_fraud_rules_plus_opencv_v2"

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
    def _submission_status(
        status_name: str,
        fallback: SubmissionStatus,
    ) -> SubmissionStatus:
        return getattr(
            SubmissionStatus,
            status_name,
            fallback,
        )

    @staticmethod
    def _verification_decision(
        decision_name: str,
        fallback: AIVerificationDecision,
    ) -> AIVerificationDecision:
        return getattr(
            AIVerificationDecision,
            decision_name,
            fallback,
        )

    @staticmethod
    def _create_check(
        db: Session,
        verification_id: str,
        check_type: FraudCheckType,
        result: FraudCheckResult,
        risk_score: float,
        message: str,
        details_json: dict | None = None,
    ) -> FraudCheck:
        check = FraudCheck(
            verification_id=verification_id,
            check_type=check_type,
            result=result,
            risk_score=max(
                0.0,
                min(
                    1.0,
                    risk_score,
                ),
            ),
            message=message,
            details_json=details_json or {},
        )

        db.add(check)
        db.flush()

        return check

    @staticmethod
    def _serialize_verification(
        verification: AIVerification,
        checks: list[FraudCheck],
    ) -> dict:
        return {
            "id": verification.id,
            "submission_id": verification.submission_id,
            "media_id": verification.media_id,
            "status": verification.status,
            "decision": verification.decision,
            "confidence_score": verification.confidence_score,
            "fraud_risk_score": verification.fraud_risk_score,
            "model_name": verification.model_name,
            "summary": verification.summary,
            "result_json": verification.result_json,
            "error_message": verification.error_message,
            "created_at": verification.created_at,
            "completed_at": verification.completed_at,
            "fraud_checks": checks,
        }

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
    def _quality_metrics(
        media: SubmissionMedia,
    ) -> dict:
        metrics = {
            "width": media.image_width,
            "height": media.image_height,
            "brightness": None,
            "contrast": None,
            "can_open_image": False,
        }

        if Image is None or ImageStat is None:
            return metrics

        path = Path(media.file_path)

        if not path.exists():
            return metrics

        try:
            with Image.open(path) as image:
                metrics["can_open_image"] = True

                grayscale = image.convert("L")
                stat = ImageStat.Stat(grayscale)

                metrics["brightness"] = round(
                    float(stat.mean[0]),
                    2,
                )

                metrics["contrast"] = round(
                    float(stat.stddev[0]),
                    2,
                )

                if not metrics["width"] or not metrics["height"]:
                    metrics["width"], metrics["height"] = image.size

        except Exception:
            metrics["can_open_image"] = False

        return metrics

    @staticmethod
    def _is_screenshot_like(
        media: SubmissionMedia,
    ) -> tuple[bool, float, dict]:
        filename = (
            media.original_filename
            or ""
        ).lower()

        screenshot_keywords = [
            "screenshot",
            "screen shot",
            "screen_capture",
            "screen-capture",
            "whatsapp image",
        ]

        keyword_hit = any(
            keyword in filename
            for keyword in screenshot_keywords
        )

        width = media.image_width or 0
        height = media.image_height or 0

        common_screen_resolutions = {
            (720, 1280),
            (1080, 1920),
            (1170, 2532),
            (1242, 2688),
            (1440, 2560),
            (750, 1334),
            (828, 1792),
            (1125, 2436),
            (1080, 2400),
            (1440, 3200),
            (1920, 1080),
            (1366, 768),
        }

        resolution_hit = (
            (width, height) in common_screen_resolutions
            or (height, width) in common_screen_resolutions
        )

        risk = 0.0

        if keyword_hit:
            risk += 0.7

        if resolution_hit:
            risk += 0.25

        return risk >= 0.7, min(risk, 1.0), {
            "filename_keyword_match": keyword_hit,
            "common_screen_resolution_match": resolution_hit,
            "width": width,
            "height": height,
        }

    @staticmethod
    def _calculate_confidence(
        checks: list[FraudCheck],
    ) -> float:
        if not checks:
            return 0.0

        pass_count = sum(
            1
            for check in checks
            if check.result == FraudCheckResult.PASS
        )

        warning_count = sum(
            1
            for check in checks
            if check.result == FraudCheckResult.WARNING
        )

        fail_count = sum(
            1
            for check in checks
            if check.result == FraudCheckResult.FAIL
        )

        confidence = (
            0.25
            + (pass_count * 0.15)
            - (warning_count * 0.08)
            - (fail_count * 0.2)
        )

        return round(
            max(
                0.0,
                min(
                    0.95,
                    confidence,
                ),
            ),
            2,
        )

    @staticmethod
    def _local_vision_result(
        local_vision_decision: str,
    ) -> FraudCheckResult:
        if local_vision_decision == "PASS":
            return FraudCheckResult.PASS

        if local_vision_decision == "FAIL":
            return FraudCheckResult.FAIL

        return FraudCheckResult.WARNING

    @staticmethod
    def _local_vision_risk(
        local_vision_decision: str,
        relevance_score: float,
        quality_score: float,
    ) -> float:
        if local_vision_decision == "PASS":
            return 0.0

        if local_vision_decision == "NEEDS_REVIEW":
            return 0.35

        if local_vision_decision == "FAIL":
            return 0.6

        if quality_score < 0.3:
            return 0.55

        if relevance_score < 0.35:
            return 0.5

        return 0.4

    @staticmethod
    def _run_local_vision_check(
        media: SubmissionMedia,
        submission: Submission,
    ) -> dict:
        return LocalVisionService.analyze_image(
            media=media,
            submission_type=submission.submission_type,
        )

    @staticmethod
    def run_submission_verification(
        db: Session,
        submission_id: str,
    ) -> dict:
        submission = (
            db.query(Submission)
            .filter(Submission.id == submission_id)
            .first()
        )

        if not submission:
            raise ValueError("Submission not found")

        media = AIVerificationService._get_latest_image_media(
            db=db,
            submission_id=submission_id,
        )

        verification = AIVerification(
            submission_id=submission_id,
            media_id=media.id if media else None,
            status=AIVerificationStatus.RUNNING,
            model_name=AIVerificationService.LOCAL_MODEL_NAME,
        )

        db.add(verification)
        db.flush()

        submission.status = SubmissionStatus.AI_REVIEWING

        checks: list[FraudCheck] = []

        local_vision_analysis = None
        local_vision_decision = "NOT_RUN"

        try:
            if not media:
                checks.append(
                    AIVerificationService._create_check(
                        db=db,
                        verification_id=verification.id,
                        check_type=FraudCheckType.FILE_INTEGRITY,
                        result=FraudCheckResult.FAIL,
                        risk_score=0.75,
                        message="No image proof found for this submission.",
                    )
                )

                verification.decision = AIVerificationDecision.MANUAL_REVIEW
                verification.fraud_risk_score = 0.75
                verification.confidence_score = 0.1
                verification.summary = (
                    "Image proof is missing. Manual review is required."
                )

                submission.status = SubmissionStatus.MANUAL_REVIEW

            else:
                file_path = Path(media.file_path)
                file_exists = file_path.exists()

                checks.append(
                    AIVerificationService._create_check(
                        db=db,
                        verification_id=verification.id,
                        check_type=FraudCheckType.FILE_INTEGRITY,
                        result=(
                            FraudCheckResult.PASS
                            if file_exists
                            else FraudCheckResult.FAIL
                        ),
                        risk_score=0.0 if file_exists else 0.9,
                        message=(
                            "Uploaded proof file is readable."
                            if file_exists
                            else "Uploaded proof file is missing from storage."
                        ),
                        details_json={
                            "file_path": media.file_path,
                            "file_sha256": media.file_sha256,
                            "mime_type": media.mime_type,
                        },
                    )
                )

                duplicate_count = 0

                if media.file_sha256:
                    duplicate_count = (
                        db.query(SubmissionMedia)
                        .filter(
                            SubmissionMedia.file_sha256 == media.file_sha256
                        )
                        .filter(SubmissionMedia.id != media.id)
                        .count()
                    )

                duplicate_result = (
                    FraudCheckResult.FAIL
                    if duplicate_count > 0
                    else FraudCheckResult.PASS
                )

                checks.append(
                    AIVerificationService._create_check(
                        db=db,
                        verification_id=verification.id,
                        check_type=FraudCheckType.DUPLICATE_IMAGE,
                        result=duplicate_result,
                        risk_score=0.85 if duplicate_count > 0 else 0.0,
                        message=(
                            "Exact duplicate image detected."
                            if duplicate_count > 0
                            else "No exact duplicate image found."
                        ),
                        details_json={
                            "duplicate_count": duplicate_count,
                            "file_sha256": media.file_sha256,
                        },
                    )
                )

                (
                    is_screenshot,
                    screenshot_risk,
                    screenshot_details,
                ) = AIVerificationService._is_screenshot_like(
                    media
                )

                checks.append(
                    AIVerificationService._create_check(
                        db=db,
                        verification_id=verification.id,
                        check_type=FraudCheckType.SCREENSHOT_DETECTION,
                        result=(
                            FraudCheckResult.WARNING
                            if is_screenshot
                            else FraudCheckResult.PASS
                        ),
                        risk_score=screenshot_risk,
                        message=(
                            "Screenshot-like image detected."
                            if is_screenshot
                            else "No strong screenshot indicators found."
                        ),
                        details_json=screenshot_details,
                    )
                )

                quality = AIVerificationService._quality_metrics(
                    media
                )

                width = quality.get("width") or 0
                height = quality.get("height") or 0
                contrast = quality.get("contrast")
                can_open_image = bool(
                    quality.get("can_open_image")
                )

                quality_failed = (
                    not can_open_image
                    or width < 320
                    or height < 320
                )

                quality_warning = (
                    not quality_failed
                    and (
                        width < 640
                        or height < 640
                        or (
                            contrast is not None
                            and contrast < 18
                        )
                    )
                )

                if quality_failed:
                    quality_result = FraudCheckResult.FAIL
                    quality_risk = 0.65
                    quality_message = (
                        "Image is unreadable or too small for reliable verification."
                    )

                elif quality_warning:
                    quality_result = FraudCheckResult.WARNING
                    quality_risk = 0.35
                    quality_message = (
                        "Image quality is acceptable but not ideal."
                    )

                else:
                    quality_result = FraudCheckResult.PASS
                    quality_risk = 0.0
                    quality_message = (
                        "Image quality is acceptable for AI verification."
                    )

                checks.append(
                    AIVerificationService._create_check(
                        db=db,
                        verification_id=verification.id,
                        check_type=FraudCheckType.IMAGE_QUALITY,
                        result=quality_result,
                        risk_score=quality_risk,
                        message=quality_message,
                        details_json=quality,
                    )
                )

                has_location = (
                    submission.latitude is not None
                    and submission.longitude is not None
                )

                checks.append(
                    AIVerificationService._create_check(
                        db=db,
                        verification_id=verification.id,
                        check_type=FraudCheckType.GPS_VALIDATION,
                        result=(
                            FraudCheckResult.PASS
                            if has_location
                            else FraudCheckResult.WARNING
                        ),
                        risk_score=0.0 if has_location else 0.3,
                        message=(
                            "Submission contains GPS coordinates."
                            if has_location
                            else "Submission has no GPS coordinates."
                        ),
                        details_json={
                            "latitude": submission.latitude,
                            "longitude": submission.longitude,
                            "location_name": submission.location_name,
                        },
                    )
                )

                if file_exists and duplicate_count == 0:
                    try:
                        local_vision_analysis = (
                            AIVerificationService._run_local_vision_check(
                                media=media,
                                submission=submission,
                            )
                        )

                        local_vision_decision = str(
                            local_vision_analysis.get(
                                "decision",
                                "NEEDS_REVIEW",
                            )
                        )

                        relevance_score = float(
                            local_vision_analysis.get(
                                "relevance_score",
                                0.0,
                            )
                        )

                        quality_score = float(
                            local_vision_analysis.get(
                                "quality_score",
                                0.0,
                            )
                        )

                        local_vision_result = (
                            AIVerificationService._local_vision_result(
                                local_vision_decision
                            )
                        )

                        local_vision_risk = (
                            AIVerificationService._local_vision_risk(
                                local_vision_decision=local_vision_decision,
                                relevance_score=relevance_score,
                                quality_score=quality_score,
                            )
                        )

                        checks.append(
                            AIVerificationService._create_check(
                                db=db,
                                verification_id=verification.id,
                                check_type=FraudCheckType.CONTENT_RELEVANCE,
                                result=local_vision_result,
                                risk_score=local_vision_risk,
                                message=(
                                    "Local OpenCV vision check passed."
                                    if local_vision_decision == "PASS"
                                    else (
                                        "Local OpenCV vision check needs manual review."
                                        if local_vision_decision == "NEEDS_REVIEW"
                                        else "Local OpenCV vision check did not strongly match the claimed eco-action."
                                    )
                                ),
                                details_json={
                                    "engine": "opencv_local_vision",
                                    "submission_type": AIVerificationService._enum_value(
                                        submission.submission_type
                                    ),
                                    "vision_decision": local_vision_decision,
                                    "relevance_score": relevance_score,
                                    "quality_score": quality_score,
                                    "confidence_score": local_vision_analysis.get(
                                        "confidence_score"
                                    ),
                                    "detected_labels": local_vision_analysis.get(
                                        "detected_labels",
                                        [],
                                    ),
                                    "explanation": local_vision_analysis.get(
                                        "explanation"
                                    ),
                                    "recommendations": local_vision_analysis.get(
                                        "recommendations",
                                        [],
                                    ),
                                    "width": local_vision_analysis.get(
                                        "width"
                                    ),
                                    "height": local_vision_analysis.get(
                                        "height"
                                    ),
                                    "green_ratio": local_vision_analysis.get(
                                        "green_ratio"
                                    ),
                                    "brown_ratio": local_vision_analysis.get(
                                        "brown_ratio"
                                    ),
                                    "blue_ratio": local_vision_analysis.get(
                                        "blue_ratio"
                                    ),
                                    "edge_density": local_vision_analysis.get(
                                        "edge_density"
                                    ),
                                },
                            )
                        )

                    except Exception as exc:
                        local_vision_decision = "ERROR"

                        checks.append(
                            AIVerificationService._create_check(
                                db=db,
                                verification_id=verification.id,
                                check_type=FraudCheckType.CONTENT_RELEVANCE,
                                result=FraudCheckResult.WARNING,
                                risk_score=0.4,
                                message=(
                                    "Local OpenCV vision check could not be completed. "
                                    "Manual review is required."
                                ),
                                details_json={
                                    "engine": "opencv_local_vision",
                                    "error": str(exc),
                                    "submission_type": AIVerificationService._enum_value(
                                        submission.submission_type
                                    ),
                                },
                            )
                        )

                else:
                    checks.append(
                        AIVerificationService._create_check(
                            db=db,
                            verification_id=verification.id,
                            check_type=FraudCheckType.CONTENT_RELEVANCE,
                            result=FraudCheckResult.NOT_APPLICABLE,
                            risk_score=0.0,
                            message=(
                                "Local vision check skipped because the file is missing "
                                "or duplicate proof was detected."
                            ),
                            details_json={
                                "engine": "opencv_local_vision",
                                "skipped": True,
                                "file_exists": file_exists,
                                "duplicate_count": duplicate_count,
                            },
                        )
                    )

                fraud_risk = round(
                    max(
                        check.risk_score
                        for check in checks
                    ),
                    2,
                )

                has_fail = any(
                    check.result == FraudCheckResult.FAIL
                    for check in checks
                )

                has_warning = any(
                    check.result == FraudCheckResult.WARNING
                    for check in checks
                )

                verification.fraud_risk_score = fraud_risk
                verification.confidence_score = (
                    AIVerificationService._calculate_confidence(
                        checks
                    )
                )

                if duplicate_count > 0 or not file_exists:
                    verification.decision = AIVerificationDecision.REJECTED
                    verification.summary = (
                        "Submission is rejected by local fraud checks. "
                        "Duplicate or missing proof was detected."
                    )

                    submission.status = (
                        AIVerificationService._submission_status(
                            "AI_REJECTED",
                            SubmissionStatus.MANUAL_REVIEW,
                        )
                    )

                elif (
                    has_fail
                    or fraud_risk >= 0.55
                    or local_vision_decision in {
                        "FAIL",
                        "ERROR",
                    }
                ):
                    verification.decision = (
                        AIVerificationDecision.MANUAL_REVIEW
                    )

                    verification.summary = (
                        "Submission needs manual review. Local fraud checks or "
                        "local vision relevance checks found possible risk."
                    )

                    submission.status = SubmissionStatus.MANUAL_REVIEW

                elif local_vision_decision == "PASS":
                    verification.decision = (
                        AIVerificationService._verification_decision(
                            "APPROVED",
                            AIVerificationDecision.MANUAL_REVIEW,
                        )
                    )

                    if verification.decision == AIVerificationDecision.MANUAL_REVIEW:
                        verification.summary = (
                            "Local fraud checks and OpenCV vision checks passed, "
                            "but this project configuration keeps final approval "
                            "under manual review."
                        )

                        submission.status = SubmissionStatus.MANUAL_REVIEW

                    else:
                        verification.summary = (
                            "Local fraud checks passed and OpenCV vision confirmed "
                            "that the proof appears relevant to the submitted eco-action."
                        )

                        submission.status = (
                            AIVerificationService._submission_status(
                                "AI_APPROVED",
                                SubmissionStatus.MANUAL_REVIEW,
                            )
                        )

                elif has_warning:
                    verification.decision = (
                        AIVerificationDecision.MANUAL_REVIEW
                    )

                    verification.summary = (
                        "Submission passed critical checks but has warnings. "
                        "Manual review is recommended before approval."
                    )

                    submission.status = SubmissionStatus.MANUAL_REVIEW

                else:
                    verification.decision = (
                        AIVerificationDecision.MANUAL_REVIEW
                    )

                    verification.summary = (
                        "Verification completed. Manual review is recommended "
                        "because the local vision decision was not strong enough "
                        "for automatic approval."
                    )

                    submission.status = SubmissionStatus.MANUAL_REVIEW

                metadata = media.metadata_json or {}
                metadata["verification_status"] = AIVerificationService._enum_value(
                    verification.decision
                )
                metadata["latest_verification_id"] = verification.id
                metadata["fraud_risk_score"] = verification.fraud_risk_score
                metadata["confidence_score"] = verification.confidence_score
                metadata["local_vision_decision"] = local_vision_decision

                if local_vision_analysis:
                    metadata["local_vision_relevance_score"] = (
                        local_vision_analysis.get("relevance_score")
                    )
                    metadata["local_vision_confidence_score"] = (
                        local_vision_analysis.get("confidence_score")
                    )
                    metadata["local_vision_labels"] = (
                        local_vision_analysis.get("detected_labels", [])
                    )

                media.metadata_json = metadata

            verification.status = AIVerificationStatus.COMPLETED
            verification.completed_at = datetime.now(timezone.utc)

            verification.result_json = {
                "engine": "free_local_rules_plus_opencv",
                "paid_api_used": False,
                "local_vision_enabled": True,
                "checks_count": len(checks),
                "local_vision_decision": local_vision_decision,
                "local_vision_analysis": local_vision_analysis,
                "final_submission_status": AIVerificationService._enum_value(
                    submission.status
                ),
                "final_ai_decision": AIVerificationService._enum_value(
                    verification.decision
                ),
                "note": (
                    "This verification uses free local fraud rules and "
                    "OpenCV-based local computer vision. No paid API is used."
                ),
            }

            db.commit()
            db.refresh(verification)

            return AIVerificationService.get_verification_detail(
                db=db,
                verification_id=verification.id,
            )

        except Exception as exc:
            verification.status = AIVerificationStatus.FAILED
            verification.decision = AIVerificationDecision.MANUAL_REVIEW
            verification.error_message = str(exc)
            verification.summary = (
                "AI verification failed due to an internal error. "
                "Manual review is required."
            )
            verification.completed_at = datetime.now(timezone.utc)

            submission.status = SubmissionStatus.MANUAL_REVIEW

            verification.result_json = {
                "engine": "free_local_rules_plus_opencv",
                "paid_api_used": False,
                "local_vision_enabled": True,
                "error": str(exc),
                "final_submission_status": AIVerificationService._enum_value(
                    submission.status
                ),
                "final_ai_decision": AIVerificationService._enum_value(
                    verification.decision
                ),
            }

            db.commit()
            db.refresh(verification)

            return AIVerificationService.get_verification_detail(
                db=db,
                verification_id=verification.id,
            )

    @staticmethod
    def get_verification_detail(
        db: Session,
        verification_id: str,
    ) -> dict | None:
        verification = (
            db.query(AIVerification)
            .filter(AIVerification.id == verification_id)
            .first()
        )

        if not verification:
            return None

        checks = (
            db.query(FraudCheck)
            .filter(FraudCheck.verification_id == verification_id)
            .order_by(FraudCheck.created_at.asc())
            .all()
        )

        return AIVerificationService._serialize_verification(
            verification=verification,
            checks=checks,
        )

    @staticmethod
    def get_latest_submission_verification(
        db: Session,
        submission_id: str,
    ) -> dict | None:
        verification = (
            db.query(AIVerification)
            .filter(AIVerification.submission_id == submission_id)
            .order_by(AIVerification.created_at.desc())
            .first()
        )

        if not verification:
            return None

        return AIVerificationService.get_verification_detail(
            db=db,
            verification_id=verification.id,
        )

    @staticmethod
    def get_manual_review_queue(
        db: Session,
    ) -> list[dict]:
        verifications = (
            db.query(AIVerification)
            .filter(
                AIVerification.decision
                == AIVerificationDecision.MANUAL_REVIEW
            )
            .order_by(AIVerification.created_at.desc())
            .all()
        )

        return [
            AIVerificationService.get_verification_detail(
                db=db,
                verification_id=verification.id,
            )
            for verification in verifications
        ]