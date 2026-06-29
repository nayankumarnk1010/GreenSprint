from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.enums import UserRole
from app.core.exceptions import (
    UserAlreadyExistsException,
    InvalidCredentialsException,
)
from app.core.security import hash_password
from app.core.security import verify_password
from app.models.user import User
from app.schemas.auth import UserRegister


class AuthService:

    @staticmethod
    def get_user_by_email(
        db: Session,
        email: str,
    ) -> User | None:

        stmt = select(User).where(
            User.email == email
        )

        return db.scalar(stmt)

    @staticmethod
    def get_user_by_id(
        db: Session,
        user_id: str,
    ) -> User | None:

        stmt = select(User).where(
            User.id == user_id
        )

        return db.scalar(stmt)

    @staticmethod
    def register_user(
        db: Session,
        payload: UserRegister,
    ) -> User:

        existing_user = (
            AuthService.get_user_by_email(
                db,
                payload.email,
            )
        )

        if existing_user:
            raise UserAlreadyExistsException(
                "Email already registered"
            )

        if payload.role == UserRole.ADMIN:
            raise ValueError(
                "Admin accounts cannot be self-registered"
            )

        user = User(
            email=payload.email,
            password_hash=hash_password(
                payload.password
            ),
            full_name=payload.full_name,
            role=payload.role,
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        return user

    @staticmethod
    def authenticate_user(
        db: Session,
        email: str,
        password: str,
    ) -> User:

        user = (
            AuthService.get_user_by_email(
                db,
                email,
            )
        )

        if not user:
            raise InvalidCredentialsException(
                "Invalid email or password"
            )

        if not verify_password(
            password,
            user.password_hash,
        ):
            raise InvalidCredentialsException(
                "Invalid email or password"
            )

        return user