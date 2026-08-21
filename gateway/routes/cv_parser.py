from fastapi import APIRouter, UploadFile, File, Form, HTTPException, status
from typing import Optional
from services.cv_parser.parser import CVParserService
from services.cv_parser.schemas import ParsedCVResponse, TextParseRequest
from common.logger import log

router = APIRouter(prefix="/cv-parser", tags=["CV & Resume Parser Microservice"])

@router.post("/upload", response_model=ParsedCVResponse, summary="Parse Resume File (PDF / DOCX / Image)")
async def parse_resume_upload(
    file: UploadFile = File(...),
    target_role: Optional[str] = Form(None)
):
    """
    Accepts a resume file (PDF, DOCX, PNG, JPG, TXT), extracts text via OCR/Parsers, and returns a structured candidate profile.
    """
    try:
        file_bytes = await file.read()
        if len(file_bytes) == 0:
            raise HTTPException(status_code=400, detail="Uploaded file is empty")

        log.info(f"Received CV upload: {file.filename} ({len(file_bytes)} bytes)")
        raw_text = CVParserService.extract_text_from_bytes(file_bytes, file.filename)

        if not raw_text.strip():
            raise HTTPException(status_code=422, detail="Unable to extract readable text from document. Ensure it is not password-protected.")

        result = CVParserService.parse_with_ai(raw_text, target_role=target_role)
        return result

    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Error parsing resume upload: {e}")
        raise HTTPException(status_code=500, detail=f"Internal Parser Error: {str(e)}")

@router.post("/parse-text", response_model=ParsedCVResponse, summary="Parse Raw Resume Text")
async def parse_resume_text(payload: TextParseRequest):
    """
    Accepts raw resume text and parses it into structured candidate JSON using AI.
    """
    try:
        return CVParserService.parse_with_ai(payload.raw_text, target_role=payload.target_role)
    except Exception as e:
        log.error(f"Error parsing raw text: {e}")
        raise HTTPException(status_code=500, detail=str(e))
