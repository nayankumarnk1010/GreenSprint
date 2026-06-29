from fastapi import Depends
from fastapi import HTTPException
from fastapi import status

from jose import JWTError
from sqlalchemy.orm import Session

from fastapi.security import OAuth2PasswordBearer

from app.core.jwt import decode_token
from app.db.dependencies import get_db
from app.models.user import User
from app.services.auth_service import AuthService

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/login"
)


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={
            "WWW-Authenticate": "Bearer",
        },
    )

    try:

        payload = decode_token(token)

        user_id = payload.get("sub")

        if not user_id:
            raise credentials_exception

    except JWTError:
        raise credentials_exception

    user = AuthService.get_user_by_id(
        db=db,
        user_id=user_id,
    )

    if not user:
        raise credentials_exception

    return user