"""
채팅 서비스 - 비즈니스 로직
"""
import asyncio
import json
from datetime import datetime
from typing import AsyncGenerator, Dict, List

from app.schemas.chat import ChatResponse, ConversationHistory
from app.services.ai_service import AIService


class ChatService:
    def __init__(self):
        self.ai_service = AIService()
        self.sessions: Dict[str, List[Dict]] = {}

    async def process_message(self, message: str, session_id: str) -> ChatResponse:
        """메시지 처리"""
        try:
            # AI 응답 생성
            ai_response = await self.ai_service.generate_response(
                message=message,
                session_id=session_id
            )

            # 세션에 대화 저장
            self._save_to_session(session_id, message, ai_response)

            return ChatResponse(
                response=ai_response,
                session_id=session_id,
                timestamp=datetime.now().isoformat()
            )

        except Exception as e:
            raise Exception(f"메시지 처리 중 오류: {str(e)}")

    async def get_history(self, session_id: str) -> ConversationHistory:
        """대화 기록 조회"""
        messages = self.sessions.get(session_id, [])
        return ConversationHistory(
            messages=messages,
            session_id=session_id
        )

    async def clear_history(self, session_id: str):
        """대화 기록 삭제"""
        if session_id in self.sessions:
            del self.sessions[session_id]
        await self.ai_service.clear_session(session_id)

    async def stream_message(self, message: str, session_id: str) -> AsyncGenerator[str, None]:
        """스트리밍 메시지 처리"""
        try:
            response = await self.process_message(message, session_id)

            # 스트리밍 효과
            for char in response.response:
                yield f"data: {json.dumps({'char': char, 'type': 'char'})}\n\n"
                await asyncio.sleep(0.02)

            yield f"data: {json.dumps({'type': 'end', 'session_id': session_id})}\n\n"

        except Exception as e:
            yield f"data: {json.dumps({'error': str(e), 'type': 'error'})}\n\n"

    async def get_active_sessions(self) -> List[str]:
        """활성 세션 목록"""
        return list(self.sessions.keys())

    def _save_to_session(self, session_id: str, user_message: str, bot_response: str):
        """세션에 대화 저장"""
        if session_id not in self.sessions:
            self.sessions[session_id] = []

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.sessions[session_id].append({
            "timestamp": timestamp,
            "user": user_message,
            "bot": bot_response,
            "type": "message"
        })