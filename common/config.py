import os
from typing import List
from pydantic_settings import BaseSettings
from pydantic import Field
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    PROJECT_NAME: str = "JobRecruitmentAI Automation Gateway"
    VERSION: str = "2.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Server & Port (Supports Render's $PORT environment variable)
    PORT: int = Field(default_factory=lambda: int(os.getenv("PORT", 8000)))
    HOST: str = "0.0.0.0"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "production")
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "jrai_super_secret_automation_key_2026")
    API_GATEWAY_KEY: str = os.getenv("API_GATEWAY_KEY", "jrai_gateway_default_key")
    
    # CORS Origins
    CORS_ORIGINS: List[str] = [
        "https://jobrecruitment.ai",
        "https://www.jobrecruitment.ai",
        "https://cv-parser.jobrecruitment.ai",
        "https://ai-matcher.jobrecruitment.ai",
        "https://admin.jobrecruitment.ai",
        "http://localhost:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "*"
    ]
    
    # Database Configuration (Hostinger / Local MySQL)
    DB_HOST: str = os.getenv("DB_HOST", "127.0.0.1")
    DB_USER: str = os.getenv("DB_USER", "u390470426_jobret_ai")
    DB_PASS: str = os.getenv("DB_PASS", "D/>bmEUu8b")
    DB_NAME: str = os.getenv("DB_NAME", "u390470426_jobret_ai")
    DB_PORT: int = Field(default_factory=lambda: int(os.getenv("DB_PORT", 3306)))
    
    # AI API Keys
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    
    # AI Models
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    GROQ_MODEL: str = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
    
    # OCR Settings
    TESSERACT_CMD: str = os.getenv("TESSERACT_CMD", "tesseract")
    
    class Config:
        case_sensitive = True
        extra = "allow"

settings = Settings()
