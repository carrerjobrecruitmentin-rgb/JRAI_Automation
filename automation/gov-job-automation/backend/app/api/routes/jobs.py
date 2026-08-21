from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.api import deps
from app.models.job import Job

router = APIRouter()

@router.get("/")
def get_jobs(db: Session = Depends(deps.get_db), skip: int = 0, limit: int = 100):
    jobs = db.query(Job).offset(skip).limit(limit).all()
    return jobs

@router.get("/{job_id}")
def get_job(job_id: int, db: Session = Depends(deps.get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job

@router.post("/")
def create_job(job_data: dict, db: Session = Depends(deps.get_db), current_user: str = Depends(deps.get_current_user)):
    # Note: In production, use Pydantic models (schemas) instead of dict
    db_job = Job(**job_data)
    db.add(db_job)
    db.commit()
    db.refresh(db_job)
    return db_job
