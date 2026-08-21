from fastapi import APIRouter, HTTPException, Body
from typing import Dict, Any, List
from services.ai_matcher.engine import AIMatchingEngine
from services.ai_matcher.webhook import JobMatchWebhookService
from common.logger import log

router = APIRouter(prefix="/matcher", tags=["AI Job Matching & Webhooks Microservice"])

@router.post("/match-score", summary="Compute Compatibility Score (Candidate vs Job)")
async def calculate_match_score(
    candidate: Dict[str, Any] = Body(..., example={"skills": ["Python", "FastAPI"], "experience_years": 3, "current_role": "Backend Engineer", "location": "Bangalore"}),
    job: Dict[str, Any] = Body(..., example={"title": "Senior Python Developer", "skills": ["Python", "FastAPI", "Docker"], "min_experience": 2, "work_mode": "Remote"})
):
    """
    Computes compatibility score between a candidate profile and a job posting.
    """
    try:
        return AIMatchingEngine.calculate_match(candidate, job)
    except Exception as e:
        log.error(f"Match calculation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/webhook/application-match", summary="Webhook Trigger: Update Application Match Score in DB")
async def trigger_application_match_webhook(
    payload: Dict[str, Any] = Body(..., example={"application_id": "app_123", "candidate_id": "cand_456", "job_id": "job_789"})
):
    """
    Processes real-time application match webhooks and updates `match_score` directly in MySQL.
    """
    app_id = payload.get("application_id")
    cand_id = payload.get("candidate_id")
    job_id = payload.get("job_id")

    if not app_id or not cand_id or not job_id:
        raise HTTPException(status_code=400, detail="Missing application_id, candidate_id, or job_id")

    result = JobMatchWebhookService.process_application_match(app_id, cand_id, job_id)
    if not result.get("success"):
        raise HTTPException(status_code=422, detail=result.get("error", "Failed to process match"))

    return result
