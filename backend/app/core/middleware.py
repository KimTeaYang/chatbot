"""
커스텀 미들웨어 설정
"""
import time
import logging
from fastapi import FastAPI, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Callable

logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """요청/응답 로깅 미들웨어"""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()

        # 요청 로깅
        logger.info(f"Request: {request.method} {request.url}")

        try:
            response = await call_next(request)
            process_time = time.time() - start_time

            # 응답 로깅
            logger.info(
                f"Response: {response.status_code} | "
                f"Time: {process_time:.4f}s | "
                f"Path: {request.url.path}"
            )

            # 응답 헤더에 처리 시간 추가
            response.headers["X-Process-Time"] = str(process_time)

            return response

        except Exception as e:
            process_time = time.time() - start_time
            logger.error(f"Request failed: {str(e)} | Time: {process_time:.4f}s")
            raise


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """보안 헤더 추가 미들웨어"""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)

        # 보안 헤더 추가
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        return response


def setup_middleware(app: FastAPI):
    """미들웨어 설정"""

    # 로깅 미들웨어 추가
    app.add_middleware(LoggingMiddleware)

    # 보안 헤더 미들웨어 추가
    app.add_middleware(SecurityHeadersMiddleware)

    logger.info("Middleware setup completed")