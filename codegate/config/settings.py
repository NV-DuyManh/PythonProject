import os
from pydantic_settings import BaseSettings

class CodeGateSettings(BaseSettings):
    # Default to sqlite for local dev and testing
    DATABASE_URL: str = os.environ.get("DATABASE_URL", "sqlite:///./codegate.db")
    
    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'

settings = CodeGateSettings()
