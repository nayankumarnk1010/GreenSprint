from fastapi import APIRouter
from fastapi import Depends

from sqlalchemy.orm import Session

from app.api.dependencies.rbac import require_role
from app.core.enums import UserRole
from app.db.dependencies import get_db
from app.schemas.system import SystemHealthResponse
from app.schemas.system import SystemIntegrationSummaryResponse
from app.schemas.system import SystemPingResponse
from app.services.system_service import SystemService


router = APIRouter()


@router.get(
    "/ping",
    response_model=SystemPingResponse,
)
def ping():
    return SystemService.ping()


@router.get(
    "/health",
    response_model=SystemHealthResponse,
)
def health(
    db: Session = Depends(get_db),
):
    return SystemService.health(
        db=db,
    )


@router.get(
    "/integration-summary",
    response_model=SystemIntegrationSummaryResponse,
)
def integration_summary(
    db: Session = Depends(get_db),
    current_user=Depends(
        require_role(
            UserRole.ADMIN,
        )
    ),
):
    return SystemService.integration_summary(
        db=db,
    )