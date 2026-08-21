# E:\automation\ai_match_webhook.py
from fastapi import FastAPI, Header, HTTPException, BackgroundTasks
from pydantic import BaseModel
import uvicorn
import time
import os
import sys

# Import our AI Matching Engine
from ai_matching_engine import run_ai_matching

app = FastAPI(title="JobRecruitmentAI Background AI Worker")
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security: API Key to authenticate requests from Hostinger PHP Webhook
API_KEY = os.getenv("AI_WORKER_API_KEY", "your_secret_api_key_123")

class JobPayload(BaseModel):
    job_id: str

def process_ai_matching(job_id: str):
    """
    Executes in background without blocking the PHP response.
    """
    print(f"[{time.strftime('%X')}] 🟢 WEBHOOK TRIGGERED: Starting AI matching for Job ID '{job_id}'...")
    result = run_ai_matching(job_id)
    if result.get("success"):
        print(f"[{time.strftime('%X')}] ✅ AI matching finished successfully for Job '{job_id}'. Database updated.")
    else:
        print(f"[{time.strftime('%X')}] ⚠️ AI matching completed with message: {result.get('error')}")

@app.post("/api/match_job")
async def trigger_match(payload: JobPayload, background_tasks: BackgroundTasks, x_api_key: str = Header(None)):
    if x_api_key != API_KEY:
        print(f"[{time.strftime('%X')}] 🔴 Unauthorized webhook attempt blocked.")
        raise HTTPException(status_code=401, detail="Unauthorized API Key")
    
    # Delegate to FastAPI background task
    background_tasks.add_task(process_ai_matching, payload.job_id)
    
    return {
        "status": "success",
        "message": f"Job {payload.job_id} received. Matching engine processing in background."
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "E:\\ Drive AI Matching Worker"}

if __name__ == "__main__":
    print("🚀 E:\\ Python AI Worker Webhook Server Started on Port 8005")
    uvicorn.run(app, host="127.0.0.1", port=8005)
