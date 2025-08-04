import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "app:app",  # app/__init__.py의 app 인스턴스 참조
        host="0.0.0.0",
        port=8000,
        reload=True,  # 개발 환경에서 자동 리로드
        log_level="info"
    )
