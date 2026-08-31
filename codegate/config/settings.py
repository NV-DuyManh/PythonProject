import os

from pydantic_settings import BaseSettings, SettingsConfigDict


class CodeGateSettings(BaseSettings):
    # Default to sqlite for local dev and testing
    DATABASE_URL: str = os.environ.get("DATABASE_URL", "sqlite:///./codegate.db")
    
    # Static Analysis Settings
    STATIC_ANALYSIS_ENABLED: bool = True
    ANALYZER_TIMEOUT_SECONDS: int = 300
    RUFF_ENABLED: bool = True
    BANDIT_ENABLED: bool = True
    RADON_ENABLED: bool = True

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = CodeGateSettings()
