import json
from datetime import datetime
from pathlib import Path
from typing import Any

from PIL import Image

import torch
import torch.nn as nn
from torchvision import models
from torchvision import transforms

try:
    from app.services.ai.ollama_client import OllamaClient
except Exception:
    OllamaClient = None


class PlantDiseaseAIService:
    MODEL_NAME = "pretrained_mobilenetv2_plant_disease"
    MODEL_SOURCE = "Daksh159/plant-disease-mobilenetv2"

    MODEL_DIR = Path("models/plant_disease")
    MODEL_PATH = MODEL_DIR / "mobilenetv2_plant.pth"
    CLASS_NAMES_PATH = MODEL_DIR / "class_names.json"
    TREATMENT_PATH = Path("app/ai/knowledge/plant_treatments.json")

    _model = None
    _class_names: list[str] | None = None
    _treatments: dict | None = None

    @staticmethod
    def health() -> dict:
        model_available = PlantDiseaseAIService.MODEL_PATH.exists()
        class_names_available = PlantDiseaseAIService.CLASS_NAMES_PATH.exists()

        classes_count = 0

        if class_names_available:
            try:
                classes_count = len(
                    PlantDiseaseAIService._load_class_names()
                )
            except Exception:
                classes_count = 0

        status = (
            "OK"
            if model_available and class_names_available and classes_count > 0
            else "MISSING_MODEL_FILES"
        )

        message = (
            "Plant disease model is ready."
            if status == "OK"
            else "Plant disease model files are missing. Download the model and create class_names.json first."
        )

        return {
            "status": status,
            "model_available": model_available,
            "class_names_available": class_names_available,
            "classes_count": classes_count,
            "model_path": str(PlantDiseaseAIService.MODEL_PATH),
            "class_names_path": str(PlantDiseaseAIService.CLASS_NAMES_PATH),
            "message": message,
        }

    @staticmethod
    def _device():
        return torch.device(
            "cuda"
            if torch.cuda.is_available()
            else "cpu"
        )

    @staticmethod
    def _load_class_names() -> list[str]:
        if PlantDiseaseAIService._class_names is not None:
            return PlantDiseaseAIService._class_names

        if not PlantDiseaseAIService.CLASS_NAMES_PATH.exists():
            raise FileNotFoundError(
                "class_names.json not found."
            )

        with open(
            PlantDiseaseAIService.CLASS_NAMES_PATH,
            "r",
            encoding="utf-8",
        ) as file:
            data = json.load(file)

        if isinstance(data, list):
            class_names = data

        elif isinstance(data, dict):
            if "class_names" in data and isinstance(data["class_names"], list):
                class_names = data["class_names"]

            else:
                sorted_items = sorted(
                    data.items(),
                    key=lambda item: int(item[0])
                    if str(item[0]).isdigit()
                    else str(item[0]),
                )

                class_names = [
                    value
                    for _, value in sorted_items
                ]

        else:
            raise ValueError(
                "Invalid class_names.json format."
            )

        PlantDiseaseAIService._class_names = [
            str(class_name)
            for class_name in class_names
        ]

        return PlantDiseaseAIService._class_names

    @staticmethod
    def _load_treatments() -> dict:
        if PlantDiseaseAIService._treatments is not None:
            return PlantDiseaseAIService._treatments

        if not PlantDiseaseAIService.TREATMENT_PATH.exists():
            PlantDiseaseAIService._treatments = {
                "default": {
                    "severity": "MODERATE",
                    "description": "The model detected a possible plant disease. Use this as decision support, not a final expert diagnosis.",
                    "organic_treatment": [
                        "Remove badly affected leaves.",
                        "Avoid overwatering.",
                        "Improve sunlight and air circulation."
                    ],
                    "chemical_treatment": [
                        "Use crop-specific fungicide or pesticide only if symptoms are severe and follow product instructions."
                    ],
                    "prevention": [
                        "Inspect plants regularly.",
                        "Keep the plant area clean.",
                        "Avoid watering leaves directly."
                    ]
                }
            }

            return PlantDiseaseAIService._treatments

        with open(
            PlantDiseaseAIService.TREATMENT_PATH,
            "r",
            encoding="utf-8",
        ) as file:
            PlantDiseaseAIService._treatments = json.load(file)

        return PlantDiseaseAIService._treatments

    @staticmethod
    def _build_model(
        num_classes: int,
    ):
        model = models.mobilenet_v2(
            weights=None,
        )

        in_features = model.classifier[1].in_features

        model.classifier[1] = nn.Linear(
            in_features,
            num_classes,
        )

        return model

    @staticmethod
    def _load_model():
        if PlantDiseaseAIService._model is not None:
            return PlantDiseaseAIService._model

        if not PlantDiseaseAIService.MODEL_PATH.exists():
            raise FileNotFoundError(
                "mobilenetv2_plant.pth not found."
            )

        class_names = PlantDiseaseAIService._load_class_names()
        device = PlantDiseaseAIService._device()

        model = PlantDiseaseAIService._build_model(
            num_classes=len(class_names),
        )

        checkpoint = torch.load(
            PlantDiseaseAIService.MODEL_PATH,
            map_location=device,
        )

        if isinstance(checkpoint, dict) and "state_dict" in checkpoint:
            state_dict = checkpoint["state_dict"]

        elif isinstance(checkpoint, dict) and "model_state_dict" in checkpoint:
            state_dict = checkpoint["model_state_dict"]

        else:
            state_dict = checkpoint

        cleaned_state_dict = {}

        for key, value in state_dict.items():
            cleaned_key = key

            if cleaned_key.startswith("module."):
                cleaned_key = cleaned_key.replace(
                    "module.",
                    "",
                    1,
                )

            cleaned_state_dict[cleaned_key] = value

        model.load_state_dict(
            cleaned_state_dict,
            strict=False,
        )

        model.to(device)
        model.eval()

        PlantDiseaseAIService._model = model

        return PlantDiseaseAIService._model

    @staticmethod
    def _transform():
        return transforms.Compose(
            [
                transforms.Resize(
                    (224, 224),
                ),
                transforms.ToTensor(),
                transforms.Normalize(
                    mean=[
                        0.485,
                        0.456,
                        0.406,
                    ],
                    std=[
                        0.229,
                        0.224,
                        0.225,
                    ],
                ),
            ]
        )

    @staticmethod
    def _clean_text(
        value: str,
    ) -> str:
        cleaned = (
            value.replace(
                "___",
                " ",
            )
            .replace(
                "__",
                " ",
            )
            .replace(
                "_",
                " ",
            )
            .replace(
                "-",
                " ",
            )
        )

        cleaned = " ".join(
            cleaned.split()
        )

        return cleaned.strip()

    @staticmethod
    def _clean_class_name(
        class_name: str,
    ) -> str:
        return PlantDiseaseAIService._clean_text(
            class_name
        )

    @staticmethod
    def _extract_crop_and_disease(
        class_name: str,
    ) -> tuple[str | None, str]:
        if "___" in class_name:
            crop_part, disease_part = class_name.split(
                "___",
                1,
            )

            crop_name = PlantDiseaseAIService._clean_text(
                crop_part
            )

            disease_name = PlantDiseaseAIService._clean_text(
                disease_part
            )

            if "healthy" in disease_name.lower():
                return crop_name or None, "healthy"

            return crop_name or None, disease_name

        cleaned = PlantDiseaseAIService._clean_class_name(
            class_name
        )

        lowered = cleaned.lower()

        if "healthy" in lowered:
            crop_name = (
                cleaned.replace(
                    "healthy",
                    "",
                )
                .replace(
                    "Healthy",
                    "",
                )
                .strip()
            )

            return crop_name or None, "healthy"

        parts = cleaned.split(
            " ",
            1,
        )

        if len(parts) == 2:
            crop_name = parts[0]
            disease_name = parts[1]
        else:
            crop_name = None
            disease_name = cleaned

        return crop_name, disease_name.strip()

    @staticmethod
    def _treatment_key(
        crop_name: str | None,
        disease_name: str,
    ) -> str:
        crop = (crop_name or "").lower()
        disease = disease_name.lower()

        if "healthy" in disease:
            return "healthy"

        if "grape" in crop and "black rot" in disease:
            return "grape_black_rot"

        if "apple" in crop and "black rot" in disease:
            return "apple_black_rot"

        if "black rot" in disease:
            return "black_rot"

        if "early blight" in disease:
            return "early_blight"

        if "late blight" in disease:
            return "late_blight"

        if "bacterial" in disease:
            return "bacterial_spot"

        if "powdery" in disease or "mildew" in disease:
            return "powdery_mildew"

        if "rust" in disease:
            return "rust"

        if "leaf mold" in disease:
            return "leaf_mold"

        if (
            "leaf spot" in disease
            or "septoria" in disease
            or "target spot" in disease
            or "gray leaf spot" in disease
            or "cercospora" in disease
            or "spot" in disease
        ):
            return "leaf_spot"

        if "yellow" in disease and "curl" in disease:
            return "yellow_leaf_curl"

        if "mosaic" in disease or "virus" in disease:
            return "mosaic_virus"

        if "spider" in disease or "mite" in disease:
            return "spider_mites"

        if "leaf scorch" in disease or "scorch" in disease:
            return "leaf_scorch"

        if "citrus greening" in disease or "haunglongbing" in disease:
            return "citrus_greening"

        if "esca" in disease or "black measles" in disease:
            return "grape_esca"

        return "default"

    @staticmethod
    def _get_treatment(
        crop_name: str | None,
        disease_name: str,
    ) -> dict:
        treatments = PlantDiseaseAIService._load_treatments()

        key = PlantDiseaseAIService._treatment_key(
            crop_name=crop_name,
            disease_name=disease_name,
        )

        return treatments.get(
            key,
            treatments.get(
                "default",
                {},
            ),
        )

    @staticmethod
    def _confidence_level(
        confidence_score: float,
    ) -> str:
        if confidence_score >= 0.75:
            return "HIGH"

        if confidence_score >= 0.50:
            return "MEDIUM"

        return "LOW"

    @staticmethod
    def _warning_message(
        confidence_score: float,
        image_width: int,
        image_height: int,
    ) -> str:
        warnings = []

        if confidence_score < 0.50:
            warnings.append(
                "Model confidence is low, so this should be treated as a possible disease only."
            )

        elif confidence_score < 0.75:
            warnings.append(
                "Model confidence is moderate. Use this result as decision support."
            )

        else:
            warnings.append(
                "Model confidence is good, but this is still AI-based decision support."
            )

        if image_width < 500 or image_height < 500:
            warnings.append(
                "The uploaded image is small. A clearer close-up leaf image may improve accuracy."
            )

        warnings.append(
            "For severe crop loss or spreading infection, ask an agricultural expert."
        )

        return " ".join(warnings)

    @staticmethod
    def _rule_based_guide_answer(
        crop_name: str | None,
        disease_name: str,
        confidence_score: float,
        treatment: dict,
        user_question: str | None = None,
    ) -> str:
        crop_text = crop_name or "the plant"
        confidence_level = PlantDiseaseAIService._confidence_level(
            confidence_score
        )

        question = (
            user_question or ""
        ).lower()

        if "healthy" in disease_name.lower():
            return (
                f"The image suggests that {crop_text} may be healthy. "
                f"Confidence level is {confidence_level}. "
                "Continue regular watering, provide suitable sunlight, inspect leaves weekly, "
                "and avoid overwatering."
            )

        if confidence_score < 0.50:
            confidence_note = (
                "The model confidence is low, so treat this as a possible condition, not a confirmed diagnosis. "
            )
        else:
            confidence_note = (
                "The model result can be used as decision-support guidance. "
            )

        if any(
            word in question
            for word in [
                "prevent",
                "prevention",
                "avoid",
                "stop",
            ]
        ):
            prevention = treatment.get(
                "prevention",
                [],
            )

            return (
                f"{confidence_note}"
                f"For {crop_text} {disease_name}, prevention steps are: "
                + " ".join(
                    f"{index + 1}. {item}"
                    for index, item in enumerate(prevention)
                )
            )

        if any(
            word in question
            for word in [
                "treat",
                "treatment",
                "cure",
                "spray",
                "medicine",
                "neem",
                "what should i do",
            ]
        ):
            organic = treatment.get(
                "organic_treatment",
                [],
            )

            chemical = treatment.get(
                "chemical_treatment",
                [],
            )

            return (
                f"{confidence_note}"
                f"For possible {crop_text} {disease_name}, first try safe care steps: "
                + " ".join(
                    f"{index + 1}. {item}"
                    for index, item in enumerate(organic)
                )
                + " Chemical option: "
                + " ".join(chemical)
            )

        if any(
            word in question
            for word in [
                "serious",
                "danger",
                "severity",
                "bad",
                "high",
            ]
        ):
            return (
                f"{confidence_note}"
                f"Severity is marked as {treatment.get('severity', 'MODERATE')}. "
                f"{treatment.get('description', '')} "
                "If symptoms spread quickly, isolate affected leaves or plants and ask an expert."
            )

        return (
            f"{confidence_note}"
            f"The model detected possible {crop_text} {disease_name}. "
            f"Severity: {treatment.get('severity', 'MODERATE')}. "
            f"{treatment.get('description', '')} "
            "Recommended first steps: "
            + " ".join(
                f"{index + 1}. {item}"
                for index, item in enumerate(
                    treatment.get(
                        "organic_treatment",
                        [],
                    )
                )
            )
        )

    @staticmethod
    def _llm_guide_answer(
        crop_name: str | None,
        disease_name: str,
        confidence_score: float,
        treatment: dict,
        warning: str,
        user_question: str | None,
    ) -> str | None:
        if not user_question:
            return None

        if OllamaClient is None:
            return None

        prompt = f"""
You are a plant health guide inside GreenSprint.

Answer the user's plant-care question using only the prediction and treatment data below.
Do not invent unsupported pesticide names.
Keep the answer simple, safe, and practical.

Prediction:
Crop: {crop_name or "Unknown"}
Disease: {disease_name}
Confidence score: {confidence_score}
Warning: {warning}

Treatment data:
{json.dumps(treatment, ensure_ascii=False, indent=2)}

User question:
{user_question}

Answer requirements:
- Mention if confidence is low.
- Give practical next steps.
- Include prevention advice if useful.
- Do not claim this is a final expert diagnosis.
"""

        try:
            success, answer = OllamaClient.generate(
                prompt=prompt,
                system_prompt=(
                    "You are a safe plant-health assistant. "
                    "Give practical agricultural guidance. "
                    "Do not give harmful instructions."
                ),
                temperature=0.2,
            )

            if success and answer:
                return answer

        except Exception:
            return None

        return None

    @staticmethod
    def _guide_answer(
        crop_name: str | None,
        disease_name: str,
        confidence_score: float,
        treatment: dict,
        warning: str,
        user_question: str | None = None,
    ) -> str:
        llm_answer = PlantDiseaseAIService._llm_guide_answer(
            crop_name=crop_name,
            disease_name=disease_name,
            confidence_score=confidence_score,
            treatment=treatment,
            warning=warning,
            user_question=user_question,
        )

        if llm_answer:
            return llm_answer

        return PlantDiseaseAIService._rule_based_guide_answer(
            crop_name=crop_name,
            disease_name=disease_name,
            confidence_score=confidence_score,
            treatment=treatment,
            user_question=user_question,
        )

    @staticmethod
    def predict_from_image_path(
        image_path: str,
        user_question: str | None = None,
    ) -> dict:
        model = PlantDiseaseAIService._load_model()
        class_names = PlantDiseaseAIService._load_class_names()
        device = PlantDiseaseAIService._device()

        path = Path(image_path)

        if not path.exists():
            raise FileNotFoundError(
                "Plant image file not found."
            )

        with Image.open(path) as image:
            image = image.convert("RGB")
            image_width, image_height = image.size

            tensor = PlantDiseaseAIService._transform()(image)
            tensor = tensor.unsqueeze(0).to(device)

        with torch.no_grad():
            outputs = model(tensor)

            probabilities = torch.softmax(
                outputs,
                dim=1,
            )[0]

            top_probabilities, top_indices = torch.topk(
                probabilities,
                k=min(
                    5,
                    len(class_names),
                ),
            )

        top_predictions = []

        for probability, index in zip(
            top_probabilities,
            top_indices,
        ):
            class_index = int(
                index.item()
            )

            raw_class_name = class_names[class_index]

            crop_name, disease_name = PlantDiseaseAIService._extract_crop_and_disease(
                raw_class_name
            )

            top_predictions.append(
                {
                    "class_name": raw_class_name,
                    "display_name": PlantDiseaseAIService._clean_class_name(
                        raw_class_name
                    ),
                    "crop_name": crop_name,
                    "disease_name": disease_name,
                    "confidence_score": round(
                        float(probability.item()),
                        4,
                    ),
                }
            )

        best_prediction = top_predictions[0]

        crop_name = best_prediction["crop_name"]
        disease_name = best_prediction["disease_name"]
        confidence_score = best_prediction["confidence_score"]

        treatment = PlantDiseaseAIService._get_treatment(
            crop_name=crop_name,
            disease_name=disease_name,
        )

        confidence_level = PlantDiseaseAIService._confidence_level(
            confidence_score
        )

        warning = PlantDiseaseAIService._warning_message(
            confidence_score=confidence_score,
            image_width=image_width,
            image_height=image_height,
        )

        guide_answer = PlantDiseaseAIService._guide_answer(
            crop_name=crop_name,
            disease_name=disease_name,
            confidence_score=confidence_score,
            treatment=treatment,
            warning=warning,
            user_question=user_question,
        )

        return {
            "predicted_class": best_prediction["class_name"],
            "crop_name": crop_name,
            "disease_name": disease_name,
            "confidence_score": confidence_score,
            "confidence_level": confidence_level,
            "top_predictions": top_predictions,
            "treatment": treatment,
            "guide_answer": guide_answer,
            "query_answered": bool(
                user_question
                and user_question.strip()
            ),
            "model_name": PlantDiseaseAIService.MODEL_NAME,
            "model_source": PlantDiseaseAIService.MODEL_SOURCE,
            "image_width": image_width,
            "image_height": image_height,
            "warning": warning,
            "created_at": datetime.utcnow(),
        }