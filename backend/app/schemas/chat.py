"""
채팅 관련 Pydantic 스키마
"""
from typing import List, Optional
from pydantic import BaseModel, Field

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=1000, description="사용자 메시지")
    session_id: Optional[str] = Field("default", description="세션 ID")

class ChatResponse(BaseModel):
    response: str = Field(..., description="AI 응답")
    session_id: str = Field(..., description="세션 ID")
    timestamp: str = Field(..., description="응답 시간")

class ConversationHistory(BaseModel):
    messages: List[dict] = Field(..., description="대화 기록")
    session_id: str = Field(..., description="세션 ID")

class SessionInfo(BaseModel):
    session_id: str
    message_count: int
    last_activity: str