from sqlalchemy import Column, Integer, String, Boolean, Enum, ForeignKey, Text, JSON, DateTime, Date, DECIMAL
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    job_uuid = Column(String(36), unique=True, index=True)
    source_id = Column(Integer, ForeignKey("source_registry.id"), nullable=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=True)

    title = Column(String(255), nullable=False)
    department = Column(String(255), nullable=True)
    organization = Column(String(255), nullable=True)
    job_category = Column(String(100), nullable=True)
    employment_type = Column(String(50), default="Full Time")
    work_mode = Column(String(50), default="On-site")

    country = Column(String(100), default="India")
    state = Column(String(100), nullable=True)
    city = Column(String(100), nullable=True)
    
    min_salary = Column(DECIMAL(12, 2), nullable=True)
    max_salary = Column(DECIMAL(12, 2), nullable=True)
    currency = Column(String(3), default="INR")
    
    description = Column(Text, nullable=True)
    vacancies = Column(Integer, nullable=True)
    last_date = Column(Date, nullable=True)
    apply_url = Column(String(1024), nullable=True)
    
    job_status = Column(String(50), default="Pending")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
