from fastapi import APIRouter, HTTPException, BackgroundTasks, Body
from typing import Dict, Any, Optional
from services.gov_crawler.extractor import GovJobExtractor
from services.gov_crawler.publisher import GovJobPublisher
from common.logger import log

router = APIRouter(prefix="/crawler", tags=["Government Job Scraper & Crawler Microservice"])

@router.post("/extract-notification", summary="Extract Structured Gov Job from Raw Text")
async def extract_gov_notification(payload: Dict[str, Any] = Body(..., example={"raw_text": "UPSC Civil Services Examination 2026 notification..."})):
    """
    Normalizes messy government notification text into structured job fields.
    """
    raw_text = payload.get("raw_text", "")
    if not raw_text or len(raw_text.strip()) < 20:
        raise HTTPException(status_code=400, detail="Raw text is too short")

    extracted = GovJobExtractor.extract_from_text(raw_text)
    if not extracted:
        raise HTTPException(status_code=422, detail="Failed to extract structured government job details")

    return {"success": True, "data": extracted}

@router.post("/publish-notification", summary="Extract and Publish Gov Job to MySQL Database")
async def publish_gov_notification(
    background_tasks: BackgroundTasks,
    payload: Dict[str, Any] = Body(...)
):
    """
    Extracts structured data from notification and publishes to live jobs table.
    """
    raw_text = payload.get("raw_text")
    direct_data = payload.get("job_data")

    if direct_data:
        success = GovJobPublisher.publish_job(direct_data)
        return {"success": success, "message": "Job published" if success else "Failed to publish"}

    if raw_text:
        extracted = GovJobExtractor.extract_from_text(raw_text)
        if not extracted:
            raise HTTPException(status_code=422, detail="Failed to extract job details")
        success = GovJobPublisher.publish_job(extracted)
        return {"success": success, "data": extracted}

    raise HTTPException(status_code=400, detail="Must provide either raw_text or job_data")
