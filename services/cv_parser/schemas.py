from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class EducationItem(BaseModel):
    degree: Optional[str] = None
    field_of_study: Optional[str] = None
    institution: Optional[str] = None
    graduation_year: Optional[str] = None
    percentage_or_cgpa: Optional[str] = None

class ExperienceItem(BaseModel):
    job_title: Optional[str] = None
    company_name: Optional[str] = None
    location: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    is_current: bool = False
    responsibilities: List[str] = Field(default_factory=list)

class ParsedCVResponse(BaseModel):
    success: bool = True
    message: str = "CV parsed successfully"
    full_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    current_role: Optional[str] = None
    matched_role: Optional[str] = None
    total_experience_years: Optional[float] = 0.0
    skills: List[str] = Field(default_factory=list)
    education: List[EducationItem] = Field(default_factory=list)
    experience: List[ExperienceItem] = Field(default_factory=list)
    certifications: List[str] = Field(default_factory=list)
    languages: List[str] = Field(default_factory=list)
    summary: Optional[str] = None
    raw_text_preview: Optional[str] = None
    extracted_by: Optional[str] = "ai_parser"

class TextParseRequest(BaseModel):
    raw_text: str
    target_role: Optional[str] = None
