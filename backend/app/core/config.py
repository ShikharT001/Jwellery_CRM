"""
Application configuration using pydantic-settings.

All settings are loaded from environment variables (or a .env file).
This is the single source of truth for all configuration values.
"""

from functools import lru_cache
from typing import List

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Central configuration class.

    Settings are read from environment variables.
    In development, they can also be loaded from a .env file.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # -------------------------
    # Application
    # -------------------------
    environment: str = "development"
    secret_key: str = "change-this-secret-key"
    debug: bool = True
    log_level: str = "INFO"
    api_v1_prefix: str = "/api/v1"

    # -------------------------
    # Database
    # -------------------------
    database_url: str = ""

    # -------------------------
    # Supabase
    # -------------------------
    supabase_url: str = ""
    supabase_service_role_key: str = ""
    supabase_jwt_secret: str = ""

    # -------------------------
    # CORS
    # -------------------------
    cors_origins: str = "http://localhost:3000"

    # -------------------------
    # Super Admin
    # -------------------------
    super_admin_email: str = ""

    @property
    def cors_origins_list(self) -> List[str]:
        """Parse comma-separated CORS origins into a list."""
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def is_production(self) -> bool:
        return self.environment.lower() == "production"

    @field_validator("database_url")
    @classmethod
    def validate_database_url(cls, v: str) -> str:
        if v and v.startswith("postgresql://"):
            return v.replace("postgresql://", "postgresql+psycopg2://", 1)
        return v


@lru_cache()
def get_settings() -> Settings:
    """
    Return cached Settings instance.

    The @lru_cache decorator ensures settings are only loaded once
    per application lifecycle, making this safe to call frequently.
    """
    return Settings()


# Module-level convenience reference
settings = get_settings()
