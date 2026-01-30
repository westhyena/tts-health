from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # LLM Settings
    LLM_PROVIDER: str = "openai"
    OPENAI_API_KEY: Optional[str] = None
    OLLAMA_BASE_URL: str = "http://localhost:11434/v1"

    # EMR Settings
    EMR_API_URL: Optional[str] = None

    # App Settings
    UPLOAD_DIR: str = "uploads"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
