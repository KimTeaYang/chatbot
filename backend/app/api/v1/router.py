"""
API v1 라우터 통합
"""
from fastapi import APIRouter

from app.api.v1 import chat

api_router = APIRouter()

# 각 도메인별 라우터 등록
api_router.include_router(
    chat.router,
    prefix="/chat",
    tags=["채팅"]
)

# 향후 추가될 라우터들
# api_router.include_router(admin.router, prefix="/admin", tags=["관리"])