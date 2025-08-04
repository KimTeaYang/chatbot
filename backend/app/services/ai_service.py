"""
AI 서비스 - Gemini API 통신
"""
import os
from typing import Dict
from langchain_core.chat_history import BaseChatMessageHistory, InMemoryChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_google_genai import ChatGoogleGenerativeAI

from app.config.settings import settings
from app.core.exceptions import AIServiceException


class AIService:
    def __init__(self):
        self.api_key = settings.GOOGLE_API_KEY
        if not self.api_key:
            raise AIServiceException("GOOGLE_API_KEY 환경 변수를 설정해주세요.")

        # 시스템 프롬프트 설정
        self.system_prompt = """
        당신은 도움이 되고 친근한 AI 어시스턴트입니다. 
        사용자의 질문에 정확하고 유용한 답변을 제공하세요.
        한국어로 자연스럽게 대화하세요.
        """

        # Gemini 모델 초기화
        self.llm = ChatGoogleGenerativeAI(
            model=settings.AI_MODEL,
            google_api_key=self.api_key,
            temperature=settings.AI_TEMPERATURE,
            max_tokens=settings.AI_MAX_TOKENS
        )

        # 세션별 채팅 히스토리 저장소
        self.store: Dict[str, BaseChatMessageHistory] = {}

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

    def get_session_history(self, session_id: str) -> BaseChatMessageHistory:
        """세션 히스토리를 가져오거나 생성합니다."""
        if session_id not in self.store:
            self.store[session_id] = InMemoryChatMessageHistory()
        return self.store[session_id]

    async def generate_response(self, message: str, session_id: str) -> str:
        """AI 응답 생성"""
        try:
            # 비동기로 대화 실행
            response = await self.conversation.ainvoke(
                {"input": message},
                config={"configurable": {"session_id": session_id}}
            )

            # AIMessage 객체에서 content 추출
            bot_response = response.content if hasattr(response, 'content') else str(response)

            return bot_response

        except Exception as e:
            raise AIServiceException(f"AI 응답 생성 중 오류: {str(e)}")

    async def clear_session(self, session_id: str):
        """세션 히스토리 삭제"""
        if session_id in self.store:
            self.store[session_id].clear()
            del self.store[session_id]