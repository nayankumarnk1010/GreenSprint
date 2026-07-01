import hashlib
import secrets
from datetime import datetime
from datetime import timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.enums import UserRole
from app.core.exceptions import (
    UserAlreadyExistsException,
    InvalidCredentialsException,
)
from app.core.security import hash_password
from app.core.security import verify_password
from app.models.password_reset_token import PasswordResetToken
from app.models.user import User
from app.schemas.auth import UserRegister
from app.services.email_service import EmailService


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

    @staticmethod
    def _hash_reset_token(
        token: str,
    ) -> str:
        return hashlib.sha256(
            token.encode("utf-8")
        ).hexdigest()

    @staticmethod
    def request_password_reset(
        db: Session,
        email: str,
    ) -> None:
        user = AuthService.get_user_by_email(
            db=db,
            email=email,
        )

        # Security rule:
        # Do not reveal whether the email exists.
        if not user:
            return

        now = datetime.utcnow()

        db.query(PasswordResetToken).filter(
            PasswordResetToken.user_id == user.id,
            PasswordResetToken.used_at.is_(None),
        ).update(
            {
                PasswordResetToken.used_at: now,
            },
            synchronize_session=False,
        )

        raw_token = secrets.token_urlsafe(48)
        token_hash = AuthService._hash_reset_token(raw_token)

        reset_token = PasswordResetToken(
            user_id=user.id,
            token_hash=token_hash,
            expires_at=now
            + timedelta(
                minutes=settings.PASSWORD_RESET_EXPIRE_MINUTES
            ),
        )

        db.add(reset_token)
        db.commit()

        reset_link = (
            f"{settings.FRONTEND_URL.rstrip()}"
            f"/reset-password?token={raw_token}"
        )

        EmailService.send_password_reset_email(
            to_email=user.email,
            full_name=user.full_name,
            reset_link=reset_link,
        )

    @staticmethod
    def reset_password(
        db: Session,
        token: str,
        new_password: str,
    ) -> None:
        token_hash = AuthService._hash_reset_token(token)

        reset_token = (
            db.query(PasswordResetToken)
            .filter(
                PasswordResetToken.token_hash == token_hash,
                PasswordResetToken.used_at.is_(None),
            )
            .first()
        )

        if not reset_token:
            raise ValueError(
                "Invalid or expired reset token"
            )

        now = datetime.utcnow()

        if reset_token.expires_at < now:
            reset_token.used_at = now
            db.commit()

            raise ValueError(
                "Invalid or expired reset token"
            )

        user = AuthService.get_user_by_id(
            db=db,
            user_id=reset_token.user_id,
        )

        if not user:
            reset_token.used_at = now
            db.commit()

            raise ValueError(
                "Invalid or expired reset token"
            )

        user.password_hash = hash_password(new_password)
        reset_token.used_at = now

        db.commit()