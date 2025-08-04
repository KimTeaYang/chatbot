from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

# 앱 인스턴스를 먼저 생성
app = FastAPI(
    title="Gemini Chatbot API",
    version="1.0.0",
    description="AI 챗봇 API 서비스",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 글로벌 엔드포인트
@app.get("/")
async def root():
    return {
        "message": "Gemini Chatbot API",
        "status": "running",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "chatbot-api"
    }

# 지연 임포트로 라우터 등록 (✅ 순환참조 방지)
def setup_routes():
    from .api.chat_api import router as chat_router
    app.include_router(chat_router, prefix="/api/v1")

# 라우터 설정 실행
setup_routes()
