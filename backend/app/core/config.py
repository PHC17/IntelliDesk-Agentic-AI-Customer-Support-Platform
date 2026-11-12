"""Typed application settings loaded from environment variables."""

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration for the API and retrieval pipeline."""

    app_name: str = "IntelliDesk"
    environment: str = "development"
    api_prefix: str = ""
    cors_origins: str = "http://localhost:8501"
    openai_api_key: str = ""
    openai_base_url: str = "https://api.openai.com/v1"
    llm_model: str = "gpt-4o-mini"
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    chroma_persist_directory: Path = Path("./data/chroma")
    chunk_size: int = 900
    chunk_overlap: int = 150
    retrieval_top_k: int = 5
    max_upload_size_mb: int = 25

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @property
    def cors_origin_list(self) -> list[str]:
        """Return configured CORS origins as a normalized list."""
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    """Return the process-wide settings singleton."""
    settings = Settings()
    settings.chroma_persist_directory.mkdir(parents=True, exist_ok=True)
    return settings
