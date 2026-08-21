import uvicorn
from common.config import settings
from common.logger import log

def main():
    log.info(f"Starting {settings.PROJECT_NAME} v{settings.VERSION} on {settings.HOST}:{settings.PORT}")
    uvicorn.run(
        "gateway.app:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.ENVIRONMENT == "development",
        access_log=True
    )

if __name__ == "__main__":
    main()
