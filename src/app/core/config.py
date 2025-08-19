# Import necessary modules for environment settings and file path management
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

# ---------------------------- Base Directory ----------------------------

# Define the base directory of the project by resolving the current file's parent path
BASE_DIR = Path(__file__).resolve().parent.parent

# ---------------------------- Application Settings ----------------------------

class Settings(BaseSettings):
    """
    This class defines application-wide configuration settings.
    The values are loaded from environment variables (e.g., from a .env file).
    """

    DATABASE_URL: str                  # URL for connecting to the database
    REDIS_URL: str                     # URL for connecting to the Redis cache
    CACHE_EXPIRATION_TIME: int = 3600 # Default cache expiration time in seconds (1 hour)
    TEMPLATE_DIR: str = str(BASE_DIR / "templates")  # Path to HTML template directory
    STATIC_DIR: str = "src/app/static"               # Path to static files (CSS, JS, images)
    ENVIRONMENT: str = "dev"                         # Environment name (e.g., dev, prod)
    PROJECT_NAME: str = "FastAPI Project"            # Name of the project

    # ---------------------------- Configuration Metadata ----------------------------

    model_config = SettingsConfigDict(
        env_file=".env",             # Path to the environment file
        case_sensitive=False,        # Environment variables are case-insensitive
        extra="ignore"               # Ignore any extra variables not defined in this class
    )

# ---------------------------- Global Settings Instance ----------------------------

# Create a global instance of the settings to be used throughout the application
settings = Settings()