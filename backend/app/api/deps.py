"""
API 의존성 주입
"""
from app.services.chat_service import ChatService

# 싱글톤 인스턴스들
_chat_service: ChatService = None

def get_chat_service() -> ChatService:
    """채팅 서비스 의존성"""
    global _chat_service
    if _chat_service is None:
        _chat_service = ChatService()
    return _chat_service