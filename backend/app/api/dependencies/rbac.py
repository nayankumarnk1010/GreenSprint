from fastapi import Depends
from fastapi import HTTPException
from fastapi import status

from app.api.dependencies.auth import get_current_user
from app.core.enums import UserRole
from app.models.user import User


def require_role(*allowed_roles: UserRole):

    def role_checker(
        current_user: User = Depends(
            get_current_user
        ),
    ) -> User:

        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )

        return current_user

    return role_checker