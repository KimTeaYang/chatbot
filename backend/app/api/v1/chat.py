"""
채팅 관련 API 엔드포인트
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse

from app.schemas.chat import ChatRequest, ChatResponse, ConversationHistory
from app.services.chat_service import ChatService
from app.api.deps import get_chat_service

router = APIRouter()

@router.post("/", response_model=ChatResponse)
async def chat_message(
    request: ChatRequest,
    chat_service: ChatService = Depends(get_chat_service)
):
    """채팅 메시지 처리"""
    try:
        response = await chat_service.process_message(
            message=request.message,
            session_id=request.session_id
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history/{session_id}", response_model=ConversationHistory)
async def get_chat_history(
    session_id: str,
    chat_service: ChatService = Depends(get_chat_service)
):
    """대화 기록 조회"""
    try:
        history = await chat_service.get_history(session_id)
        return history
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/history/{session_id}")
async def clear_chat_history(
    session_id: str,
    chat_service: ChatService = Depends(get_chat_service)
):
    """대화 기록 삭제"""
    try:
        await chat_service.clear_history(session_id)
        return {"message": f"세션 {session_id}의 대화 기록이 삭제되었습니다."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/stream")
async def chat_stream(
    request: ChatRequest,
    chat_service: ChatService = Depends(get_chat_service)
):
    """스트리밍 채팅 응답"""
    return StreamingResponse(
        chat_service.stream_message(request.message, request.session_id),
        media_type="text/plain"
    )

@router.get("/sessions")
async def get_active_sessions(
    chat_service: ChatService = Depends(get_chat_service)
):
    """활성 세션 목록"""
    sessions = await chat_service.get_active_sessions()
    return {"active_sessions": sessions}