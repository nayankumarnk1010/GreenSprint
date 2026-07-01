import re

from pydantic import BaseModel
from pydantic import EmailStr
from pydantic import Field
from pydantic import field_validator

from app.core.enums import UserRole


def validate_strong_password(value: str) -> str:
    if not re.search(r"[A-Z]", value):
        raise ValueError(
            "Password must contain at least one uppercase letter"
        )

    if not re.search(r"[a-z]", value):
        raise ValueError(
            "Password must contain at least one lowercase letter"
        )

    if not re.search(r"\d", value):
        raise ValueError(
            "Password must contain at least one number"
        )

    if not re.search(
        r"[!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>/?]",
        value,
    ):
        raise ValueError(
            "Password must contain at least one special character"
        )

    return value


class UserRegister(BaseModel):
    email: EmailStr

    password: str = Field(
        min_length=8,
        max_length=128,
    )

    full_name: str

    role: UserRole = UserRole.USER

    @field_validator("password")
    @classmethod
    def validate_password(
        cls,
        value: str,
    ) -> str:
        return validate_strong_password(value)


class UserResponse(BaseModel):
    id: str
    email: EmailStr
    full_name: str
    role: UserRole

    model_config = {
        "from_attributes": True
    }


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str = Field(
        min_length=20,
        max_length=300,
    )

    new_password: str = Field(
        min_length=8,
        max_length=128,
    )

    @field_validator("new_password")
    @classmethod
    def validate_new_password(
        cls,
        value: str,
    ) -> str:
        return validate_strong_password(value)


class MessageResponse(BaseModel):
    message: str