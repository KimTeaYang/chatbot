"""
커스텀 예외 및 예외 핸들러 설정
"""
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import logging

logger = logging.getLogger(__name__)


class ChatbotException(Exception):
    """챗봇 관련 커스텀 예외"""

    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class AIServiceException(ChatbotException):
    """AI 서비스 관련 예외"""

    def __init__(self, message: str = "AI 서비스 오류가 발생했습니다"):
        super().__init__(message, status_code=503)


class SessionNotFoundException(ChatbotException):
    """세션을 찾을 수 없을 때 예외"""

    def __init__(self, session_id: str):
        message = f"세션 '{session_id}'를 찾을 수 없습니다"
        super().__init__(message, status_code=404)


def setup_exception_handlers(app: FastAPI):
    """예외 핸들러 설정"""

    @app.exception_handler(ChatbotException)
    async def chatbot_exception_handler(request: Request, exc: ChatbotException):
        logger.error(f"Chatbot error: {exc.message}")
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": exc.message,
                "type": "chatbot_error",
                "path": str(request.url)
            }
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": exc.detail,
                "type": "http_error",
                "path": str(request.url)
            }
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "error": "입력 데이터 검증에 실패했습니다",
                "details": exc.errors(),
                "type": "validation_error",
                "path": str(request.url)
            }
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        logger.error(f"Unexpected error: {str(exc)}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": "서버 내부 오류가 발생했습니다",
                "type": "internal_error",
                "path": str(request.url)
            }
        )