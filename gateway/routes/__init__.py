"""
API Gateway Route Handlers.
"""
from .cv_parser import router as cv_parser_router
from .ai_matcher import router as ai_matcher_router
from .crawler import router as crawler_router

__all__ = ["cv_parser_router", "ai_matcher_router", "crawler_router"]
