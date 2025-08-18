from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
class Settings(BaseSettings):
    DATABASE_URL: str
    REDIS_URL: str
    CACHE_EXPIRATION_TIME: int = 3600
    TEMPLATE_DIR: str = str(BASE_DIR / "templates")
    STATIC_DIR: str = "src/app/static"
    ENVIRONMENT: str = "dev"
    PROJECT_NAME: str = "FastAPI Project"

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore"      # Ignore extra fields in the .env file
    )

settings = Settings()