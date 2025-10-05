from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )
    
    database_url: str = Field(..., description="Database connection URL")
    redis_url: str = Field(..., description="Redis connection URL")
    celery_broker_url: str = Field(..., description="Celery broker URL")
    celery_result_backend: str = Field(..., description="Celery result backend URL")
    
    serp_api_key: str = Field(default="", description="SERP API key")
    llm_api_key: str = Field(default="", description="LLM API key")
    
    secret_key: str = Field(..., description="Secret key")
    debug: bool = Field(default=False, description="Debug mode")
    log_level: str = Field(default="INFO", description="Log level")


@lru_cache()
def get_settings() -> Settings:
    return Settings()