import asyncio
import json
import os
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from langchain_core.chat_history import BaseChatMessageHistory, InMemoryChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel

# 라우터 생성
router = APIRouter(tags=["chat"])


# 요청/응답 모델 정의
class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = "default"


class ChatResponse(BaseModel):
    response: str
    session_id: str
    timestamp: str


class ConversationHistory(BaseModel):
    messages: List[dict]
    session_id: str


# 세션별 챗봇 인스턴스 저장
chatbot_sessions = {}


class GeminiChatbotAPI:
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.api_key = os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY 환경 변수를 설정해주세요.")

        # 시스템 프롬프트 설정
        self.system_prompt = """
        당신은 도움이 되고 친근한 AI 어시스턴트입니다. 
        사용자의 질문에 정확하고 유용한 답변을 제공하세요.
        한국어로 자연스럽게 대화하세요.
        """

        # Gemini 모델 초기화
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash-exp",
            google_api_key=self.api_key,
            temperature=0.7,
            max_tokens=1000
        )

        # 채팅 히스토리 저장소
        self.store = {}

        # 프롬프트 템플릿 생성
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", self.system_prompt),
            MessagesPlaceholder(variable_name="history"),
            ("human", "{input}")
        ])

        # 체인 생성
        self.chain = self.prompt | self.llm

        # 메시지 히스토리와 함께 실행 가능한 체인
        self.conversation = RunnableWithMessageHistory(
            self.chain,
            self.get_session_history,
            input_messages_key="input",
            history_messages_key="history"
        )

        # 대화 기록 저장을 위한 리스트
        self.chat_history = []

    def get_session_history(self, session_id: str = None) -> BaseChatMessageHistory:
        """세션 히스토리를 가져오거나 생성합니다."""
        if session_id is None:
            session_id = self.session_id
        if session_id not in self.store:
            self.store[session_id] = InMemoryChatMessageHistory()
        return self.store[session_id]

    async def chat(self, user_input: str):
        """비동기 채팅 메서드"""
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # 비동기로 대화 실행
            response = await self.conversation.ainvoke(
                {"input": user_input},
                config={"configurable": {"session_id": self.session_id}}
            )

            # AIMessage 객체에서 content 추출
            bot_response = response.content if hasattr(response, 'content') else str(response)

            # 대화 기록에 저장
            self.chat_history.append({
                "timestamp": timestamp,
                "user": user_input,
                "bot": bot_response,
                "type": "message"
            })

            return bot_response
        except Exception as e:
            error_msg = f"챗봇 오류: {str(e)}"
            print(f"Debug error: {e}")
            raise HTTPException(status_code=500, detail=error_msg)

    def get_history(self):
        """대화 기록 반환"""
        return self.chat_history

    def clear_history(self):
        """대화 기록 초기화"""
        if self.session_id in self.store:
            self.store[self.session_id].clear()
        self.chat_history.clear()


def get_chatbot(session_id: str) -> GeminiChatbotAPI:
    """세션별 챗봇 인스턴스 반환"""
    if session_id not in chatbot_sessions:
        chatbot_sessions[session_id] = GeminiChatbotAPI(session_id)
    return chatbot_sessions[session_id]


# API 엔드포인트들
@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """채팅 메시지 처리"""
    try:
        chatbot = get_chatbot(request.session_id)
        response = await chatbot.chat(request.message)

        return ChatResponse(
            response=response,
            session_id=request.session_id,
            timestamp=datetime.now().isoformat()
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail=f"서버 오류: {str(e)}")


@router.get("/chat/history/{session_id}")
async def get_chat_history(session_id: str):
    """대화 기록 조회"""
    try:
        chatbot = get_chatbot(session_id)
        history = chatbot.get_history()

        return ConversationHistory(
            messages=history,
            session_id=session_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/chat/history/{session_id}")
async def clear_chat_history(session_id: str):
    """대화 기록 삭제"""
    try:
        chatbot = get_chatbot(session_id)
        chatbot.clear_history()

        return {"message": f"세션 {session_id}의 대화 기록이 삭제되었습니다."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sessions")
async def get_active_sessions():
    """활성 세션 목록 조회"""
    return {"active_sessions": list(chatbot_sessions.keys())}


@router.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    """스트리밍 채팅 응답"""

    async def generate_stream():
        try:
            chatbot = get_chatbot(request.session_id)
            response = await chatbot.chat(request.message)

            # 스트리밍 효과를 위해 글자별로 전송
            for char in response:
                yield f"data: {json.dumps({'char': char, 'type': 'char'})}\n\n"
                await asyncio.sleep(0.02)

            yield f"data: {json.dumps({'type': 'end', 'session_id': request.session_id})}\n\n"

        except Exception as e:
            yield f"data: {json.dumps({'error': str(e), 'type': 'error'})}\n\n"

    return StreamingResponse(
        generate_stream(),
        media_type="text/plain",
        headers={"Cache-Control": "no-cache"}
    )