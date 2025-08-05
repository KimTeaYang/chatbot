"""
애플리케이션 설정
"""
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    # 기본 설정
    PROJECT_NAME: str = "Gemini Chatbot API"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "AI 챗봇 API 서비스"

    # 서버 설정
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"

    # API 설정
    API_V1_STR: str = "/api/v1"

    # CORS 설정
    ALLOWED_HOSTS: List[str] = ["*"]

    # AI 설정
    GOOGLE_API_KEY: str = Field(..., env="GOOGLE_API_KEY")
    AI_MODEL: str = "gemini-2.0-flash-exp"
    AI_TEMPERATURE: float = 0.7
    AI_MAX_TOKENS: int = 1000

    # 데이터베이스 설정 (향후 사용)
    DATABASE_URL: Optional[str] = Field(None, env="DATABASE_URL")

    # Redis 설정 (향후 세션 관리용)
    REDIS_URL: Optional[str] = Field(None, env="REDIS_URL")

    # 보안 설정
    SECRET_KEY: str = Field("your-secret-key-here", env="SECRET_KEY")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    #LangFuse
    LANGFUSE_PUBLIC_KEY: str = Field(..., env="LANGFUSE_PUBLIC_KEY")
    LANGFUSE_SECRET_KEY: str = Field(..., env="LANGFUSE_SECRET_KEY")
    LANGFUSE_HOST: str = Field(..., env="LANGFUSE_HOST")

    # Redis 설정
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str = ""  # 필요한 경우 설정

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()