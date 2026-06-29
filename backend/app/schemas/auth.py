from pydantic import BaseModel
from pydantic import EmailStr
from pydantic import Field
from app.core.enums import UserRole

import re
from pydantic import field_validator

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


class UserResponse(BaseModel):
    id: str
    email: EmailStr
    full_name: str
    role: UserRole

    model_config = {
        "from_attributes": True
    }