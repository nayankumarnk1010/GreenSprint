from pydantic_settings import BaseSettings
from pydantic_settings import SettingsConfigDict


class Settings(BaseSettings):
    # App settings
    APP_NAME: str = "GreenSprint"
    PROJECT_NAME: str = "GreenSprint"
    API_V1_PREFIX: str = "/api/v1"

    # Database
    DATABASE_URL: str = "sqlite:///./greensprint.db"

    # JWT settings
    SECRET_KEY: str = "change-this-secret-key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # Media upload settings
    MEDIA_STORAGE_DIR: str = "media"
    MAX_UPLOAD_SIZE_MB: int = 10

    # CORS
    BACKEND_CORS_ORIGINS: list[str] = ["*"]
    
    #Ai configs
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3.2:3b"
    AI_AUDIO_STORAGE_DIR: str = "media/ai_audio"
    AI_DEFAULT_LANGUAGE: str = "en"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()