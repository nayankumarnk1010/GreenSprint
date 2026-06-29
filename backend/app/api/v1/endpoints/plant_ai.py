import shutil
import uuid
from pathlib import Path

from fastapi import APIRouter
from fastapi import File
from fastapi import Form
from fastapi import HTTPException
from fastapi import UploadFile

from app.schemas.plant_ai import PlantDiseaseModelHealthResponse
from app.schemas.plant_ai import PlantDiseasePredictionResponse
from app.services.ai.plant_disease_ai_service import PlantDiseaseAIService


router = APIRouter()


UPLOAD_DIR = Path("media/plant_ai_uploads")
UPLOAD_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


ALLOWED_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".webp",
}


@router.get(
    "/health",
    response_model=PlantDiseaseModelHealthResponse,
)
def health():
    return PlantDiseaseAIService.health()


@router.post(
    "/predict",
    response_model=PlantDiseasePredictionResponse,
)
def predict_plant_disease(
    image: UploadFile = File(...),
    user_question: str | None = Form(
        default=None,
        description=(
            "Optional user question, for example: "
            "'How can I treat this?', 'Is this serious?', "
            "'How can I prevent it?'"
        ),
    ),
):
    extension = Path(
        image.filename or ""
    ).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Only JPG, JPEG, PNG, and WEBP images are allowed.",
        )

    file_name = f"{uuid.uuid4()}{extension}"
    file_path = UPLOAD_DIR / file_name

    try:
        with open(
            file_path,
            "wb",
        ) as buffer:
            shutil.copyfileobj(
                image.file,
                buffer,
            )

        return PlantDiseaseAIService.predict_from_image_path(
            image_path=str(file_path),
            user_question=user_question,
        )

    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Plant disease prediction failed: {exc}",
        )