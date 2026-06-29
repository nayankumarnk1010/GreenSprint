from datetime import datetime
from pathlib import Path
from typing import Any

import cv2
import numpy as np


class LocalVisionService:
    IMAGE_EXTENSIONS = {
        ".jpg",
        ".jpeg",
        ".png",
        ".webp",
        ".bmp",
    }

    @staticmethod
    def health() -> dict:
        try:
            version = cv2.__version__

            return {
                "status": "OK",
                "opencv_available": True,
                "message": "Local computer vision engine is available.",
                "details": {
                    "opencv_version": version,
                },
            }

        except Exception as exc:
            return {
                "status": "ERROR",
                "opencv_available": False,
                "message": "Local computer vision engine is not available.",
                "details": {
                    "error": str(exc),
                },
            }

    @staticmethod
    def is_image_media(
        media: Any,
    ) -> bool:
        mime_type = (
            getattr(media, "mime_type", None)
            or getattr(media, "content_type", None)
            or ""
        )

        if str(mime_type).lower().startswith("image/"):
            return True

        file_name = (
            getattr(media, "original_file_name", None)
            or getattr(media, "stored_file_name", None)
            or getattr(media, "file_name", None)
            or ""
        )

        return Path(str(file_name)).suffix.lower() in LocalVisionService.IMAGE_EXTENSIONS

    @staticmethod
    def resolve_media_path(
        media: Any,
    ) -> str:
        direct_fields = [
            "file_path",
            "storage_path",
            "local_path",
            "path",
        ]

        for field_name in direct_fields:
            value = getattr(
                media,
                field_name,
                None,
            )

            if value:
                path = Path(str(value))

                if path.exists():
                    return str(path)

        media_url = (
            getattr(media, "media_url", None)
            or getattr(media, "file_url", None)
            or getattr(media, "url", None)
        )

        if media_url:
            cleaned_url = str(media_url).lstrip("/")

            if cleaned_url.startswith("media/"):
                path = Path(cleaned_url)

                if path.exists():
                    return str(path)

            if cleaned_url.startswith("static/"):
                path = Path(cleaned_url)

                if path.exists():
                    return str(path)

        stored_file_name = (
            getattr(media, "stored_file_name", None)
            or getattr(media, "file_name", None)
        )

        if stored_file_name:
            matches = list(
                Path("media").glob(
                    f"**/{stored_file_name}"
                )
            )

            if matches:
                return str(matches[0])

        raise FileNotFoundError(
            "Media file was not found in local storage."
        )

    @staticmethod
    def _safe_ratio(
        mask: np.ndarray,
        total_pixels: int,
    ) -> float:
        if total_pixels <= 0:
            return 0.0

        return round(
            float(np.count_nonzero(mask)) / float(total_pixels),
            4,
        )

    @staticmethod
    def _normalize_submission_type(
        submission_type: Any,
    ) -> str:
        if not submission_type:
            return "UNKNOWN"

        value = getattr(
            submission_type,
            "value",
            submission_type,
        )

        value = str(value).upper().strip()

        if "." in value:
            value = value.split(".")[-1]

        return value

    @staticmethod
    def _quality_score(
        blur_score: float,
        brightness_score: float,
        contrast_score: float,
    ) -> float:
        blur_component = min(
            blur_score / 150.0,
            1.0,
        )

        brightness_component = 1.0

        if brightness_score < 45:
            brightness_component = brightness_score / 45.0

        elif brightness_score > 225:
            brightness_component = max(
                0.0,
                (255.0 - brightness_score) / 30.0,
            )

        contrast_component = min(
            contrast_score / 60.0,
            1.0,
        )

        score = (
            blur_component * 0.4
            + brightness_component * 0.35
            + contrast_component * 0.25
        )

        return round(
            max(
                0.0,
                min(score, 1.0),
            ),
            3,
        )

    @staticmethod
    def _detected_labels(
        green_ratio: float,
        brown_ratio: float,
        blue_ratio: float,
        white_ratio: float,
        gray_ratio: float,
        edge_density: float,
        blur_score: float,
        brightness_score: float,
    ) -> list[str]:
        labels = []

        if green_ratio >= 0.03:
            labels.append("vegetation_or_plant_area")

        if green_ratio >= 0.15:
            labels.append("strong_greenery_presence")

        if brown_ratio >= 0.04:
            labels.append("soil_or_natural_ground")

        if brown_ratio >= 0.25:
            labels.append("strong_soil_or_ground_presence")

        if blue_ratio >= 0.10:
            labels.append("water_or_sky_region")

        if edge_density >= 0.05:
            labels.append("object_rich_scene")

        if white_ratio >= 0.35:
            labels.append("large_light_background")

        if gray_ratio >= 0.30:
            labels.append("large_gray_area")

        if blur_score < 40:
            labels.append("possibly_blurry_image")

        if brightness_score < 45:
            labels.append("too_dark_image")

        if brightness_score > 225:
            labels.append("too_bright_image")

        if not labels:
            labels.append("general_image_content")

        return labels

    @staticmethod
    def _relevance_score(
        submission_type: str,
        green_ratio: float,
        brown_ratio: float,
        blue_ratio: float,
        edge_density: float,
        quality_score: float,
        contrast_score: float,
    ) -> float:
        contrast_component = min(
            contrast_score / 70.0,
            1.0,
        )

        if submission_type in {
            "TREE_PLANTATION",
            "PLANT_HEALTH_CHECK",
        }:
            green_component = min(
                green_ratio * 3.0,
                1.0,
            )

            soil_component = min(
                brown_ratio * 3.0,
                1.0,
            )

            object_component = min(
                edge_density * 6.0,
                1.0,
            )

            if submission_type == "TREE_PLANTATION":
                score = (
                    green_component * 0.35
                    + soil_component * 0.20
                    + object_component * 0.20
                    + quality_score * 0.25
                )

            else:
                score = (
                    green_component * 0.55
                    + soil_component * 0.10
                    + object_component * 0.10
                    + quality_score * 0.25
                )

        elif submission_type in {
            "RECYCLING",
            "WASTE_CLEANUP",
            "WASTE_REDUCTION",
        }:
            score = (
                min(edge_density * 10.0, 1.0) * 0.35
                + contrast_component * 0.30
                + quality_score * 0.25
                + min(green_ratio * 2.0, 1.0) * 0.10
            )

        elif submission_type in {
            "WATER_CONSERVATION",
        }:
            score = (
                min(blue_ratio * 4.0, 1.0) * 0.35
                + min(edge_density * 8.0, 1.0) * 0.20
                + contrast_component * 0.20
                + quality_score * 0.25
            )

        elif submission_type in {
            "SUSTAINABLE_TRANSPORT",
            "ENERGY_SAVING",
        }:
            score = (
                min(edge_density * 10.0, 1.0) * 0.35
                + contrast_component * 0.30
                + quality_score * 0.35
            )

        else:
            score = (
                quality_score * 0.50
                + min(edge_density * 8.0, 1.0) * 0.25
                + contrast_component * 0.25
            )

        return round(
            max(
                0.0,
                min(score, 1.0),
            ),
            3,
        )

    @staticmethod
    def _decision(
        relevance_score: float,
        quality_score: float,
    ) -> str:
        if quality_score < 0.30:
            return "NEEDS_REVIEW"

        if relevance_score >= 0.55:
            return "PASS"

        if relevance_score >= 0.35:
            return "NEEDS_REVIEW"

        return "FAIL"

    @staticmethod
    def _explanation(
        submission_type: str,
        decision: str,
        relevance_score: float,
        quality_score: float,
        labels: list[str],
    ) -> str:
        label_text = ", ".join(labels)

        if decision == "PASS":
            return (
                f"The image appears relevant for {submission_type}. "
                f"Local vision detected: {label_text}. "
                f"Relevance score is {relevance_score}, and quality score is {quality_score}."
            )

        if decision == "NEEDS_REVIEW":
            return (
                f"The image needs manual review for {submission_type}. "
                f"Local vision detected: {label_text}. "
                f"Relevance score is {relevance_score}, and quality score is {quality_score}."
            )

        return (
            f"The image does not strongly match the expected proof for {submission_type}. "
            f"Local vision detected: {label_text}. "
            f"Relevance score is {relevance_score}, and quality score is {quality_score}."
        )

    @staticmethod
    def _recommendations(
        decision: str,
        labels: list[str],
    ) -> list[str]:
        recommendations = []

        if "possibly_blurry_image" in labels:
            recommendations.append(
                "Upload a clearer image."
            )

        if "too_dark_image" in labels:
            recommendations.append(
                "Upload an image with better lighting."
            )

        if "too_bright_image" in labels:
            recommendations.append(
                "Avoid overexposed images."
            )

        if decision == "FAIL":
            recommendations.append(
                "Upload proof that clearly shows the claimed eco-action."
            )

        if decision == "NEEDS_REVIEW":
            recommendations.append(
                "Admin review is recommended before approval."
            )

        if not recommendations:
            recommendations.append(
                "Image quality and relevance look acceptable."
            )

        return recommendations

    @staticmethod
    def analyze_image(
        media: Any,
        submission_type: Any,
    ) -> dict:
        file_path = LocalVisionService.resolve_media_path(
            media=media,
        )

        image_data = np.fromfile(
            file_path,
            dtype=np.uint8,
        )

        image = cv2.imdecode(
            image_data,
            cv2.IMREAD_COLOR,
        )

        if image is None:
            raise ValueError(
                "Unable to read image file for vision analysis."
            )

        height, width = image.shape[:2]
        total_pixels = width * height

        gray = cv2.cvtColor(
            image,
            cv2.COLOR_BGR2GRAY,
        )

        hsv = cv2.cvtColor(
            image,
            cv2.COLOR_BGR2HSV,
        )

        blur_score = round(
            float(
                cv2.Laplacian(
                    gray,
                    cv2.CV_64F,
                ).var()
            ),
            3,
        )

        brightness_score = round(
            float(gray.mean()),
            3,
        )

        contrast_score = round(
            float(gray.std()),
            3,
        )

        green_mask = cv2.inRange(
            hsv,
            np.array([35, 35, 35]),
            np.array([95, 255, 255]),
        )

        brown_mask = cv2.inRange(
            hsv,
            np.array([5, 35, 25]),
            np.array([35, 255, 220]),
        )

        blue_mask = cv2.inRange(
            hsv,
            np.array([90, 35, 40]),
            np.array([135, 255, 255]),
        )

        white_mask = cv2.inRange(
            hsv,
            np.array([0, 0, 200]),
            np.array([180, 45, 255]),
        )

        gray_mask = cv2.inRange(
            hsv,
            np.array([0, 0, 55]),
            np.array([180, 40, 210]),
        )

        edges = cv2.Canny(
            gray,
            80,
            160,
        )

        green_ratio = LocalVisionService._safe_ratio(
            green_mask,
            total_pixels,
        )

        brown_ratio = LocalVisionService._safe_ratio(
            brown_mask,
            total_pixels,
        )

        blue_ratio = LocalVisionService._safe_ratio(
            blue_mask,
            total_pixels,
        )

        white_ratio = LocalVisionService._safe_ratio(
            white_mask,
            total_pixels,
        )

        gray_ratio = LocalVisionService._safe_ratio(
            gray_mask,
            total_pixels,
        )

        edge_density = LocalVisionService._safe_ratio(
            edges,
            total_pixels,
        )

        quality_score = LocalVisionService._quality_score(
            blur_score=blur_score,
            brightness_score=brightness_score,
            contrast_score=contrast_score,
        )

        normalized_submission_type = LocalVisionService._normalize_submission_type(
            submission_type=submission_type,
        )

        relevance_score = LocalVisionService._relevance_score(
            submission_type=normalized_submission_type,
            green_ratio=green_ratio,
            brown_ratio=brown_ratio,
            blue_ratio=blue_ratio,
            edge_density=edge_density,
            quality_score=quality_score,
            contrast_score=contrast_score,
        )

        confidence_score = round(
            (quality_score * 0.45) + (relevance_score * 0.55),
            3,
        )

        labels = LocalVisionService._detected_labels(
            green_ratio=green_ratio,
            brown_ratio=brown_ratio,
            blue_ratio=blue_ratio,
            white_ratio=white_ratio,
            gray_ratio=gray_ratio,
            edge_density=edge_density,
            blur_score=blur_score,
            brightness_score=brightness_score,
        )

        decision = LocalVisionService._decision(
            relevance_score=relevance_score,
            quality_score=quality_score,
        )

        explanation = LocalVisionService._explanation(
            submission_type=normalized_submission_type,
            decision=decision,
            relevance_score=relevance_score,
            quality_score=quality_score,
            labels=labels,
        )

        recommendations = LocalVisionService._recommendations(
            decision=decision,
            labels=labels,
        )

        file_name = (
            getattr(media, "original_file_name", None)
            or getattr(media, "stored_file_name", None)
            or getattr(media, "file_name", None)
        )

        return {
            "media_id": str(getattr(media, "id")),
            "file_name": file_name,
            "file_path": file_path,
            "width": width,
            "height": height,
            "blur_score": blur_score,
            "brightness_score": brightness_score,
            "contrast_score": contrast_score,
            "green_ratio": green_ratio,
            "brown_ratio": brown_ratio,
            "blue_ratio": blue_ratio,
            "white_ratio": white_ratio,
            "gray_ratio": gray_ratio,
            "edge_density": edge_density,
            "quality_score": quality_score,
            "relevance_score": relevance_score,
            "confidence_score": confidence_score,
            "detected_labels": labels,
            "decision": decision,
            "explanation": explanation,
            "recommendations": recommendations,
        }

    @staticmethod
    def analyze_submission_images(
        submission: Any,
        media_items: list[Any],
    ) -> dict:
        submission_type = getattr(
            submission,
            "submission_type",
            None,
        )

        normalized_submission_type = LocalVisionService._normalize_submission_type(
            submission_type,
        )

        image_items = [
            media
            for media in media_items
            if LocalVisionService.is_image_media(media)
        ]

        analyses = []

        for media in image_items:
            analysis = LocalVisionService.analyze_image(
                media=media,
                submission_type=submission_type,
            )

            analyses.append(analysis)

        if not analyses:
            return {
                "submission_id": str(getattr(submission, "id")),
                "submission_type": normalized_submission_type,
                "images_analyzed": 0,
                "final_decision": "NEEDS_REVIEW",
                "final_relevance_score": 0.0,
                "final_confidence_score": 0.0,
                "analysis_summary": "No image media was available for local vision analysis.",
                "analyses": [],
                "created_at": datetime.utcnow(),
            }

        best_analysis = max(
            analyses,
            key=lambda item: item["confidence_score"],
        )

        decisions = [
            analysis["decision"]
            for analysis in analyses
        ]

        if "PASS" in decisions:
            final_decision = "PASS"

        elif "NEEDS_REVIEW" in decisions:
            final_decision = "NEEDS_REVIEW"

        else:
            final_decision = "FAIL"

        final_relevance_score = round(
            max(
                analysis["relevance_score"]
                for analysis in analyses
            ),
            3,
        )

        final_confidence_score = round(
            max(
                analysis["confidence_score"]
                for analysis in analyses
            ),
            3,
        )

        analysis_summary = (
            f"Local vision analyzed {len(analyses)} image(s). "
            f"Best image decision is {best_analysis['decision']} with "
            f"relevance score {best_analysis['relevance_score']} and "
            f"confidence score {best_analysis['confidence_score']}."
        )

        return {
            "submission_id": str(getattr(submission, "id")),
            "submission_type": normalized_submission_type,
            "images_analyzed": len(analyses),
            "final_decision": final_decision,
            "final_relevance_score": final_relevance_score,
            "final_confidence_score": final_confidence_score,
            "analysis_summary": analysis_summary,
            "analyses": analyses,
            "created_at": datetime.utcnow(),
        }