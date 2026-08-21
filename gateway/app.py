import time
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from common.config import settings
from common.logger import log
from gateway.routes.cv_parser import router as cv_parser_router
from gateway.routes.ai_matcher import router as ai_matcher_router
from gateway.routes.crawler import router as crawler_router

# Initialize Gateway FastAPI Application
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Unified API Gateway and Microservices Engine for JobRecruitmentAI (CV Parsing, AI Matching, Scrapers)",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 1. CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. Timing & Logging Middleware
@app.middleware("http")
async def add_process_time_and_log(request: Request, call_next):
    start_time = time.time()
    try:
        response = await call_next(request)
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = f"{process_time:.4f}s"
        log.info(f"{request.method} {request.url.path} -> {response.status_code} ({process_time * 1000:.1f}ms)")
        return response
    except Exception as e:
        process_time = time.time() - start_time
        log.error(f"Unhandled Exception on {request.method} {request.url.path}: {e}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": "Internal Gateway Server Error", "detail": str(e)}
        )

# 3. Mount Microservices Routers
app.include_router(cv_parser_router, prefix=settings.API_V1_STR)
app.include_router(ai_matcher_router, prefix=settings.API_V1_STR)
app.include_router(crawler_router, prefix=settings.API_V1_STR)

# 4. Root & Health Check Endpoints
@app.get("/", tags=["System & Health"])
async def root_status():
    return {
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "status": "online",
        "environment": settings.ENVIRONMENT,
        "docs": "/docs",
        "endpoints": {
            "cv_parser": f"{settings.API_V1_STR}/cv-parser/upload",
            "ai_matcher": f"{settings.API_V1_STR}/matcher/match-score",
            "crawler": f"{settings.API_V1_STR}/crawler/extract-notification"
        }
    }

@app.get("/health", tags=["System & Health"])
async def health_check():
    """
    Standard Render / Cloudflare liveness and readiness probe.
    """
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "services": {
            "gateway": "running",
            "cv_parser": "ready",
            "ai_matcher": "ready",
            "gov_crawler": "ready"
        }
    }
