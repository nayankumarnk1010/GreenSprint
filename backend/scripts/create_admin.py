import os

from passlib.context import CryptContext
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.core.enums import UserRole
from app.models.user import User


pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
)


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def main():
    admin_email = os.getenv(
        "ADMIN_EMAIL",
        "admin@example.com",
    )

    admin_password = os.getenv(
        "ADMIN_PASSWORD",
        "Admin@12345",
    )

    admin_name = os.getenv(
        "ADMIN_NAME",
        "GreenSprint Admin",
    )

    engine = create_engine(
        settings.DATABASE_URL,
        connect_args={"check_same_thread": False}
        if settings.DATABASE_URL.startswith("sqlite")
        else {},
    )

    SessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
    )

    db = SessionLocal()

    try:
        existing_user = (
            db.query(User)
            .filter(User.email == admin_email)
            .first()
        )

        if existing_user:
            existing_user.full_name = admin_name
            existing_user.role = UserRole.ADMIN
            existing_user.is_active = True
            existing_user.is_verified = True

            if admin_password:
                existing_user.password_hash = hash_password(admin_password)

            db.commit()

            print("Admin user already existed. Updated to ADMIN role.")
            print(f"Email: {admin_email}")
            print(f"Password: {admin_password}")
            return

        admin_user = User(
            email=admin_email,
            password_hash=hash_password(admin_password),
            full_name=admin_name,
            role=UserRole.ADMIN,
            is_active=True,
            is_verified=True,
        )

        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)

        print("Admin user created successfully.")
        print(f"Admin ID: {admin_user.id}")
        print(f"Email: {admin_email}")
        print(f"Password: {admin_password}")

    finally:
        db.close()


if __name__ == "__main__":
    main()