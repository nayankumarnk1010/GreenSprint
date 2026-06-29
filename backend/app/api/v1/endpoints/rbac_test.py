from fastapi import APIRouter
from fastapi import Depends

from app.api.dependencies.rbac import require_role
from app.core.enums import UserRole
from app.models.user import User

router = APIRouter(
    prefix="/rbac-test",
    tags=["RBAC"],
)


@router.get("/admin")
def admin_only(
    current_user: User = Depends(
        require_role(UserRole.ADMIN)
    ),
):
    return {
        "message": "Admin access granted"
    }