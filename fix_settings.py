content = '''import os
from pydantic_settings import BaseSettings

class CodeGateSettings(BaseSettings):
    # Default to sqlite for local dev and testing
    DATABASE_URL: str = os.environ.get("DATABASE_URL", "sqlite:///./codegate.db")
    
    # Static Analysis Settings
    STATIC_ANALYSIS_ENABLED: bool = True
    RUFF_ENABLED: bool = True
    BANDIT_ENABLED: bool = True
    RADON_ENABLED: bool = True

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'

settings = CodeGateSettings()
'''
with open('codegate/config/settings.py', 'w', encoding='utf-8') as f:
    f.write(content)
