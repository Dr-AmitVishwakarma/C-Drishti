from functools import lru_cache

from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
)


class Settings(BaseSettings):
    """
    Central configuration for the C-Drishti backend.

    Environment-specific values should be supplied through
    the backend/.env file rather than hard-coded throughout
    the application.
    """

    app_name: str = "C-Drishti API"

    app_version: str = "0.3.0"

    environment: str = "development"

    debug: bool = True

    api_v1_prefix: str = "/api/v1"

    frontend_origin: str = (
        "http://localhost:8080"
    )

    ollama_base_url: str = (
        "http://127.0.0.1:11434"
    )

    ollama_model: str = "llama3.2:3b"

    rag_collection_name: str = (
        "c_drishti_legal"
    )

    rag_max_distance: float = 1.35

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    """
    Return one cached Settings instance.
    """

    return Settings()


settings = get_settings()