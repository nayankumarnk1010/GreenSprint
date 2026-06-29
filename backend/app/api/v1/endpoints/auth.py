from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import status

from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm

from app.core.exceptions import (
    UserAlreadyExistsException,
    InvalidCredentialsException,
)
from app.core.jwt import create_access_token
from app.db.dependencies import get_db
from app.schemas.auth import (
    UserRegister,
    UserResponse,
    
)
from app.schemas.token import TokenResponse
from app.services.auth_service import (
    AuthService,
)

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(
    payload: UserRegister,
    db: Session = Depends(get_db),
):
    try:
        user = AuthService.register_user(
            db=db,
            payload=payload,
        )

        return user

    except UserAlreadyExistsException as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )


@router.post(
    "/login",
    response_model=TokenResponse,
)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    try:

        user = AuthService.authenticate_user(
            db=db,
            email=form_data.username,
            password=form_data.password,
        )

        access_token = create_access_token(
            subject=user.id,
            role=user.role.value,
        )

        return TokenResponse(
            access_token=access_token,
        )

    except InvalidCredentialsException as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
            headers={
                "WWW-Authenticate": "Bearer",
            },
        )