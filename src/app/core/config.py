from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DATABASE_URL: str
    REDIS_URL: str
    TEMPLATE_DIR: str = "src/app/templates"
    STATIC_DIR: str = "src/app/static"
    ENVIRONMENT: str = "dev"
    PROJECT_NAME: str = "FastAPI Project"

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore"      # <<< con esto Pydantic no fallará si hay vars de más
    )

settings = Settings()