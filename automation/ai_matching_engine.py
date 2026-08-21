"""
E:\automation\ai_matching_engine.py
AI Candidate-to-Job Matching Engine
Calculates intelligent match scores between job postings and candidates.
"""

import os
import json
import uuid
import re
import sys
import pymysql
from typing import Dict, List, Any, Optional

# Ensure UTF-8 output encoding on Windows console
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Database Configuration (supports local or remote Hostinger MySQL)
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_USER = os.getenv('DB_USER', 'root')
DB_PASS = os.getenv('DB_PASS', '')
DB_NAME = os.getenv('DB_NAME', 'job_recruitment_ai')

def get_db_connection():
    return pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASS,
        database=DB_NAME,
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=True
    )

def ensure_matches_table(cursor):
    """Ensures the job_candidate_matches table exists in MySQL."""
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS job_candidate_matches (
        id CHAR(36) PRIMARY KEY,
        job_id CHAR(36) NOT NULL,
        candidate_id CHAR(36) NOT NULL,
        overall_score INT NOT NULL,
        skills_score INT NOT NULL,
        experience_score INT NOT NULL,
        location_score INT NOT NULL,
        matched_skills JSON,
        missing_skills JSON,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        UNIQUE KEY unique_job_candidate (job_id, candidate_id)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """)

def parse_json_safely(data: Any, default=None) -> Any:
    if default is None:
        default = {}
    if not data:
        return default
    if isinstance(data, (dict, list)):
        return data
    try:
        return json.loads(data)
    except Exception:
        return default

def calculate_skills_score(job_skills: List[str], candidate_skills: List[str]) -> tuple[int, List[str], List[str]]:
    """Calculates skill overlap score, matched skills, and missing skills."""
    if not job_skills:
        return 80, candidate_skills[:5], []
    
    # Normalize strings for comparison
    clean_job = {re.sub(r'[^a-zA-Z0-9]', '', s.lower()): s for s in job_skills if s}
    clean_cand = {re.sub(r'[^a-zA-Z0-9]', '', s.lower()) for s in candidate_skills if s}
    
    matched = [clean_job[k] for k in clean_job if k in clean_cand]
    missing = [clean_job[k] for k in clean_job if k not in clean_cand]
    
    match_ratio = len(matched) / max(len(job_skills), 1)
    score = int(match_ratio * 100)
    return score, matched, missing

def calculate_experience_score(job_exp: Dict[str, Any], candidate_exp: Any) -> int:
    """Compares candidate experience in years against job required range."""
    min_req = float(job_exp.get('min', 0) or 0)
    max_req = float(job_exp.get('max', 10) or 10)
    
    cand_years = 0.0
    if isinstance(candidate_exp, list):
        cand_years = len(candidate_exp) * 1.5
    elif isinstance(candidate_exp, dict):
        cand_years = float(candidate_exp.get('total_years', 0) or 0)
    elif isinstance(candidate_exp, (int, float)):
        cand_years = float(candidate_exp)
    
    if cand_years >= min_req and cand_years <= max_req:
        return 100
    elif cand_years < min_req:
        deficit = min_req - cand_years
        return max(20, int(100 - (deficit * 20)))
    else:
        return 90

def calculate_location_score(job_loc: Dict[str, Any], work_mode: str, cand_addr: Dict[str, Any]) -> int:
    """Calculates location compatibility score."""
    if str(work_mode).lower() == 'remote':
        return 100
    
    job_city = str(job_loc.get('city', '')).strip().lower()
    job_state = str(job_loc.get('state', '')).strip().lower()
    
    cand_city = str(cand_addr.get('city', '')).strip().lower()
    cand_state = str(cand_addr.get('state', '')).strip().lower()
    
    if job_city and cand_city and job_city == cand_city:
        return 100
    elif job_state and cand_state and job_state == cand_state:
        return 75
    return 40

def run_ai_matching(job_id: str) -> Dict[str, Any]:
    """
    Main entry point for AI matching.
    Fetches the job by ID, computes match scores across all candidate profiles,
    and saves the top ranked matches into MySQL.
    """
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            ensure_matches_table(cursor)
            
            # 1. Fetch Job
            cursor.execute("SELECT * FROM jobs WHERE id = %s", (job_id,))
            job = cursor.fetchone()
            if not job:
                print(f"[WARN] Job {job_id} not found in database.")
                return {"success": False, "error": f"Job {job_id} not found"}
            
            # Parse Job details
            job_skills = parse_json_safely(job.get('skills'), [])
            if isinstance(job_skills, str):
                job_skills = [s.strip() for s in job_skills.split(',') if s.strip()]
                
            job_exp = parse_json_safely(job.get('experience_details'), {})
            job_loc = parse_json_safely(job.get('location_details'), {})
            work_mode = job.get('work_mode', 'On-site')
            
            # 2. Fetch Candidates
            cursor.execute("""
                SELECT cp.*, u.username, u.email 
                FROM candidate_profiles cp 
                JOIN users u ON cp.user_id = u.id 
                WHERE u.role = 'CANDIDATE'
            """)
            candidates = cursor.fetchall()
            print(f"[INFO] Analyzing {len(candidates)} candidates for Job '{job.get('title')}' (ID: {job_id})...")
            
            match_results = []
            for cand in candidates:
                cand_id = cand['user_id']
                cand_skills = parse_json_safely(cand.get('skills'), [])
                if isinstance(cand_skills, str):
                    cand_skills = [s.strip() for s in cand_skills.split(',') if s.strip()]
                
                cand_exp = parse_json_safely(cand.get('experience'), [])
                cand_addr = parse_json_safely(cand.get('address_info'), {})
                
                # Scores
                skills_score, matched_skills, missing_skills = calculate_skills_score(job_skills, cand_skills)
                exp_score = calculate_experience_score(job_exp, cand_exp)
                loc_score = calculate_location_score(job_loc, work_mode, cand_addr)
                
                # Composite Weighted Score: 45% Skills, 30% Experience, 25% Location
                overall_score = int((skills_score * 0.45) + (exp_score * 0.30) + (loc_score * 0.25))
                
                match_id = str(uuid.uuid4())
                cursor.execute("""
                    INSERT INTO job_candidate_matches 
                        (id, job_id, candidate_id, overall_score, skills_score, experience_score, location_score, matched_skills, missing_skills)
                    VALUES 
                        (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE 
                        overall_score = VALUES(overall_score),
                        skills_score = VALUES(skills_score),
                        experience_score = VALUES(experience_score),
                        location_score = VALUES(location_score),
                        matched_skills = VALUES(matched_skills),
                        missing_skills = VALUES(missing_skills)
                """, (
                    match_id, job_id, cand_id, overall_score, skills_score, exp_score, loc_score,
                    json.dumps(matched_skills), json.dumps(missing_skills)
                ))
                
                match_results.append({
                    "candidate_id": cand_id,
                    "candidate_name": cand.get('username'),
                    "overall_score": overall_score,
                    "matched_skills": matched_skills,
                    "missing_skills": missing_skills
                })
            
            # Sort top matches
            match_results.sort(key=lambda x: x['overall_score'], reverse=True)
            top_3 = match_results[:3]
            top_name = top_3[0]['candidate_name'] if top_3 else 'None'
            top_score = top_3[0]['overall_score'] if top_3 else 0
            print(f"[SUCCESS] Matching complete! Top candidate: {top_name} ({top_score}% match)")
            
            return {
                "success": True,
                "job_id": job_id,
                "total_matched": len(match_results),
                "top_matches": top_3
            }
            
    except Exception as e:
        print(f"[ERROR] Error during AI matching execution: {e}")
        return {"success": False, "error": str(e)}
    finally:
        conn.close()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        test_id = sys.argv[1]
        print(f"[INFO] Running AI Matching for specified Job ID: {test_id}")
        res = run_ai_matching(test_id)
        print(json.dumps(res, indent=2))
    else:
        print("[INFO] AI Matching Engine started in auto-polling mode...")
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT id, title FROM jobs ORDER BY created_at DESC LIMIT 5")
                jobs = cursor.fetchall()
                if not jobs:
                    print("[INFO] No jobs found in database. Seeding/Waiting for jobs...")
                for j in jobs:
                    print(f"\n[JOB MATCHING] Processing matches for: '{j['title']}' ({j['id']})")
                    run_ai_matching(j['id'])
        except Exception as e:
            print(f"[ERROR] Auto-polling encountered error: {e}")
        finally:
            conn.close()
