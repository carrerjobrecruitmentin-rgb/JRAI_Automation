import json
from typing import Dict, Any, Optional
from common.database import get_db_connection
from common.logger import log
from services.ai_matcher.engine import AIMatchingEngine

class JobMatchWebhookService:
    """
    Webhook dispatcher to calculate and update match scores in the MySQL database when a candidate applies or updates their profile.
    """

    @classmethod
    def process_application_match(cls, application_id: str, candidate_id: str, job_id: str) -> Dict[str, Any]:
        """
        Fetches candidate profile and job details from the DB, calculates the AI match score, and updates the application record.
        """
        conn = get_db_connection()
        if not conn:
            return {"success": False, "error": "Database unavailable"}

        try:
            with conn.cursor() as cursor:
                # 1. Fetch candidate skills & details
                cursor.execute(
                    "SELECT id, full_name, email, skills, experience_years, current_role, location FROM candidates WHERE id = %s LIMIT 1",
                    (candidate_id,)
                )
                cand = cursor.fetchone()

                # 2. Fetch job details
                cursor.execute(
                    "SELECT id, title, skills, requirements, min_experience, max_experience, work_mode, location_text FROM jobs WHERE id = %s LIMIT 1",
                    (job_id,)
                )
                job = cursor.fetchone()

                if not cand or not job:
                    return {"success": False, "error": "Candidate or Job not found"}

                # Normalize candidate skills
                cand_skills = []
                if cand.get("skills"):
                    if isinstance(cand["skills"], list):
                        cand_skills = cand["skills"]
                    elif isinstance(cand["skills"], str):
                        try:
                            cand_skills = json.loads(cand["skills"])
                        except Exception:
                            cand_skills = [s.strip() for s in cand["skills"].split(",") if s.strip()]
                cand["skills"] = cand_skills

                # Normalize job skills
                job_skills = []
                if job.get("skills"):
                    if isinstance(job["skills"], list):
                        job_skills = job["skills"]
                    elif isinstance(job["skills"], str):
                        try:
                            job_skills = json.loads(job["skills"])
                        except Exception:
                            job_skills = [s.strip() for s in job["skills"].split(",") if s.strip()]
                job["skills"] = job_skills

                # Compute Score
                match_result = AIMatchingEngine.calculate_match(cand, job)
                score = match_result["score"]

                # 3. Update application table
                cursor.execute(
                    "UPDATE applications SET match_score = %s WHERE id = %s",
                    (score, application_id)
                )

                log.info(f"Updated Application #{application_id} with Match Score: {score}%")
                return {
                    "success": True,
                    "application_id": application_id,
                    "match_score": score,
                    "details": match_result
                }
        except Exception as e:
            log.error(f"Error processing application match webhook: {e}")
            return {"success": False, "error": str(e)}
        finally:
            conn.close()
