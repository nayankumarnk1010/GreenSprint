from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException

from sqlalchemy.orm import Session

from app.api.dependencies.auth import get_current_user
from app.api.dependencies.rbac import require_role
from app.core.enums import UserRole
from app.db.dependencies import get_db
from app.models.plant_diagnosis import PlantDiagnosis
from app.models.user import User
from app.schemas.plant_health import PlantDiagnosisRequest
from app.schemas.plant_health import PlantDiagnosisResponse
from app.services.plant_health_service import PlantHealthService


router = APIRouter()


@router.post(
    "/submissions/{submission_id}/diagnose",
    response_model=PlantDiagnosisResponse,
)
def diagnose_submission(
    submission_id: str,
    payload: PlantDiagnosisRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return PlantHealthService.diagnose_submission(
            db=db,
            submission_id=submission_id,
            user_id=current_user.id,
            plant_name=payload.plant_name,
            user_question=payload.user_question,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Plant diagnosis failed: {exc}",
        )


@router.get(
    "/diagnoses/my",
    response_model=list[PlantDiagnosisResponse],
)
def get_my_diagnoses(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    diagnoses = PlantHealthService.get_my_diagnoses(
        db=db,
        user_id=current_user.id,
    )

    results = []

    for diagnosis in diagnoses:
        detail = PlantHealthService.get_diagnosis_detail(
            db=db,
            diagnosis_id=diagnosis.id,
        )

        if detail:
            results.append(detail)

    return results


@router.get(
    "/diagnoses/{diagnosis_id}",
    response_model=PlantDiagnosisResponse,
)
def get_diagnosis_detail(
    diagnosis_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    diagnosis = (
        db.query(PlantDiagnosis)
        .filter(PlantDiagnosis.id == diagnosis_id)
        .first()
    )

    if not diagnosis:
        raise HTTPException(
            status_code=404,
            detail="Diagnosis not found.",
        )

    if (
        str(diagnosis.user_id) != str(current_user.id)
        and current_user.role != UserRole.ADMIN
    ):
        raise HTTPException(
            status_code=403,
            detail="You are not allowed to view this diagnosis.",
        )

    detail = PlantHealthService.get_diagnosis_detail(
        db=db,
        diagnosis_id=diagnosis_id,
    )

    if not detail:
        raise HTTPException(
            status_code=404,
            detail="Diagnosis not found.",
        )

    return detail


@router.get(
    "/admin/manual-review",
    response_model=list[PlantDiagnosisResponse],
)
def get_manual_review_diagnoses(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role(
            UserRole.ADMIN,
        )
    ),
):
    return PlantHealthService.get_manual_review_diagnoses(
        db=db,
    )