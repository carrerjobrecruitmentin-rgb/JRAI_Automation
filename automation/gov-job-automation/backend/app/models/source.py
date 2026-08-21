from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from app.core.database import Base

class SourceRegistry(Base):
    __tablename__ = "source_registry"

    id = Column(Integer, primary_key=True, index=True)
    source_name = Column(String(255), nullable=False)
    domain = Column(String(255), unique=True, index=True, nullable=False)
    website_url = Column(String(512), nullable=False)
    recruitment_url = Column(String(512), nullable=True)
    source_type = Column(String(50), default="Other")
    
    status = Column(String(50), default="Active")
    priority = Column(String(50), default="Medium")
    
    supports_rss = Column(Boolean, default=False)
    supports_sitemap = Column(Boolean, default=False)
    supports_api = Column(Boolean, default=False)
    
    last_crawl_at = Column(DateTime, nullable=True)
    next_crawl_at = Column(DateTime, nullable=True)
    health_score = Column(Integer, default=100)
    adapter_name = Column(String(100), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
