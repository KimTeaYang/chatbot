"""
FastAPI 애플리케이션 생성 및 설정
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from .api.v1.router import api_router
from app.config.settings import settings
from app.core.exceptions import setup_exception_handlers
from app.core.middleware import setup_middleware


def create_application() -> FastAPI:
    """FastAPI 애플리케이션 생성"""

    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        description=settings.DESCRIPTION,
        openapi_url=f"{settings.API_V1_STR}/openapi.json" if settings.DEBUG else None,
        docs_url="/docs" if settings.DEBUG else None,
        redoc_url="/redoc" if settings.DEBUG else None,
    )

    # CORS 설정
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_HOSTS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Trusted Host 설정
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=settings.ALLOWED_HOSTS
    )

    # 커스텀 미들웨어 설정
    setup_middleware(app)

    # 예외 핸들러 설정
    setup_exception_handlers(app)

    # 라우터 등록
    app.include_router(api_router, prefix=settings.API_V1_STR)

    # 헬스체크 엔드포인트
    @app.get("/")
    async def root():
        return {
            "message": f"{settings.PROJECT_NAME} API",
            "version": settings.VERSION,
            "status": "running"
        }

    @app.get("/health")
    async def health_check():
        return {
            "status": "healthy",
            "service": settings.PROJECT_NAME.lower().replace(" ", "-")
        }

    return app


# 앱 인스턴스 생성
app = create_application()